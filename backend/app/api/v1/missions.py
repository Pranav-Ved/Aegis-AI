from typing import Optional, List
from datetime import datetime
import uuid
import structlog
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.core.security import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.mission import Mission, MissionStatus, MissionUpdate
from app.mcp_servers.firestore_mcp import firestore_mcp
from app.websocket.manager import manager
from app.core.exceptions import NotFoundError

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/", response_model=List[Mission])
async def list_missions(
    status: Optional[str] = Query(None, description="Filter by status (planned, active, completed, failed)"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """List all rescue missions with filters."""
    filters = []
    if status:
        filters.append({"field": "status", "op": "==", "value": status})
        
    res = await firestore_mcp.query_collection("missions", filters=filters, limit=1000, order_by="-created_at")
    docs = res.get("data", [])
    
    paginated = docs[skip:skip + limit]
    return [Mission(**doc) for doc in paginated]

@router.get("/active/count")
async def get_active_missions_count(current_user: User = Depends(get_current_user)):
    """Retrieve absolute count of active deployments."""
    res = await firestore_mcp.query_collection("missions", filters=[{"field": "status", "op": "==", "value": "active"}])
    docs = res.get("data", [])
    return {"count": len(docs)}

@router.get("/{mission_id}", response_model=Mission)
async def get_mission(mission_id: str, current_user: User = Depends(get_current_user)):
    """Retrieve full directives and responder list for a mission."""
    res = await firestore_mcp.get_document("missions", mission_id)
    doc = res.get("data")
    if not doc:
        raise NotFoundError(f"Rescue Mission {mission_id} not found")
    return Mission(**doc)

@router.patch("/{mission_id}", response_model=Mission)
async def update_mission(
    mission_id: str,
    update_data: MissionUpdate,
    current_user: User = Depends(require_role(["volunteer", "ngo", "government", "admin"]))
):
    """
    Update rescue deployment state or add step logs.
    Restricted to Responders, NGOs, and Administrators.
    """
    res = await firestore_mcp.get_document("missions", mission_id)
    doc = res.get("data")
    if not doc:
        raise NotFoundError(f"Mission {mission_id} not found")
        
    mission = Mission(**doc)
    update_fields = {"updated_at": datetime.utcnow().isoformat()}
    
    if update_data.status:
        mission.status = update_data.status
        update_fields["status"] = update_data.status.value
        
        # If completing, set completed timestamp
        if update_data.status == MissionStatus.completed:
            mission.completed_at = datetime.utcnow()
            update_fields["completed_at"] = mission.completed_at.isoformat()
            
            # Auto update linked incident status to resolved!
            inc_id = mission.incident_id
            await firestore_mcp.update_document("incidents", inc_id, {
                "status": "resolved",
                "updated_at": datetime.utcnow().isoformat()
            })
            # Broadcast the updated incident as resolved
            inc_data = await firestore_mcp.get_document("incidents", inc_id)
            if inc_data.get("data"):
                await manager.broadcast("dashboard", {
                    "event": "incident_updated",
                    "data": inc_data.get("data")
                })
                
            # Create notification for mission completion
            notif_id = f"notif_{str(uuid.uuid4())[:8]}"
            await firestore_mcp.create_document("notifications", {
                "id": notif_id,
                "type": "info",
                "message": f"✅ [Mission Completed] Mission {mission_id.upper()} has been marked as completed. Linked incident {inc_id} resolved.",
                "status": "unread",
                "created_at": datetime.utcnow().isoformat()
            }, doc_id=notif_id)
            
    await firestore_mcp.update_document("missions", mission_id, update_fields)
    
    # Broadcast mission update to live web sockets
    mission_dict = mission.model_dump()
    # Serialize datetime values
    mission_dict["created_at"] = mission_dict["created_at"].isoformat()
    mission_dict["updated_at"] = mission_dict["updated_at"].isoformat()
    if mission_dict.get("completed_at"):
        mission_dict["completed_at"] = mission_dict["completed_at"].isoformat()
        
    await manager.broadcast_mission_updated(mission_dict)
    
    return mission
