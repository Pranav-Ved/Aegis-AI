import structlog
from fastapi import APIRouter, Depends, status

from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.mcp_servers.firestore_mcp import firestore_mcp

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Retrieve operational statistics and aggregated counters for dashboard widgets."""
    incidents_res = await firestore_mcp.query_collection("incidents", limit=1000)
    incidents = incidents_res.get("data", [])
    
    missions_res = await firestore_mcp.query_collection("missions", limit=1000)
    missions = missions_res.get("data", [])
    
    shelters_res = await firestore_mcp.query_collection("shelters", limit=100)
    shelters = shelters_res.get("data", [])
    
    hospitals_res = await firestore_mcp.query_collection("hospitals", limit=100)
    hospitals = hospitals_res.get("data", [])
    
    # Core aggregation logic
    active_inc = [i for i in incidents if i.get("status") in ("reported", "processing", "active")]
    resolved_inc = [i for i in incidents if i.get("status") == "resolved"]
    crit_inc = [i for i in incidents if i.get("severity") == "critical"]
    
    active_mis = [m for m in missions if m.get("status") == "active"]
    open_shelters = [s for s in shelters if s.get("status") == "open"]
    
    total_shelter_cap = sum(s.get("total_capacity", 0) for s in shelters)
    total_shelter_occ = sum(s.get("current_occupancy", 0) for s in shelters)
    
    total_hosp_beds = sum(h.get("emergency_capacity", 0) for h in hospitals)
    avail_hosp_beds = sum(h.get("available_beds", 0) for h in hospitals)
    
    # Sort incidents by date to find most recent
    sorted_incidents = sorted(incidents, key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {
        "total_incidents": len(incidents),
        "active_incidents": len(active_inc),
        "resolved_incidents": len(resolved_inc),
        "critical_incidents": len(crit_inc),
        "total_missions": len(missions),
        "active_missions": len(active_mis),
        "available_shelters": len(open_shelters),
        "total_shelter_capacity": total_shelter_cap,
        "shelter_occupancy_pct": round((total_shelter_occ / max(1, total_shelter_cap)) * 100, 1),
        "total_hospital_beds": total_hosp_beds,
        "available_hospital_beds": avail_hosp_beds,
        "recent_incidents": sorted_incidents[:5],
        "ai_available": settings.gemini_available,
        "db_mode": settings.db_mode,
        "notifications_mode": settings.notifications_mode,
        "maps_mode": settings.maps_mode,
        "weather_mode": settings.weather_mode
    }

@router.get("/system-status")
async def get_system_status(current_user: User = Depends(get_current_user)):
    """Check check statuses of external APIs (Gemini, Maps, Twilio, SendGrid)."""
    overall_status = "operational"
    
    issues = []
    if not settings.gemini_available:
        issues.append("Gemini AI API Key is missing")
        overall_status = "degraded"
        
    if not settings.google_maps_api_key:
        issues.append("Google Maps API Key is missing")
        overall_status = "degraded"
        
    if not settings.twilio_account_sid:
        issues.append("Twilio Account SID is missing")
        
    if not settings.sendgrid_api_key:
        issues.append("SendGrid API Key is missing")
        
    return {
        "overall_status": overall_status,
        "api_connectivity": {
            "gemini": settings.gemini_available,
            "maps": bool(settings.google_maps_api_key),
            "weather": bool(settings.openweather_api_key),
            "database": settings.db_mode,
            "sms": settings.notifications_mode == "live" and bool(settings.twilio_account_sid),
            "email": settings.notifications_mode == "live" and bool(settings.sendgrid_api_key)
        },
        "issues": issues
    }

@router.get("/notifications")
async def get_notifications(current_user: User = Depends(get_current_user)):
    """Fetch latest unread notifications for the notification panel."""
    res = await firestore_mcp.query_collection(
        "notifications",
        order_by="-created_at",
        limit=20
    )
    notifications = res.get("data", [])
    return {"notifications": notifications, "unread_count": sum(1 for n in notifications if n.get("status") == "unread")}

@router.patch("/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read."""
    await firestore_mcp.update_document("notifications", notif_id, {"status": "read"})
    return {"success": True}
