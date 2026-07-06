import structlog
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.mcp_servers.firestore_mcp import firestore_mcp
from app.mcp_servers.maps_mcp import maps_mcp

try:
    from google.adk.agents import Agent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None

logger = structlog.get_logger(__name__)

async def find_best_shelter(lat: float, lng: float, victim_count: int = 1) -> dict:
    """Find the closest open shelter with enough capacity."""
    # Query open shelters
    shelter_query = await firestore_mcp.query_collection(
        "shelters", 
        filters=[{"field": "status", "op": "==", "value": "open"}]
    )
    shelters = shelter_query.get("data", [])
    
    if not shelters:
        # Check all shelters as fallback
        fallback = await firestore_mcp.query_collection("shelters")
        shelters = fallback.get("data", [])
        
    scored_shelters = []
    for s in shelters:
        total_cap = s.get("total_capacity", 100)
        curr_occ = s.get("current_occupancy", 0)
        avail = max(0, total_cap - curr_occ)
        
        # Calculate distance
        s_lat = s.get("location", {}).get("lat") or s.get("lat")
        s_lng = s.get("location", {}).get("lng") or s.get("lng")
        
        dist_res = await maps_mcp.calculate_distance(lat, lng, s_lat, s_lng)
        dist_km = dist_res.get("data", {}).get("distance_km", 999.0)
        
        # Score shelter based on distance (weight 70%) and availability (weight 30%)
        # Lower score is better
        capacity_score = 0.0 if avail >= victim_count else 50.0
        score = (dist_km * 0.7) + (capacity_score * 0.3)
        
        scored_shelters.append({
            **s,
            "distance_km": dist_km,
            "available_capacity": avail,
            "score": score
        })
        
    scored_shelters.sort(key=lambda x: x["score"])
    
    best = scored_shelters[0] if scored_shelters else None
    alternatives = scored_shelters[1:3] if len(scored_shelters) > 1 else []
    
    return {
        "recommended_shelter": best,
        "alternatives": alternatives
    }

async def find_best_hospital(lat: float, lng: float, severity: str = "medium") -> dict:
    """Identify the optimal hospital based on distance and available beds."""
    hosp_query = await firestore_mcp.query_collection("hospitals")
    hospitals = hosp_query.get("data", [])
    
    scored_hospitals = []
    for h in hospitals:
        avail_beds = h.get("available_beds", 0)
        
        # Calculate distance
        h_lat = h.get("location", {}).get("lat") or h.get("lat")
        h_lng = h.get("location", {}).get("lng") or h.get("lng")
        
        dist_res = await maps_mcp.calculate_distance(lat, lng, h_lat, h_lng)
        dist_km = dist_res.get("data", {}).get("distance_km", 999.0)
        
        # Priority logic: critical severity requires hospital with available trauma ICU capacity
        if severity == "critical":
            # Penalize hospitals with no beds heavily
            bed_score = 0.0 if avail_beds > 0 else 100.0
            score = (dist_km * 0.5) + (bed_score * 0.5)
        else:
            bed_score = 0.0 if avail_beds > 5 else 20.0
            score = (dist_km * 0.8) + (bed_score * 0.2)
            
        scored_hospitals.append({
            **h,
            "distance_km": dist_km,
            "score": score
        })
        
    scored_hospitals.sort(key=lambda x: x["score"])
    best = scored_hospitals[0] if scored_hospitals else None
    return {"recommended_hospital": best}

async def calculate_resource_needs(incident_type: str, severity: str, estimated_victims: int = 50) -> dict:
    """Perform a rules-based estimation of food, water, medical kits, and blankets required."""
    needs = {}
    
    # Base requirements per victim
    meals_per_day = 3
    water_liters_per_day = 3
    
    if incident_type == "flood":
        needs["food"] = estimated_victims * meals_per_day
        needs["water"] = estimated_victims * water_liters_per_day
        needs["blankets"] = estimated_victims
        needs["medical_kits"] = max(5, estimated_victims // 10)
    elif incident_type == "fire":
        needs["medical_kits"] = max(10, estimated_victims // 5)
        needs["water"] = estimated_victims * water_liters_per_day * 1.5
        needs["blankets"] = estimated_victims // 2
        needs["food"] = estimated_victims * meals_per_day // 2
    else:  # earthquake, cyclone, etc
        needs["food"] = estimated_victims * meals_per_day * 2
        needs["water"] = estimated_victims * water_liters_per_day * 2
        needs["blankets"] = estimated_victims
        needs["medical_kits"] = max(15, estimated_victims // 5)
        
    # Scale based on severity
    scale = 1.0
    if severity == "critical":
        scale = 2.0
    elif severity == "high":
        scale = 1.5
        
    scaled_needs = {k: int(v * scale) for k, v in needs.items()}
    return scaled_needs

async def allocate_resources(incident_id: str, needs: dict) -> dict:
    """Reserve required supplies from inventory and record updates in the database."""
    inventory_query = await firestore_mcp.query_collection("resources")
    inventory = inventory_query.get("data", [])
    
    allocated = []
    shortfalls = []
    
    for need_type, need_qty in needs.items():
        # Find matching inventory items
        matching = [item for item in inventory if item.get("type") == need_type]
        if not matching:
            shortfalls.append({"type": need_type, "requested": need_qty, "available": 0})
            continue
            
        allocated_qty = 0
        for item in matching:
            if allocated_qty >= need_qty:
                break
                
            avail_qty = item.get("quantity", 0)
            take_qty = min(avail_qty, need_qty - allocated_qty)
            
            if take_qty > 0:
                # Update item quantity in DB
                new_qty = avail_qty - take_qty
                await firestore_mcp.update_document("resources", item["id"], {
                    "quantity": new_qty,
                    "allocated_to": incident_id
                })
                allocated_qty += take_qty
                allocated.append({
                    "resource_id": item["id"],
                    "type": need_type,
                    "quantity": take_qty,
                    "unit": item.get("unit", "units"),
                    "warehouse": item.get("warehouse_name", "Unknown")
                })
                
        if allocated_qty < need_qty:
            shortfalls.append({
                "type": need_type,
                "requested": need_qty,
                "allocated": allocated_qty,
                "shortfall": need_qty - allocated_qty
            })
            
    return {
        "resources_allocated": allocated,
        "shortfalls": shortfalls,
        "allocated_at": datetime.utcnow().isoformat()
    }

RESOURCE_COORDINATION_INSTRUCTION = """
You are the AegisAI Resource Coordination Agent. Your role is to balance shelter capacities, hospital beds, and logistics inventories.
You select the best shelters/hospitals based on proximity and load, calculate supply requirements, and commit DB reservations.
"""

resource_coordination_agent = None
if ADK_AVAILABLE and settings.gemini_available:
    resource_coordination_agent = Agent(
        name="resource_coordination",
        model="gemini-2.0-flash",
        instruction=RESOURCE_COORDINATION_INSTRUCTION,
        tools=[find_best_shelter, find_best_hospital, calculate_resource_needs, allocate_resources]
    )

async def run_resource_coordination(incident_data: dict, detection_result: dict, location_result: dict) -> dict:
    loc = incident_data.get("location") or {}
    lat = loc.get("lat") or 19.0380
    lng = loc.get("lng") or 72.8526
    
    inc_type = detection_result.get("incident_type", "flood")
    severity = detection_result.get("severity", "medium")
    
    # 1. Shelter Recommendation
    shelter_res = await find_best_shelter(lat, lng, victim_count=25)
    best_shelter = shelter_res.get("recommended_shelter")
    
    # 2. Hospital Recommendation
    hosp_res = await find_best_hospital(lat, lng, severity)
    best_hosp = hosp_res.get("recommended_hospital")
    
    # 3. Supply Calculations
    needs = await calculate_resource_needs(inc_type, severity, estimated_victims=60)
    
    # 4. Inventory Allocation
    allocation = await allocate_resources(incident_data.get("id", "unknown"), needs)
    
    # Calculate travel times (mock estimate)
    estimated_arrival_minutes = 20
    if best_shelter:
        dist = best_shelter.get("distance_km", 5.0)
        estimated_arrival_minutes = max(5, int(dist * 3)) # 3 mins per km approx
        
    return {
        "agent": "resource_coordination",
        "recommended_shelter": best_shelter,
        "recommended_hospital": best_hosp,
        "resources_allocated": allocation.get("resources_allocated", []),
        "shortfalls": allocation.get("shortfalls", []),
        "estimated_arrival_minutes": estimated_arrival_minutes
    }
