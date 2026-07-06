import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = structlog.get_logger(__name__)

# SlowAPI Limiter Singleton
limiter = Limiter(key_func=get_remote_address)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming HTTP requests with timing details."""
    SKIP_PATHS = {"/health", "/metrics", "/favicon.ico"}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
            
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            client_ip=request.client.host if request.client else "unknown"
        )
        return response
