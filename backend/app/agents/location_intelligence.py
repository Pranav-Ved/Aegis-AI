import structlog
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.mcp_servers.maps_mcp import maps_mcp
from app.mcp_servers.weather_mcp import weather_mcp

try:
    from google.adk.agents import Agent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None

logger = structlog.get_logger(__name__)

async def get_location_context(lat: float, lng: float, description: Optional[str] = None) -> dict:
    """Retrieve weather summaries, geocoded address, and nearby critical shelters/hospitals."""
    # 1. Reverse Geocode Coordinates to Address
    geo_res = await maps_mcp.reverse_geocode(lat, lng)
    address = geo_res.get("data", {}).get("address", "Coordinates Provided")
    
    # 2. Query Nearby Shelters and Hospitals
    shelter_res = await maps_mcp.find_nearby_places(lat, lng, "shelter", radius_km=10.0)
    hospital_res = await maps_mcp.find_nearby_places(lat, lng, "hospital", radius_km=10.0)
    
    nearby_shelters = shelter_res.get("data", [])
    nearby_hospitals = hospital_res.get("data", [])
    
    # 3. Query Weather Conditions
    weather_res = await weather_mcp.get_current_weather(lat, lng)
    weather_data = weather_res.get("data", {})
    weather_summary = f"{weather_data.get('condition', 'Unknown')}: {weather_data.get('temp_celsius', 'N/A')}°C, Winds {weather_data.get('wind_speed_kmh', 'N/A')} km/h"
    
    # 4. Assess storm surge/hazard risk level
    risk_res = await weather_mcp.assess_disaster_risk(lat, lng)
    risk_level = risk_res.get("data", {}).get("risk_level", "medium")
    
    return {
        "address": address,
        "nearby_shelters": nearby_shelters,
        "nearby_hospitals": nearby_hospitals,
        "weather_summary": weather_summary,
        "risk_level": risk_level
    }

async def find_evacuation_route(from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> dict:
    """Calculate safest evacuation route to a shelter."""
    route_res = await maps_mcp.get_directions(from_lat, from_lng, to_lat, to_lng)
    return route_res.get("data", {})

LOCATION_INTELLIGENCE_INSTRUCTION = """
You are the AegisAI Location Intelligence Agent. Your job is to analyze coordinates, find nearby evacuation assets, and obtain weather forecast risks.
You call the maps-mcp and weather-mcp tools to aggregate location summaries for the emergency.
"""

location_intelligence_agent = None
if ADK_AVAILABLE and settings.gemini_available:
    location_intelligence_agent = Agent(
        name="location_intelligence",
        model="gemini-2.0-flash",
        instruction=LOCATION_INTELLIGENCE_INSTRUCTION,
        tools=[get_location_context, find_evacuation_route]
    )

async def run_location_intelligence(incident_data: dict) -> dict:
    loc = incident_data.get("location") or {}
    lat = loc.get("lat") or 19.0380
    lng = loc.get("lng") or 72.8526
    desc = incident_data.get("description", "")
    
    res = await get_location_context(lat, lng, desc)
    
    return {
        "agent": "location_intelligence",
        **res
    }
