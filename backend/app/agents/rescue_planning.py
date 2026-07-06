import uuid
import structlog
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.mcp_servers.firestore_mcp import firestore_mcp

try:
    from google.adk.agents import Agent
    import google.generativeai as genai
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None
    genai = None

logger = structlog.get_logger(__name__)

async def generate_rescue_plan(
    incident_id: str,
    severity: str,
    incident_type: str,
    location_context: dict,
    resource_plan: dict
) -> dict:
    """Generate prioritized rescue steps and team directives."""
    address = location_context.get("address", "Mumbai, India")
    shelter = resource_plan.get("recommended_shelter", {}).get("name", "Local Rescue Camp")
    hospital = resource_plan.get("recommended_hospital", {}).get("name", "City Trauma Center")
    supplies = ", ".join([f"{r.get('quantity')} {r.get('unit')} {r.get('type')}" for r in resource_plan.get("resources_allocated", [])])
    
    # 1. AI planning if available
    if settings.gemini_available and genai:
        try:
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            prompt = (
                f"You are the AegisAI Rescue Planner. Create a tactical rescue operation plan for a {severity} {incident_type} at {address}.\n"
                f"Available assets: Recommended Shelter: {shelter}, Hospital: {hospital}, Allocated Supplies: {supplies}.\n"
                f"Prioritization directive: Critical injuries -> Children -> Elderly -> Disabled -> General public.\n"
                f"Respond ONLY in JSON format containing:\n"
                "{\n"
                "  \"priority_level\": int (1 to 4, 1 is highest),\n"
                "  \"rescue_steps\": List of strings (ordered sequence of tactical instructions),\n"
                "  \"team_assignments\": {\n"
                "     \"extract_team\": string,\n"
                "     \"medical_team\": string,\n"
                "     \"logistics_team\": string\n"
                "  },\n"
                "  \"estimated_completion_hours\": float,\n"
                "  \"special_considerations\": List of strings\n"
                "}"
            )
            response = model.generate_content(prompt)
            import json
            text_clean = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text_clean)
            return data
        except Exception as e:
            logger.error("rescue_planning_gemini_failed", error=str(e))
            
    # 2. Heuristic fallback based on disaster type
    priority = 2
    if severity == "critical":
        priority = 1
    elif severity == "medium":
        priority = 3
    elif severity == "low":
        priority = 4
        
    steps = []
    assignments = {
        "extract_team": "NDRF Water Extraction Squad" if incident_type == "flood" else "Fire Rescue Team A",
        "medical_team": "Civil Hospital Triage Squad B",
        "logistics_team": "Municipal Logistics Unit"
    }
    considerations = []
    
    if incident_type == "flood":
        steps = [
            "Deploy rubber motorboats to extract citizens stranded on rooftops.",
            "Establish floating medical triage checkpoint at high-ground area.",
            "Transport evacuated victims to Dharavi Relief Center.",
            "Dispatch allocated water and food packages to the relief shelter."
        ]
        considerations = ["Submerged electrical wires hazard", "Risk of leptospirosis water contamination"]
    elif incident_type == "fire":
        steps = [
            "Establish perimeter control and mobilize structural cooling sprays.",
            "Conduct search and rescue in building structure, prioritized by floor hazard.",
            "Triage burns and smoke inhalation victims at hospital trauma bay.",
            "Establish secure volunteer zone at local fire house."
        ]
        considerations = ["Toxic carbon monoxide fumes", "Risk of structural ceiling collapse"]
    elif incident_type == "earthquake":
        steps = [
            "Mobilize canine search teams to evaluate collapsed concrete ruins.",
            "Deploy seismic sound listening devices to check for trapped survivors.",
            "Set up field hospital surgical units near the disaster center.",
            "Mobilize water purification systems and blankets."
        ]
        considerations = ["Continuous aftershocks risk", "Unstable brick structures"]
    else:  # default
        steps = [
            "Deploy emergency evacuation responders to the location.",
            "Triage victims based on active injury severity.",
            "Transport high-injury victims to KEM Hospital.",
            "Escort others to nearest open civic center shelter."
        ]
        considerations = ["Ensure clear routing for logistics supply trucks"]
        
    return {
        "priority_level": priority,
        "rescue_steps": steps,
        "team_assignments": assignments,
        "estimated_completion_hours": 4.5,
        "special_considerations": considerations
    }

async def create_mission(
    incident_id: str,
    rescue_plan: dict,
    shelter_id: Optional[str] = None,
    hospital_id: Optional[str] = None,
    resources_allocated: List[dict] = None
) -> dict:
    """Create a new mission brief record in the database."""
    mission_id = f"mis_{str(uuid.uuid4())[:8]}"
    
    steps = []
    for idx, desc in enumerate(rescue_plan.get("rescue_steps", []), 1):
        steps.append({
            "order": idx,
            "description": desc,
            "status": "pending",
            "completed_at": None
        })
        
    # Seed a responder team
    teams = [
        {
            "id": "team_002",
            "name": rescue_plan.get("team_assignments", {}).get("extract_team", "Civil Search Squad"),
            "role": "Search and Rescue Extraction",
            "contact": "+91-22-2659-1111"
        }
    ]
    
    mission = {
        "id": mission_id,
        "incident_id": incident_id,
        "status": "planned",
        "priority": rescue_plan.get("priority_level", 2),
        "title": f"Tactical Evacuation Mission {mission_id.upper()}",
        "description": f"Rescue mission dispatched for incident {incident_id}.",
        "rescue_steps": steps,
        "assigned_teams": teams,
        "shelter_id": shelter_id,
        "hospital_id": hospital_id,
        "resources_allocated": resources_allocated or [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "completed_at": None
    }
    
    await firestore_mcp.create_document("missions", mission, doc_id=mission_id)
    
    # Create notification for mission assignment
    notif_id = f"notif_{str(uuid.uuid4())[:8]}"
    await firestore_mcp.create_document("notifications", {
        "id": notif_id,
        "type": "info",
        "message": f"📋 [Mission Dispatched] Mission {mission_id.upper()} has been created and teams assigned for Incident {incident_id}.",
        "status": "unread",
        "created_at": datetime.utcnow().isoformat()
    }, doc_id=notif_id)
    
    return {"mission_id": mission_id, "status": "planned"}

RESCUE_PLANNING_INSTRUCTION = """
You are the AegisAI Rescue Planning Agent. Your role is to determine prioritizations and outline tactical mission directives.
You generate ordered steps prioritizing critical victim care, coordinate assignments, and write mission files.
"""

rescue_planning_agent = None
if ADK_AVAILABLE and settings.gemini_available:
    rescue_planning_agent = Agent(
        name="rescue_planning",
        model="gemini-2.0-flash",
        instruction=RESCUE_PLANNING_INSTRUCTION,
        tools=[generate_rescue_plan, create_mission]
    )

async def run_rescue_planning(
    incident_id: str,
    incident_data: dict,
    detection_result: dict,
    location_result: dict,
    resource_plan: dict
) -> dict:
    inc_type = detection_result.get("incident_type", "flood")
    severity = detection_result.get("severity", "medium")
    
    # 1. Compile Plan details
    plan = await generate_rescue_plan(incident_id, severity, inc_type, location_result, resource_plan)
    
    # 2. Write Mission Brief
    shelter_id = resource_plan.get("recommended_shelter", {}).get("id")
    hosp_id = resource_plan.get("recommended_hospital", {}).get("id")
    supplies = resource_plan.get("resources_allocated", [])
    
    mission = await create_mission(incident_id, plan, shelter_id, hosp_id, supplies)
    
    return {
        "agent": "rescue_planning",
        "mission_id": mission.get("mission_id"),
        **plan
    }
