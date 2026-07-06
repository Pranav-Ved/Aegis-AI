import uuid
import structlog
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, BackgroundTasks, status, Query, HTTPException
from starlette.requests import Request

from app.core.config import settings
from app.core.security import get_current_user, get_current_user_optional, require_role
from app.core.middleware import limiter
from app.core.prompt_guard import validate_emergency_text
from app.core.exceptions import NotFoundError
from app.models.emergency import Incident, IncidentCreate, IncidentStatus, IncidentListResponse
from app.models.user import User
from app.services.incident_service import IncidentService
from app.mcp_servers.firestore_mcp import firestore_mcp
from app.websocket.manager import manager
from app.agents.orchestrator import orchestrator

router = APIRouter()
logger = structlog.get_logger(__name__)

async def run_agent_pipeline(incident_id: str, incident_data: dict):
    """Background task processing incident through all ADK sub-agents."""
    async def ws_callback(event):
        # Broadcast agent progress to the dashboard WebSocket
        await manager.broadcast_agent_progress(event["agent"], event["status"], event.get("data"))
        
    logger.info("Starting multi-agent response pipeline", incident_id=incident_id)
    result = await orchestrator.process_emergency(incident_id, incident_data, ws_callback)
    
    # Broadcast final completion flag
    await manager.broadcast("dashboard", {
        "event": "workflow_completed",
        "incident_id": incident_id,
        "status": result.get("status")
    })
    logger.info("Multi-agent response pipeline finished", incident_id=incident_id, status=result.get("status"))


@router.post("/report", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(settings.rate_limit_emergency)
async def report_emergency(
    request: Request,
    incident_data: IncidentCreate,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Submit a citizen or responder disaster report.
    Triggers the Google ADK Multi-Agent pipeline in the background.
    """
    user_id = current_user.id if current_user else "anonymous"
    service = IncidentService(firestore_mcp)
    
    # Validation (field validator does prompt injection guard)
    incident = await service.create_incident(incident_data, user_id)
    
    # Format payload for background processing
    incident_dict = incident.model_dump()
    # Serialize datetime values to iso format for json processing
    incident_dict["created_at"] = incident_dict["created_at"].isoformat()
    incident_dict["updated_at"] = incident_dict["updated_at"].isoformat()
    
    # Broadcast to active WebSockets
    await manager.broadcast_incident_created(incident_dict)
    
    # Queue background task
    background_tasks.add_task(run_agent_pipeline, incident.id, incident_dict)
    
    return {
        "incident_id": incident.id,
        "status": "reported",
        "message": "Emergency report registered. Dispatching response agents...",
        "ai_available": settings.gemini_available
    }


@router.post("/", response_model=dict, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(settings.rate_limit_emergency)
async def report_emergency_root(
    request: Request,
    incident_data: IncidentCreate,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Alias for POST / to match frontend submitting without sub-route."""
    return await report_emergency(request, incident_data, background_tasks, current_user)


@router.get("/", response_model=List[Incident])
async def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status (reported, active, resolved, closed)"),
    severity: Optional[str] = Query(None, description="Filter by severity (critical, high, medium, low)"),
    incident_type: Optional[str] = Query(None, description="Filter by type (flood, fire, earthquake, etc)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List recent incidents with filters and pagination, returning flat list for frontend compatibility."""
    service = IncidentService(firestore_mcp)
    res = await service.list_incidents(
        status=status,
        severity=severity,
        incident_type=incident_type,
        skip=skip,
        limit=limit
    )
    return res.items


@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str, current_user: User = Depends(get_current_user)):
    """Retrieve full detail profile of an incident, including all agent results."""
    service = IncidentService(firestore_mcp)
    return await service.get_incident(incident_id)


@router.put("/{incident_id}/resolve", response_model=Incident)
async def resolve_incident(
    incident_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resolve an incident and update the status in the database."""
    service = IncidentService(firestore_mcp)
    updated = await service.update_incident_status(incident_id, IncidentStatus.resolved)
    
    # Broadcast to dashboard WebSocket
    await manager.broadcast("dashboard", {
        "event": "incident_updated",
        "data": updated.model_dump()
    })
    
    return updated


@router.patch("/{incident_id}/status", response_model=Incident)
async def update_incident_status(
    incident_id: str,
    status_update: dict,  # e.g. {"status": "resolved"}
    current_user: User = Depends(require_role(["government", "admin"]))
):
    """
    Resolve or close an active incident.
    Restricted to Government Officials and System Administrators.
    """
    new_status_str = status_update.get("status")
    if not new_status_str or new_status_str not in [s.value for s in IncidentStatus]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid status value. Allowed: {[s.value for s in IncidentStatus]}"
        )
        
    service = IncidentService(firestore_mcp)
    updated = await service.update_incident_status(incident_id, IncidentStatus(new_status_str))
    
    # Broadcast status change to websockets
    await manager.broadcast("dashboard", {
        "event": "incident_updated",
        "data": updated.model_dump()
    })
    
    return updated
