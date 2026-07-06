"""
AegisAI FastAPI Backend Entry Point.
Coordinates REST routers, WebSocket rooms, rate limits, exception wrappers, and logs.
"""

import time
from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.core.exceptions import AegisException
from app.core.middleware import RequestLoggingMiddleware, limiter
from app.api.v1.router import api_router
from app.websocket.manager import manager
from app.core.database import get_db

# Configure Structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer() if not settings.debug else structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Sequence
    logger.info(
        "Starting AegisAI backend service",
        version=settings.app_version,
        environment=settings.environment,
        db_mode=settings.db_mode,
        gemini_available=settings.gemini_available
    )
    
    # Initialize DB client singleton on startup to confirm credentials
    try:
        db = get_db()
        logger.info("Database client connection confirmed successfully")
    except Exception as e:
        logger.critical("Database initialization failed", error=str(e))
        
    yield
    
    # Shutdown Sequence
    logger.info("Stopping AegisAI backend service")

# Initialize FastAPI App
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AegisAI Multi-Agent Disaster Management Platform API",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Setup SlowAPI state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom Middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(AegisException)
async def aegis_exception_handler(request: Request, exc: AegisException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(p) for p in err["loc"]])
        errors.append(f"[{loc}]: {err['msg']} (type={err['type']})")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors, "error_code": "VALIDATION_ERROR"}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_system_exception", error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal system server error occurred", "error_code": "INTERNAL_SERVER_ERROR"}
    )

# REST Router Mount
app.include_router(api_router, prefix="/api/v1")

# WebSocket Endpoint Room Management
@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            # Sockets can receive events or listen for heartbeats
            data = await websocket.receive_text()
            # Echo heartbeats
            await manager.send_personal(websocket, {"event": "ping", "data": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
    except Exception as e:
        logger.warning("websocket_exception_encountered", room=room, error=str(e))
        manager.disconnect(websocket, room)

# Core System Health Endpoint
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "ai_available": settings.gemini_available,
        "db_mode": settings.db_mode,
        "notifications_mode": settings.notifications_mode,
        "timestamp": time.time()
    }
