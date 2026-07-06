import uuid
import structlog
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.mcp_servers.base import BaseMCPServer
from app.core.database import get_db

logger = structlog.get_logger(__name__)

class LoggingMCPServer(BaseMCPServer):
    name = "logging-mcp"
    description = "Provides centralized structured logging and audit trailing services"

    def __init__(self):
        super().__init__()
        # Console structured logging config is done globally in main.py, but we keep an in-memory buffer for fast local auditing
        self._buffer: List[Dict[str, Any]] = []

    async def log_event(self, level: str, source: str, message: str, metadata: dict = None) -> dict:
        """Write a structured event log."""
        async def _run():
            log_id = str(uuid.uuid4())
            meta = metadata or {}
            
            # Print to structlog console
            log_fn = getattr(self._logger, level.lower(), self._logger.info)
            log_fn(message, source=source, **meta)
            
            log_entry = {
                "id": log_id,
                "timestamp": datetime.utcnow().isoformat(),
                "level": level.upper(),
                "source": source,
                "message": message,
                "metadata": meta
            }
            
            # Persist in DB
            db = get_db()
            await db.create_document("audit_logs", log_entry, doc_id=log_id)
            
            self._buffer.append(log_entry)
            if len(self._buffer) > 100:
                self._buffer.pop(0) # cap buffer
                
            return {"log_id": log_id, "success": True}
        res = await self._execute_tool("log_event", _run)
        return res.to_dict()

    async def log_agent_action(
        self, 
        agent_name: str, 
        action: str, 
        input_summary: str, 
        output_summary: str, 
        duration_ms: float, 
        success: bool
    ) -> dict:
        """Log a specific ADK Agent execution step."""
        async def _run():
            msg = f"Agent [{agent_name}] executed action [{action}] (success={success})"
            meta = {
                "agent": agent_name,
                "action": action,
                "input_summary": input_summary[:200],
                "output_summary": output_summary[:200],
                "duration_ms": duration_ms,
                "success": success
            }
            return await self.log_event("INFO", f"agent.{agent_name}", msg, meta)
        res = await self._execute_tool("log_agent_action", _run)
        return res.to_dict()

    async def log_error(self, source: str, error: str, traceback_str: str, context: dict = None) -> dict:
        """Log an exception or critical system failure with context."""
        async def _run():
            ctx = context or {}
            meta = {
                "error": error,
                "traceback": traceback_str[:500],
                **ctx
            }
            return await self.log_event("ERROR", source, f"Error encountered in {source}: {error}", meta)
        res = await self._execute_tool("log_error", _run)
        return res.to_dict()

    async def log_notification(self, notification_type: str, provider: str, recipients: List[str], status: str, incident_id: str = None) -> dict:
        """Log notifications dispatched."""
        async def _run():
            msg = f"Dispatched {notification_type} warning alert via {provider} to {len(recipients)} contacts"
            meta = {
                "type": notification_type,
                "provider": provider,
                "recipients_count": len(recipients),
                "status": status,
                "incident_id": incident_id
            }
            return await self.log_event("INFO", "notification_agent", msg, meta)
        res = await self._execute_tool("log_notification", _run)
        return res.to_dict()

    async def get_audit_trail(self, source: Optional[str] = None, level: Optional[str] = None, limit: int = 50, skip: int = 0) -> dict:
        """Fetch audit logs filtered by source or level."""
        async def _run():
            db = get_db()
            filters = []
            if source:
                filters.append({"field": "source", "op": "==", "value": source})
            if level:
                filters.append({"field": "level", "op": "==", "value": level.upper()})
                
            docs = await db.query_collection("audit_logs", filters=filters, limit=1000, order_by="-timestamp")
            paginated = docs[skip:skip + limit]
            return paginated
        res = await self._execute_tool("get_audit_trail", _run)
        return res.to_dict()

logging_mcp = LoggingMCPServer()
