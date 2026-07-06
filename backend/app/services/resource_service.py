import math
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.resource import Shelter, Hospital, Resource, ResourceType, ShelterStatus, HospitalStatus
from app.core.exceptions import NotFoundError

class ResourceService:
    def __init__(self, db):
        self.db = db
        
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Haversine formula to calculate distance between two coordinates in kilometers."""
        R = 6371.0  # Earth radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
        
    async def get_shelters(self, lat: Optional[float] = None, lng: Optional[float] = None) -> List[Shelter]:
        docs = await self.db.query_collection("shelters", limit=100)
        if isinstance(docs, dict) and "data" in docs and "success" in docs:
            docs = docs["data"]
        shelters = [Shelter(**doc) for doc in docs]
        
        if lat is not None and lng is not None:
            for s in shelters:
                s.distance_km = round(self._calculate_distance(lat, lng, s.location.lat, s.location.lng), 2)
            # Sort by distance
            shelters.sort(key=lambda x: x.distance_km or 0.0)
            
        return shelters
        
    async def get_hospitals(self, lat: Optional[float] = None, lng: Optional[float] = None) -> List[Hospital]:
        docs = await self.db.query_collection("hospitals", limit=100)
        if isinstance(docs, dict) and "data" in docs and "success" in docs:
            docs = docs["data"]
        hospitals = [Hospital(**doc) for doc in docs]
        
        if lat is not None and lng is not None:
            for h in hospitals:
                h.distance_km = round(self._calculate_distance(lat, lng, h.location.lat, h.location.lng), 2)
            # Sort by distance
            hospitals.sort(key=lambda x: x.distance_km or 0.0)
            
        return hospitals
        
    async def get_resource_inventory(self) -> Dict[str, List[Resource]]:
        docs = await self.db.query_collection("resources", limit=1000)
        if isinstance(docs, dict) and "data" in docs and "success" in docs:
            docs = docs["data"]
        resources = [Resource(**doc) for doc in docs]
        
        grouped: Dict[str, List[Resource]] = {}
        for r in resources:
            r_type = r.type.value
            if r_type not in grouped:
                grouped[r_type] = []
            grouped[r_type].append(r)
            
        return grouped
        
    async def update_shelter_occupancy(self, shelter_id: str, delta: int) -> Shelter:
        data = await self.db.get_document("shelters", shelter_id)
        if isinstance(data, dict) and "data" in data and "success" in data:
            data = data["data"]
        if not data:
            raise NotFoundError(f"Shelter {shelter_id} not found")
            
        shelter = Shelter(**data)
        new_occ = max(0, min(shelter.total_capacity, shelter.current_occupancy + delta))
        was_full = shelter.status == ShelterStatus.full
        shelter.current_occupancy = new_occ
        shelter.status = ShelterStatus.full if new_occ >= shelter.total_capacity else ShelterStatus.open
        shelter.updated_at = datetime.utcnow()
        
        await self.db.update_document("shelters", shelter_id, {
            "current_occupancy": shelter.current_occupancy,
            "status": shelter.status.value,
            "updated_at": shelter.updated_at.isoformat()
        })
        
        if shelter.status == ShelterStatus.full and not was_full:
            notif_id = f"notif_{str(uuid.uuid4())[:8]}"
            await self.db.create_document("notifications", {
                "id": notif_id,
                "type": "alert",
                "message": f"🚨 [Shelter Full] Relief Shelter '{shelter.name}' has reached maximum occupancy capacity ({shelter.total_capacity}/{shelter.total_capacity}).",
                "status": "unread",
                "created_at": datetime.utcnow().isoformat()
            }, doc_id=notif_id)
            
        return shelter
        
    async def update_hospital_beds(self, hospital_id: str, available_beds: int) -> Hospital:
        data = await self.db.get_document("hospitals", hospital_id)
        if isinstance(data, dict) and "data" in data and "success" in data:
            data = data["data"]
        if not data:
            raise NotFoundError(f"Hospital {hospital_id} not found")
            
        hospital = Hospital(**data)
        was_overwhelmed = hospital.status == HospitalStatus.overwhelmed
        hospital.available_beds = max(0, min(hospital.emergency_capacity, available_beds))
        hospital.status = HospitalStatus.overwhelmed if hospital.available_beds == 0 else HospitalStatus.operational
        hospital.updated_at = datetime.utcnow()
        
        await self.db.update_document("hospitals", hospital_id, {
            "available_beds": hospital.available_beds,
            "status": hospital.status.value,
            "updated_at": hospital.updated_at.isoformat()
        })
        
        if hospital.status == HospitalStatus.overwhelmed and not was_overwhelmed:
            notif_id = f"notif_{str(uuid.uuid4())[:8]}"
            await self.db.create_document("notifications", {
                "id": notif_id,
                "type": "alert",
                "message": f"⚠️ [Hospital Overwhelmed] Hospital '{hospital.name}' reports 0 available emergency beds.",
                "status": "unread",
                "created_at": datetime.utcnow().isoformat()
            }, doc_id=notif_id)
            
        return hospital
