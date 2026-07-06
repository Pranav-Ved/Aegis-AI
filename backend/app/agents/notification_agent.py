import structlog
from typing import List, Dict, Any

from app.core.config import settings
from app.mcp_servers.notifications_mcp import notifications_mcp
from app.mcp_servers.logging_mcp import logging_mcp

try:
    from google.adk.agents import Agent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None

logger = structlog.get_logger(__name__)

# Core emergency response agencies notified on critical alerts
EMERGENCY_CONTACTS = [
    {"name": "NDRF Mumbai Command", "phone": "+912224140000", "email": "ndrf-mumbai@aegisai.example.com", "role": "rescue"},
    {"name": "BMC Emergency Control", "phone": "+912224640000", "email": "bmc-control@aegisai.example.com", "role": "municipal"},
    {"name": "Mumbai Police Control", "phone": "+912222620111", "email": "police-control@aegisai.example.com", "role": "law_enforcement"},
    {"name": "State Disaster Management Authority", "phone": "+912222026301", "email": "sdma-hq@aegisai.example.com", "role": "government"}
]

async def notify_emergency_contacts(
    incident_id: str,
    severity: str,
    incident_type: str,
    description: str,
    location_address: str
) -> dict:
    """Send high-priority alerts to emergency agencies via Notifications MCP."""
    clean_desc = f"{incident_type.upper()} in progress at {location_address}. Brief: {description}"
    
    alert_summary = await notifications_mcp.send_emergency_alert(
        incident_id=incident_id,
        severity=severity,
        description=clean_desc,
        contacts=EMERGENCY_CONTACTS
    )
    
    contacts_notified = alert_summary.get("data", {}).get("contacts_notified", 0)
    sms_sent = alert_summary.get("data", {}).get("sms_sent", 0)
    email_sent = alert_summary.get("data", {}).get("email_sent", 0)
    
    await logging_mcp.log_notification(
        notification_type="emergency_alert",
        provider=notifications_mcp.sms_mode + "_" + notifications_mcp.email_mode,
        recipients=[c["name"] for c in EMERGENCY_CONTACTS],
        status="sent",
        incident_id=incident_id
    )
    
    return {
        "success": True,
        "contacts_notified": contacts_notified,
        "sms_sent": sms_sent,
        "email_sent": email_sent,
        "provider_mode": f"SMS: {notifications_mcp.sms_mode} | Email: {notifications_mcp.email_mode}"
    }

async def notify_citizens_in_area(area_description: str, safety_message: str) -> dict:
    """Simulates broadcasting evacuation/weather warning logs to public citizens in the area."""
    # In Mock mode, log this event clearly.
    print(f"\n📢 [CITIZEN BROADCAST] Area: {area_description}\nWarning: {safety_message}\n")
    return {
        "success": True,
        "message": f"Broadcast logged for area: {area_description}",
        "status": "mock"
    }

NOTIFICATION_INSTRUCTION = """
You are the AegisAI Notification Agent. Your role is to alert responders and warning citizens about disaster events.
You call the notifications-mcp to send SMS alerts and email bulletins.
"""

notification_agent = None
if ADK_AVAILABLE and settings.gemini_available:
    notification_agent = Agent(
        name="notification",
        model="gemini-2.0-flash",
        instruction=NOTIFICATION_INSTRUCTION,
        tools=[notify_emergency_contacts, notify_citizens_in_area]
    )

async def run_notification(
    incident_id: str,
    incident_data: dict,
    detection_result: dict,
    rescue_plan: dict
) -> dict:
    inc_type = detection_result.get("incident_type", "flood")
    severity = detection_result.get("severity", "medium")
    desc = incident_data.get("description", "")
    
    # We estimate location address from coordinates or default
    loc_addr = incident_data.get("location", {}).get("address") or "Dharavi Sector 3, Mumbai"
    
    # 1. Alert responders
    alerts = await notify_emergency_contacts(incident_id, severity, inc_type, desc, loc_addr)
    
    # 2. Alert citizens if critical
    if severity in ("critical", "high"):
        msg = f"AegisAI Alert: {inc_type.upper()} detected. Avoid low areas. Shelter in place or evacuate to recommended relief camp."
        await notify_citizens_in_area(loc_addr, msg)
        
    return {
        "agent": "notification",
        "alerts_dispatched": alerts
    }
