import time
import structlog
from abc import ABC
from typing import Any, Callable
from pydantic import BaseModel, Field
from datetime import datetime

logger = structlog.get_logger(__name__)

class MCPToolResult(BaseModel):
    """Standardized wrapper for all MCP server tool invocation results."""
    success: bool
    data: Any = None
    error: str | None = None
    tool_name: str = ""
    server_name: str = ""
    duration_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "tool_name": self.tool_name,
            "server_name": self.server_name,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp
        }

class BaseMCPServer(ABC):
    """Base class for all AegisAI MCP Servers."""
    name: str = "base-mcp"
    description: str = "Base MCP Server"
    
    def __init__(self):
        self._logger = structlog.get_logger(self.name)
        
    async def _execute_tool(self, tool_name: str, tool_fn: Callable, **kwargs) -> MCPToolResult:
        """Helper to run a tool function with standard logging, timing, and error handling."""
        start_time = time.perf_counter()
        try:
            result = await tool_fn(**kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._logger.debug(
                "tool_execution_success",
                tool=tool_name,
                duration_ms=round(duration_ms, 2)
            )
            return MCPToolResult(
                success=True,
                data=result,
                tool_name=tool_name,
                server_name=self.name,
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self._logger.error(
                "tool_execution_failed",
                tool=tool_name,
                error=str(e),
                duration_ms=round(duration_ms, 2)
            )
            return MCPToolResult(
                success=False,
                error=str(e),
                tool_name=tool_name,
                server_name=self.name,
                duration_ms=duration_ms
            )
