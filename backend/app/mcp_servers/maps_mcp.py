import math
import httpx
import structlog
from typing import Optional, List, Dict, Any

from app.mcp_servers.base import BaseMCPServer
from app.core.config import settings

logger = structlog.get_logger(__name__)

# Mock geocoded database for fallback (Mumbai area)
MOCK_LOCATIONS = {
    "dharavi": {"lat": 19.0380, "lng": 72.8526, "formatted_address": "Dharavi, Mumbai, Maharashtra, India"},
    "bandra": {"lat": 19.0596, "lng": 72.8295, "formatted_address": "Bandra, Mumbai, Maharashtra, India"},
    "sion": {"lat": 19.0390, "lng": 72.8619, "formatted_address": "Sion, Mumbai, Maharashtra, India"},
    "parel": {"lat": 18.9967, "lng": 72.8414, "formatted_address": "Parel, Mumbai, Maharashtra, India"},
    "andheri": {"lat": 19.1136, "lng": 72.8697, "formatted_address": "Andheri, Mumbai, Maharashtra, India"}
}

MOCK_PLACES = [
    {"id": "shelter_001", "name": "Dharavi Relief Center", "address": "Dharavi, Mumbai", "lat": 19.0380, "lng": 72.8526, "phone": "+91-22-2414-0000", "type": "shelter"},
    {"id": "shelter_002", "name": "BKC Emergency Camp", "address": "Bandra Kurla Complex, Mumbai", "lat": 19.0642, "lng": 72.8669, "phone": "+91-22-2659-0000", "type": "shelter"},
    {"id": "shelter_003", "name": "Andheri Sports Ground Camp", "address": "Andheri East, Mumbai", "lat": 19.1136, "lng": 72.8697, "phone": "+91-22-2836-0000", "type": "shelter"},
    {"id": "hospital_001", "name": "KEM Hospital", "address": "Parel, Mumbai", "lat": 18.9967, "lng": 72.8414, "phone": "+91-22-2410-7000", "type": "hospital"},
    {"id": "hospital_002", "name": "Lokmanya Tilak Municipal Hospital", "address": "Sion, Mumbai", "lat": 19.0390, "lng": 72.8619, "phone": "+91-22-2404-6000", "type": "hospital"},
    {"id": "fire_001", "name": "Dharavi Fire Station", "address": "Dharavi Road, Mumbai", "lat": 19.0410, "lng": 72.8510, "phone": "+91-22-2407-1111", "type": "fire_station"},
    {"id": "police_001", "name": "Shahu Nagar Police Station", "address": "Dharavi, Mumbai", "lat": 19.0350, "lng": 72.8550, "phone": "+91-22-2407-2222", "type": "police_station"}
]

class MapsMCPServer(BaseMCPServer):
    name = "maps-mcp"
    description = "Provides geocoding, routing, and nearby facility search services"
    
    def _haversine(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Haversine distance in km."""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    async def geocode(self, address: str) -> dict:
        """Geocode an address to lat/lng coordinates."""
        async def _run():
            if settings.google_maps_api_key:
                url = "https://maps.googleapis.com/maps/api/geocode/json"
                params = {"address": address, "key": settings.google_maps_api_key}
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "OK" and data.get("results"):
                            result = data["results"][0]
                            loc = result["geometry"]["location"]
                            return {
                                "lat": loc["lat"],
                                "lng": loc["lng"],
                                "formatted_address": result["formatted_address"],
                                "place_id": result["place_id"]
                            }
            
            # Fallback
            addr_lower = address.lower()
            for key, val in MOCK_LOCATIONS.items():
                if key in addr_lower:
                    return val
            # Default to Mumbai center
            return {"lat": 19.0760, "lng": 72.8777, "formatted_address": f"{address} (Mocked)", "place_id": "mock_default"}
            
        res = await self._execute_tool("geocode", _run)
        return res.to_dict()

    async def reverse_geocode(self, lat: float, lng: float) -> dict:
        """Convert lat/lng to a readable address."""
        async def _run():
            if settings.google_maps_api_key:
                url = "https://maps.googleapis.com/maps/api/geocode/json"
                params = {"latlng": f"{lat},{lng}", "key": settings.google_maps_api_key}
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "OK" and data.get("results"):
                            return {
                                "address": data["results"][0]["formatted_address"],
                                "city": "Mumbai",
                                "state": "Maharashtra",
                                "country": "India"
                            }
            
            # Fallback
            closest = None
            min_dist = float("inf")
            for key, val in MOCK_LOCATIONS.items():
                dist = self._haversine(lat, lng, val["lat"], val["lng"])
                if dist < min_dist:
                    min_dist = dist
                    closest = val
                    
            if closest and min_dist < 5.0:
                return {
                    "address": closest["formatted_address"],
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "country": "India"
                }
            return {
                "address": f"Coordinates ({lat:.4f}, {lng:.4f})",
                "city": "Mumbai",
                "state": "Maharashtra",
                "country": "India"
            }
            
        res = await self._execute_tool("reverse_geocode", _run)
        return res.to_dict()

    async def find_nearby_places(self, lat: float, lng: float, place_type: str, radius_km: float = 5.0) -> dict:
        """Find nearby shelters, hospitals, fire stations, or police stations."""
        async def _run():
            if settings.google_maps_api_key:
                # Real Places API call
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                g_type = place_type
                if place_type == "shelter":
                    g_type = "civic_building"
                elif place_type == "hospital":
                    g_type = "hospital"
                elif place_type == "fire_station":
                    g_type = "fire_station"
                elif place_type == "police_station":
                    g_type = "police_station"
                    
                params = {
                    "location": f"{lat},{lng}",
                    "radius": int(radius_km * 1000),
                    "type": g_type,
                    "key": settings.google_maps_api_key
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        places = []
                        for item in data.get("results", []):
                            i_lat = item["geometry"]["location"]["lat"]
                            i_lng = item["geometry"]["location"]["lng"]
                            places.append({
                                "id": item["place_id"],
                                "name": item["name"],
                                "address": item.get("vicinity", ""),
                                "lat": i_lat,
                                "lng": i_lng,
                                "distance_km": round(self._haversine(lat, lng, i_lat, i_lng), 2),
                                "type": place_type
                            })
                        return places

            # Fallback
            places = []
            for place in MOCK_PLACES:
                if place["type"] == place_type or place_type == "all":
                    dist = self._haversine(lat, lng, place["lat"], place["lng"])
                    if dist <= radius_km:
                        places.append({
                            **place,
                            "distance_km": round(dist, 2)
                        })
            places.sort(key=lambda x: x["distance_km"])
            return places

        res = await self._execute_tool("find_nearby_places", _run)
        return res.to_dict()

    async def get_directions(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> dict:
        """Calculate routes and driving directions."""
        async def _run():
            if settings.google_maps_api_key:
                url = "https://maps.googleapis.com/maps/api/directions/json"
                params = {
                    "origin": f"{origin_lat},{origin_lng}",
                    "destination": f"{dest_lat},{dest_lng}",
                    "key": settings.google_maps_api_key
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "OK" and data.get("routes"):
                            route = data["routes"][0]
                            leg = route["legs"][0]
                            steps = [step["html_instructions"] for step in leg["steps"]]
                            return {
                                "distance_km": round(leg["distance"]["value"] / 1000.0, 2),
                                "duration_minutes": round(leg["duration"]["value"] / 60.0, 1),
                                "steps": steps,
                                "polyline": route["overview_polyline"]["points"]
                            }

            # Fallback
            dist = self._haversine(origin_lat, origin_lng, dest_lat, dest_lng)
            duration = (dist / 30.0) * 60.0  # Assumes 30 km/h average speed in disaster traffic
            return {
                "distance_km": round(dist, 2),
                "duration_minutes": round(duration, 1),
                "steps": [
                    "Head north toward main evacuation route.",
                    "Turn right onto critical emergency clearance corridor.",
                    "Proceed to the recommended destination checkpoint."
                ],
                "polyline": "mock_polyline_data"
            }

        res = await self._execute_tool("get_directions", _run)
        return res.to_dict()

    async def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> dict:
        """Calculate distance in meters and km between two points."""
        async def _run():
            dist_km = self._haversine(lat1, lng1, lat2, lng2)
            return {
                "distance_km": round(dist_km, 2),
                "distance_meters": int(dist_km * 1000)
            }
        res = await self._execute_tool("calculate_distance", _run)
        return res.to_dict()

maps_mcp = MapsMCPServer()
