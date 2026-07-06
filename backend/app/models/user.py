from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class UserRole(str, Enum):
    citizen = "citizen"
    volunteer = "volunteer"
    ngo = "ngo"
    government = "government"
    admin = "admin"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.citizen

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    role: UserRole
    created_at: datetime
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: User

class TokenData(BaseModel):
    user_id: str
    role: str
    exp: Optional[int] = None
