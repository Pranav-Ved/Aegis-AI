import io
import structlog
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.security import get_current_user, require_role
from app.models.user import User
from app.mcp_servers.firestore_mcp import firestore_mcp
from app.mcp_servers.pdf_mcp import pdf_mcp
from app.mcp_servers.logging_mcp import logging_mcp
from app.core.exceptions import NotFoundError

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/")
async def list_reports(current_user: User = Depends(require_role(["government", "admin"]))):
    """Retrieve listing of compiled operational reports."""
    res = await firestore_mcp.query_collection("reports", limit=100)
    return res.get("data", [])

@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(require_role(["government", "admin"]))
):
    """
    Download a compiled PDF brief.
    Restricted to Government Officials and Administrators.
    """
    rep_res = await firestore_mcp.get_document("reports", report_id)
    report = rep_res.get("data")
    if not report:
        raise NotFoundError(f"Report brief {report_id} not found")
        
    incident_id = report.get("incident_id")
    
    # 1. Fetch incident data
    inc_res = await firestore_mcp.get_document("incidents", incident_id)
    incident = inc_res.get("data")
    if not incident:
        raise NotFoundError(f"Linked incident data {incident_id} not found")
        
    # 2. Fetch linked mission details if available
    mission = None
    mission_id = incident.get("mission_id")
    if mission_id:
        mis_res = await firestore_mcp.get_document("missions", mission_id)
        mission = mis_res.get("data")
        
    # 3. Generate PDF bytes on the fly (ensures real-time updates are captured)
    pdf_bytes = await pdf_mcp.generate_incident_report(incident, mission)
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=aegisai_report_{report_id}.pdf"}
    )

@router.post("/generate")
async def generate_report_auto(
    body: dict,
    current_user: User = Depends(require_role(["government", "admin"]))
):
    """
    Generate a report automatically picking the most recent unresolved incident.
    Called by the frontend 'Generate Report' button.
    """
    from app.mcp_servers.firestore_mcp import firestore_mcp as fmcp
    # Get most recent active incident
    inc_res = await fmcp.query_collection("incidents", limit=5)
    incidents = inc_res.get("data", [])
    active = [i for i in incidents if i.get("status") in ("reported", "processing", "active")]
    if not active:
        active = incidents
    if not active:
        raise HTTPException(status_code=404, detail="No incidents found to generate report for")
    
    incident_id = active[0]["id"]
    from app.agents.report_generation import compile_and_generate_report
    report_meta = await compile_and_generate_report(incident_id, {"incident_id": incident_id})
    return report_meta

@router.post("/generate/{incident_id}")
async def generate_report_manually(
    incident_id: str,
    current_user: User = Depends(require_role(["government", "admin"]))
):
    """
    Manually compile operational PDF for an incident.
    Restricted to Government Officials and Administrators.
    """
    inc_res = await firestore_mcp.get_document("incidents", incident_id)
    incident = inc_res.get("data")
    if not incident:
        raise NotFoundError(f"Incident {incident_id} not found")
        
    # Import agent call helper
    from app.agents.report_generation import compile_and_generate_report
    
    # Compile report metadata and save pdf file
    report_meta = await compile_and_generate_report(incident_id, {"incident_id": incident_id})
    return report_meta
