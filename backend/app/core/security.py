from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ForbiddenError

import bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": int(expire.timestamp()), "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(data: dict) -> str:
    """Create a signed JWT refresh token with longer expiry."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": int(expire.timestamp()), "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode a JWT token. Raises UnauthorizedError on failure."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != token_type:
            raise UnauthorizedError(detail="Invalid token type")
        return payload
    except JWTError as e:
        raise UnauthorizedError(detail=f"Token validation failed: {str(e)}")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """FastAPI dependency: extract and validate the current user from JWT."""
    from app.core.database import get_db
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError(detail="Invalid token: missing user ID")
    db = get_db()
    user_data = await db.get_document("users", user_id)
    if not user_data:
        raise UnauthorizedError(detail="User not found")
    from app.models.user import User
    return User(**user_data)

async def get_current_user_optional(token: Annotated[Optional[str], Depends(oauth2_scheme_optional)]):
    """FastAPI dependency: optionally extract current user (returns None if not authenticated)."""
    if not token:
        return None
    try:
        return await get_current_user(token)
    except Exception:
        return None

def require_role(allowed_roles: list[str]):
    """FastAPI dependency factory: enforce Role-Based Access Control."""
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role.value not in allowed_roles:
            raise ForbiddenError(
                detail=f"Access denied. Required role(s): {allowed_roles}. Your role: {current_user.role.value}"
            )
        return current_user
    return role_checker
