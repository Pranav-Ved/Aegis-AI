import structlog
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.mcp_servers.base import BaseMCPServer
from app.core.config import settings
from app.core.database import get_db

logger = structlog.get_logger(__name__)

class MockNotificationService:
    """Logs notifications to console when real API keys are not provided."""
    def send_sms(self, to: str, message: str) -> dict:
        print(f"\n📱 [MOCK SMS] To: {to}\nMessage: {message}\n")
        logger.info("mock_sms_logged", to=to, length=len(message))
        return {
            "message_id": f"mock_sms_{datetime.utcnow().timestamp()}",
            "status": "mock",
            "provider": "mock",
            "to": to,
            "timestamp": datetime.utcnow().isoformat()
        }

    def send_email(self, to: str, subject: str, body: str) -> dict:
        print(f"\n📧 [MOCK EMAIL] To: {to}\nSubject: {subject}\nBody: {body}\n")
        logger.info("mock_email_logged", to=to, subject=subject)
        return {
            "message_id": f"mock_email_{datetime.utcnow().timestamp()}",
            "status": "mock",
            "provider": "mock",
            "to": to,
            "timestamp": datetime.utcnow().isoformat()
        }


class TwilioSMSService:
    """Twilio SMS integration."""
    def __init__(self):
        from twilio.rest import Client
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    def send_sms(self, to: str, message: str) -> dict:
        try:
            resp = self.client.messages.create(
                body=message,
                from_=settings.twilio_from_number,
                to=to
            )
            return {
                "message_id": resp.sid,
                "status": "sent",
                "provider": "twilio",
                "to": to,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("twilio_sms_error", error=str(e))
            raise e


class SendGridEmailService:
    """SendGrid Email integration."""
    def __init__(self):
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        self.client = SendGridAPIClient(settings.sendgrid_api_key)
        self.MailClass = Mail

    def send_email(self, to: str, subject: str, body: str) -> dict:
        try:
            message = self.MailClass(
                from_email=settings.sendgrid_from_email,
                to_emails=to,
                subject=subject,
                plain_text_content=body
            )
            resp = self.client.send(message)
            return {
                "message_id": resp.headers.get("X-Message-Id", "sg_unknown"),
                "status": "sent",
                "provider": "sendgrid",
                "to": to,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("sendgrid_email_error", error=str(e))
            raise e


class NotificationsMCPServer(BaseMCPServer):
    name = "notifications-mcp"
    description = "Provides SMS, Email, and bulk emergency alert dispatching services"

    def __init__(self):
        super().__init__()
        # Initialize fallback services
        self.mock_service = MockNotificationService()
        self.sms_service = None
        self.email_service = None
        
        # Check for Twilio keys
        if settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_from_number:
            try:
                self.sms_service = TwilioSMSService()
                self._logger.info("Twilio SMS service initialized successfully")
            except Exception as e:
                self._logger.warning("Failed to initialize Twilio SMS service, using mock", error=str(e))
                
        # Check for SendGrid keys
        if settings.sendgrid_api_key:
            try:
                self.email_service = SendGridEmailService()
                self._logger.info("SendGrid Email service initialized successfully")
            except Exception as e:
                self._logger.warning("Failed to initialize SendGrid Email service, using mock", error=str(e))

    @property
    def sms_mode(self) -> str:
        return "twilio" if self.sms_service else "mock"

    @property
    def email_mode(self) -> str:
        return "sendgrid" if self.email_service else "mock"

    async def send_sms(self, to: str, message: str, priority: str = "normal") -> dict:
        """Send a single SMS message."""
        async def _run():
            if self.sms_service:
                return self.sms_service.send_sms(to, message)
            return self.mock_service.send_sms(to, message)
        res = await self._execute_tool("send_sms", _run)
        return res.to_dict()

    async def send_bulk_sms(self, recipients: List[str], message: str) -> dict:
        """Send SMS to multiple numbers."""
        async def _run():
            results = []
            sent = 0
            failed = 0
            for number in recipients:
                try:
                    if self.sms_service:
                        res = self.sms_service.send_sms(number, message)
                    else:
                        res = self.mock_service.send_sms(number, message)
                    results.append(res)
                    sent += 1
                except Exception as e:
                    results.append({"to": number, "status": "failed", "error": str(e)})
                    failed += 1
            return {"total": len(recipients), "sent": sent, "failed": failed, "results": results}
        res = await self._execute_tool("send_bulk_sms", _run)
        return res.to_dict()

    async def send_email(self, to: str, subject: str, body: str) -> dict:
        """Send a single Email."""
        async def _run():
            if self.email_service:
                return self.email_service.send_email(to, subject, body)
            return self.mock_service.send_email(to, subject, body)
        res = await self._execute_tool("send_email", _run)
        return res.to_dict()

    async def send_bulk_email(self, recipients: List[str], subject: str, body: str) -> dict:
        """Send Emails to multiple recipients."""
        async def _run():
            results = []
            sent = 0
            failed = 0
            for email in recipients:
                try:
                    if self.email_service:
                        res = self.email_service.send_email(email, subject, body)
                    else:
                        res = self.mock_service.send_email(email, subject, body)
                    results.append(res)
                    sent += 1
                except Exception as e:
                    results.append({"to": email, "status": "failed", "error": str(e)})
                    failed += 1
            return {"total": len(recipients), "sent": sent, "failed": failed, "results": results}
        res = await self._execute_tool("send_bulk_email", _run)
        return res.to_dict()

    async def send_emergency_alert(self, incident_id: str, severity: str, description: str, contacts: List[dict]) -> dict:
        """Orchestrate and send immediate alert reports (SMS + Email) to responders."""
        async def _run():
            sms_sent = 0
            email_sent = 0
            failures = 0
            
            sms_msg = f"🚨 AEGIS-ALERT: {severity.upper()} emergency reported (ID: {incident_id}). Description: {description[:100]}..."
            email_subject = f"🛡️ AegisAI Emergency Response Notification [{severity.upper()}]"
            email_body = (
                f"🛡️ AegisAI Disaster Alert System\n"
                f"---------------------------------------\n"
                f"Incident ID: {incident_id}\n"
                f"Severity Level: {severity.upper()}\n"
                f"Status: Active operation requested\n"
                f"Description: {description}\n"
                f"Timestamp: {datetime.utcnow().isoformat()} UTC\n\n"
                f"Please log in to the dashboard at {settings.frontend_url}/dashboard/alerts to coordinate resource deployment."
            )
            
            for contact in contacts:
                # Send SMS
                phone = contact.get("phone")
                if phone:
                    try:
                        if self.sms_service:
                            self.sms_service.send_sms(phone, sms_msg)
                        else:
                            self.mock_service.send_sms(phone, sms_msg)
                        sms_sent += 1
                    except Exception:
                        failures += 1
                        
                # Send Email
                email = contact.get("email")
                if email:
                    try:
                        if self.email_service:
                            self.email_service.send_email(email, email_subject, email_body)
                        else:
                            self.mock_service.send_email(email, email_subject, email_body)
                        email_sent += 1
                    except Exception:
                        failures += 1
                        
            # Store notification log in DB
            db_log = {
                "incident_id": incident_id,
                "message": sms_msg,
                "sms_count": sms_sent,
                "email_count": email_sent,
                "failure_count": failures,
                "provider": "twilio_sendgrid" if (self.sms_service or self.email_service) else "mock",
                "sent_at": datetime.utcnow().isoformat()
            }
            db = get_db()
            await db.create_document("notifications", db_log)
            
            return {
                "incident_id": incident_id,
                "contacts_notified": len(contacts),
                "sms_sent": sms_sent,
                "email_sent": email_sent,
                "failures": failures
            }
            
        res = await self._execute_tool("send_emergency_alert", _run)
        return res.to_dict()

notifications_mcp = NotificationsMCPServer()
