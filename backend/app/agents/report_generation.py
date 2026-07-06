import structlog
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.mcp_servers.pdf_mcp import pdf_mcp
from app.mcp_servers.firestore_mcp import firestore_mcp

try:
    from google.adk.agents import Agent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None

logger = structlog.get_logger(__name__)

async def compile_and_generate_report(incident_id: str, all_agent_outputs: dict) -> dict:
    """Consolidate pipeline logs and compile PDF operational brief via PDF MCP."""
    # 1. Fetch current incident record from database
    inc_query = await firestore_mcp.get_document("incidents", incident_id)
    incident = inc_query.get("data")
    if not incident:
        # Fallback to direct provided info
        incident = {
            "id": incident_id,
            "description": "Emergency event details",
            "severity": "medium",
            "incident_type": "flood",
            "status": "active"
        }
        
    # 2. Fetch linked mission details if available
    mission = None
    mission_id = incident.get("mission_id")
    if mission_id:
        mis_query = await firestore_mcp.get_document("missions", mission_id)
        mission = mis_query.get("data")
        
    # 3. Call PDF generation tool
    pdf_bytes = await pdf_mcp.generate_incident_report(incident, mission)
    
    # 4. Save file to disk
    filename = f"aegisai_report_{incident_id}.pdf"
    file_path = await pdf_mcp.save_report_to_file(pdf_bytes, filename)
    
    # 5. Store report record in DB
    report_id = f"rep_{incident_id}"
    report_doc = {
        "id": report_id,
        "incident_id": incident_id,
        "filename": filename,
        "file_path": file_path,
        "file_size_kb": round(len(pdf_bytes) / 1024.0, 1),
        "generated_at": datetime.utcnow().isoformat(),
        "summary_text": f"Operational Brief generated for incident {incident_id}. Threat type: {incident.get('incident_type', '').upper()}."
    }
    
    await firestore_mcp.create_document("reports", report_doc, doc_id=report_id)
    
    # Create notification for report generation
    notif_id = f"notif_{str(uuid.uuid4())[:8]}"
    await firestore_mcp.create_document("notifications", {
        "id": notif_id,
        "type": "info",
        "message": f"📄 [Report Generated] A new situation report brief {report_id.upper()} has been generated for Incident {incident_id}.",
        "status": "unread",
        "created_at": datetime.utcnow().isoformat()
    }, doc_id=notif_id)
    
    return {
        "report_id": report_id,
        "filename": filename,
        "file_path": file_path,
        "generated_at": report_doc["generated_at"],
        "summary": report_doc["summary_text"]
    }

async def get_report_metadata(report_id: str) -> dict:
    """Fetch report entry by ID."""
    rep_query = await firestore_mcp.get_document("reports", report_id)
    return rep_query.get("data") or {}

REPORT_GENERATION_INSTRUCTION = """
You are the AegisAI Report Generation Agent. Your role is to compile all data points into a PDF brief.
You call the pdf-mcp to generate files and store reports metadata in Firestore.
"""

report_generation_agent = None
if ADK_AVAILABLE and settings.gemini_available:
    report_generation_agent = Agent(
        name="report_generation",
        model="gemini-2.0-flash",
        instruction=REPORT_GENERATION_INSTRUCTION,
        tools=[compile_and_generate_report, get_report_metadata]
    )

async def run_report_generation(incident_id: str, all_outputs: dict) -> dict:
    res = await compile_and_generate_report(incident_id, all_outputs)
    return {
        "agent": "report_generation",
        **res
    }
