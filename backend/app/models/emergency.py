from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.core.prompt_guard import validate_emergency_text

class IncidentType(str, Enum):
    flood = "flood"
    fire = "fire"
    earthquake = "earthquake"
    cyclone = "cyclone"
    landslide = "landslide"
    building_collapse = "building_collapse"
    tsunami = "tsunami"
    wildfire = "wildfire"
    chemical_leak = "chemical_leak"
    road_accident = "road_accident"
    medical_emergency = "medical_emergency"
    other = "other"

class IncidentSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class IncidentStatus(str, Enum):
    reported = "reported"
    processing = "processing"
    active = "active"
    resolved = "resolved"
    closed = "closed"

class GeoPoint(BaseModel):
    lat: float
    lng: float
    address: Optional[str] = None

class IncidentCreate(BaseModel):
    description: str
    incident_type: Optional[IncidentType] = None
    location: Optional[GeoPoint] = None
    severity_hint: Optional[IncidentSeverity] = None
    media_urls: List[str] = []
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        return validate_emergency_text(v)

class DetectionResult(BaseModel):
    incident_type: IncidentType
    confidence: float
    severity: IncidentSeverity
    description: str
    ai_available: bool = True

class LocationContext(BaseModel):
    address: str
    nearby_shelters: List[Dict[str, Any]]
    nearby_hospitals: List[Dict[str, Any]]
    weather_summary: str
    risk_level: str

class ResourcePlan(BaseModel):
    recommended_shelter: Optional[Dict[str, Any]] = None
    recommended_hospital: Optional[Dict[str, Any]] = None
    resources_allocated: List[Dict[str, Any]] = []
    estimated_arrival_minutes: Optional[int] = None

class RescuePlan(BaseModel):
    priority_level: int
    rescue_steps: List[str]
    team_assignment: Dict[str, Any]
    estimated_completion_hours: float

class Incident(BaseModel):
    id: str
    description: str
    incident_type: Optional[IncidentType] = None
    severity: Optional[IncidentSeverity] = None
    status: IncidentStatus = IncidentStatus.reported
    location: Optional[GeoPoint] = None
    media_urls: List[str] = []
    reported_by: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    
    # Agent response payloads
    detection_result: Optional[DetectionResult] = None
    location_context: Optional[LocationContext] = None
    resource_plan: Optional[ResourcePlan] = None
    rescue_plan: Optional[RescuePlan] = None
    mission_id: Optional[str] = None
    
    # Track which agents have completed execution
    agent_status: Dict[str, str] = {}
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class IncidentListResponse(BaseModel):
    items: List[Incident]
    total: int
    page: int
    limit: int
