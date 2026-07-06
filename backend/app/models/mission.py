from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class MissionStatus(str, Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    failed = "failed"

class MissionPriority(int, Enum):
    critical = 1
    high = 2
    medium = 3
    low = 4

class TeamMember(BaseModel):
    id: str
    name: str
    role: str
    contact: str

class MissionStep(BaseModel):
    order: int
    description: str
    status: str  # pending, active, completed
    completed_at: Optional[datetime] = None

class Mission(BaseModel):
    id: str
    incident_id: str
    status: MissionStatus
    priority: MissionPriority
    title: str
    description: str
    rescue_steps: List[MissionStep] = []
    assigned_teams: List[TeamMember] = []
    shelter_id: Optional[str] = None
    hospital_id: Optional[str] = None
    resources_allocated: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class MissionUpdate(BaseModel):
    status: Optional[MissionStatus] = None
    notes: Optional[str] = None
