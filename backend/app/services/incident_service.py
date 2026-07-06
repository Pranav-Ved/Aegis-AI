import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.models.emergency import Incident, IncidentCreate, IncidentStatus, IncidentListResponse
from app.core.exceptions import NotFoundError

class IncidentService:
    def __init__(self, db):
        self.db = db
        
    async def create_incident(self, incident_data: IncidentCreate, user_id: str) -> Incident:
        incident_id = str(uuid.uuid4())
        
        # Map location
        loc_dict = None
        if incident_data.location:
            loc_dict = incident_data.location.model_dump()
            
        incident = Incident(
            id=incident_id,
            description=incident_data.description,
            incident_type=incident_data.incident_type,
            severity=incident_data.severity_hint,
            status=IncidentStatus.reported,
            location=incident_data.location,
            media_urls=incident_data.media_urls,
            reported_by=user_id,
            reporter_name=incident_data.reporter_name,
            reporter_phone=incident_data.reporter_phone,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            agent_status={"emergency_intake": "completed"}
        )
        
        await self.db.create_document("incidents", incident.model_dump(), doc_id=incident_id)
        
        # Create a database notification
        notif_id = f"notif_{str(uuid.uuid4())[:8]}"
        await self.db.create_document("notifications", {
            "id": notif_id,
            "type": "alert",
            "message": f"🚨 [New Incident] {incident.incident_type.value.replace('_', ' ').capitalize() if incident.incident_type else 'Emergency'} reported: {incident.description[:60]}...",
            "status": "unread",
            "created_at": datetime.utcnow().isoformat()
        }, doc_id=notif_id)
        
        return incident
        
    async def get_incident(self, incident_id: str) -> Incident:
        data = await self.db.get_document("incidents", incident_id)
        if isinstance(data, dict) and "data" in data and "success" in data:
            data = data["data"]
        if not data:
            raise NotFoundError(f"Incident {incident_id} not found")
        return Incident(**data)
        
    async def list_incidents(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        incident_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> IncidentListResponse:
        filters = []
        if status:
            filters.append({"field": "status", "op": "==", "value": status})
        if severity:
            filters.append({"field": "severity", "op": "==", "value": severity})
        if incident_type:
            filters.append({"field": "incident_type", "op": "==", "value": incident_type})
            
        docs = await self.db.query_collection("incidents", filters=filters, limit=1000, order_by="-created_at")
        if isinstance(docs, dict) and "data" in docs and "success" in docs:
            docs = docs["data"]
            
        total = len(docs)
        paginated_docs = docs[skip:skip + limit]
        
        items = [Incident(**doc) for doc in paginated_docs]
        
        # Calculate pagination details
        page = (skip // limit) + 1 if limit else 1
        
        return IncidentListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit
        )
        
    async def update_incident_status(self, incident_id: str, status: IncidentStatus) -> Incident:
        incident = await self.get_incident(incident_id)
        incident.status = status
        incident.updated_at = datetime.utcnow()
        
        await self.db.update_document("incidents", incident_id, {
            "status": status.value,
            "updated_at": incident.updated_at.isoformat()
        })
        return incident
        
    async def update_agent_result(self, incident_id: str, agent_name: str, result: dict) -> None:
        update_data = {
            f"agent_status.{agent_name}": "done"
        }
        
        if agent_name == "disaster_detection":
            update_data["detection_result"] = result
            if result.get("severity"):
                update_data["severity"] = result.get("severity")
            if result.get("incident_type"):
                update_data["incident_type"] = result.get("incident_type")
        elif agent_name == "location_intelligence":
            update_data["location_context"] = result
            if result.get("address") and not settings.google_maps_api_key:
                # If we got a geocoded address back, update the incident location address field
                update_data["location.address"] = result.get("address")
        elif agent_name == "resource_coordination":
            update_data["resource_plan"] = result
        elif agent_name == "rescue_planning":
            update_data["rescue_plan"] = result
            if result.get("mission_id"):
                update_data["mission_id"] = result.get("mission_id")
                
        await self.db.update_document("incidents", incident_id, update_data)
