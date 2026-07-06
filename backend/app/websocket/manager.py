import json
import structlog
from typing import Dict, List
from fastapi import WebSocket

logger = structlog.get_logger(__name__)

class ConnectionManager:
    """Manages active WebSocket connections for real-time dashboard events."""
    def __init__(self):
        # Maps room names (e.g. 'dashboard', 'incidents', 'missions') to list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, room: str) -> None:
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
        logger.debug("websocket_connected", room=room, active_count=len(self.active_connections[room]))
        
    def disconnect(self, websocket: WebSocket, room: str) -> None:
        if room in self.active_connections and websocket in self.active_connections[room]:
            self.active_connections[room].remove(websocket)
            logger.debug("websocket_disconnected", room=room, active_count=len(self.active_connections[room]))
            
    async def send_personal(self, websocket: WebSocket, message: dict) -> None:
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.warning("failed_to_send_personal_websocket", error=str(e))
            
    async def broadcast(self, room: str, message: dict) -> None:
        if room not in self.active_connections:
            return
            
        disconnected = []
        for connection in self.active_connections[room]:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.warning("failed_to_send_broadcast_websocket", room=room, error=str(e))
                disconnected.append(connection)
                
        # Clean up stale connections
        for conn in disconnected:
            self.disconnect(conn, room)
            
    async def broadcast_all(self, message: dict) -> None:
        for room in self.active_connections.keys():
            await self.broadcast(room, message)
            
    # Helper wrappers for specific AegisAI business events
    async def broadcast_incident_created(self, incident: dict) -> None:
        await self.broadcast("incidents", {
            "event": "incident_created",
            "data": incident
        })
        await self.broadcast("dashboard", {
            "event": "incident_created",
            "data": incident
        })
        
    async def broadcast_mission_updated(self, mission: dict) -> None:
        await self.broadcast("missions", {
            "event": "mission_updated",
            "data": mission
        })
        await self.broadcast("dashboard", {
            "event": "mission_updated",
            "data": mission
        })
        
    async def broadcast_agent_progress(self, agent_name: str, status: str, data: dict) -> None:
        await self.broadcast("dashboard", {
            "event": "agent_progress",
            "agent": agent_name,
            "status": status,
            "data": data
        })
        
    async def broadcast_notification_sent(self, notification: dict) -> None:
        await self.broadcast("dashboard", {
            "event": "notification_sent",
            "data": notification
        })

manager = ConnectionManager()
