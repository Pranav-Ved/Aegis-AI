from typing import Optional
from fastapi import HTTPException, status

class AegisException(HTTPException):
    """Base exception for all AegisAI application errors."""
    def __init__(self, status_code: int, detail: str, error_code: Optional[str] = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code or f"AEGIS_{status_code}"

class NotFoundError(AegisException):
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail, error_code)

class UnauthorizedError(AegisException):
    def __init__(self, detail: str = "Authentication required", error_code: str = "UNAUTHORIZED"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, error_code)

class ForbiddenError(AegisException):
    def __init__(self, detail: str = "Insufficient permissions", error_code: str = "FORBIDDEN"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail, error_code)

class ValidationError(AegisException):
    def __init__(self, detail: str = "Validation failed", error_code: str = "VALIDATION_ERROR"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, error_code)

class RateLimitError(AegisException):
    def __init__(self, detail: str = "Too many requests", error_code: str = "RATE_LIMITED"):
        super().__init__(status.HTTP_429_TOO_MANY_REQUESTS, detail, error_code)

class AgentError(AegisException):
    def __init__(self, detail: str, agent_name: str, error_code: str = "AGENT_ERROR"):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, error_code)
        self.agent_name = agent_name

class MCPToolError(AegisException):
    def __init__(self, detail: str, tool_name: str, server_name: str, error_code: str = "MCP_TOOL_ERROR"):
        super().__init__(status.HTTP_502_BAD_GATEWAY, detail, error_code)
        self.tool_name = tool_name
        self.server_name = server_name

class DatabaseError(AegisException):
    def __init__(self, detail: str = "Database operation failed", error_code: str = "DATABASE_ERROR"):
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, detail, error_code)

class ExternalServiceError(AegisException):
    def __init__(self, detail: str, service_name: str, error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(status.HTTP_502_BAD_GATEWAY, detail, error_code)
        self.service_name = service_name
