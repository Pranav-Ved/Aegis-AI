from datetime import datetime, timedelta
import uuid
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request

from app.core.config import settings
from app.core.security import (
    get_current_user, create_access_token, create_refresh_token,
    hash_password, verify_password, verify_token
)
from app.core.exceptions import UnauthorizedError, ValidationError
from app.core.middleware import limiter
from app.models.user import User, UserCreate, UserLogin, Token, UserRole
from app.mcp_servers.firestore_mcp import firestore_mcp
from app.mcp_servers.logging_mcp import logging_mcp

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_public)
async def register(request: Request, user_data: UserCreate):
    """Register a new citizen, volunteer or NGO account."""
    # Check if user already exists
    user_query = await firestore_mcp.query_collection(
        "users", 
        filters=[{"field": "email", "op": "==", "value": user_data.email}]
    )
    if user_query.get("data"):
        raise ValidationError(detail="Email is already registered")
        
    user_id = f"user_{str(uuid.uuid4())[:8]}"
    hashed_pw = hash_password(user_data.password)
    
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "phone": user_data.phone,
        "role": user_data.role.value,
        "hashed_password": hashed_pw,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await firestore_mcp.create_document("users", new_user, doc_id=user_id)
    await logging_mcp.log_event("INFO", "auth.register", f"User {user_data.email} registered with role {user_data.role.value}")
    
    # Return User schema
    return User(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        phone=user_data.phone,
        role=user_data.role,
        created_at=datetime.fromisoformat(new_user["created_at"])
    )

@router.post("/login", response_model=Token)
@limiter.limit(settings.rate_limit_public)
async def login(request: Request, login_data: UserLogin):
    """Authenticate credentials and issue JWT Access + Refresh Token."""
    user_query = await firestore_mcp.query_collection(
        "users", 
        filters=[{"field": "email", "op": "==", "value": login_data.email}]
    )
    users = user_query.get("data", [])
    if not users:
        raise UnauthorizedError(detail="Invalid email or password credentials")
        
    user_data = users[0]
    if not verify_password(login_data.password, user_data.get("hashed_password", "")):
        raise UnauthorizedError(detail="Invalid email or password credentials")
        
    user = User(**user_data)
    
    token_data = {"sub": user.id, "role": user.role.value, "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    await logging_mcp.log_event("INFO", "auth.login", f"User {user.email} logged in successfully")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Generate a new access token from a valid refresh token."""
    payload = verify_token(refresh_token, token_type="refresh")
    user_id = payload.get("sub")
    role = payload.get("role")
    email = payload.get("email")
    
    if not user_id:
        raise UnauthorizedError(detail="Invalid refresh token payload")
        
    token_data = {"sub": user_id, "role": role, "email": email}
    new_access = create_access_token(token_data)
    
    return {
        "access_token": new_access,
        "token_type": "bearer"
    }

@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve currently logged in profile details."""
    return current_user

@router.get("/demo-login")
async def demo_login():
    """Development helper issuing pre-authorized demo token (Admin/Gov credentials)."""
    if settings.environment not in ("development", "testing"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Demo login is only available in development environment."
        )
        
    token_data = {"sub": "user_admin_001", "role": "admin", "email": "admin@aegisai.com"}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    user = User(
        id="user_admin_001",
        email="admin@aegisai.com",
        name="AegisAI Admin",
        role=UserRole.admin,
        created_at=datetime.utcnow()
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }
