from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models.emergency import GeoPoint

class ResourceType(str, Enum):
    food = "food"
    water = "water"
    medicine = "medicine"
    blankets = "blankets"
    fuel = "fuel"
    medical_kits = "medical_kits"
    rescue_equipment = "rescue_equipment"

class ShelterStatus(str, Enum):
    open = "open"
    full = "full"
    closed = "closed"

class HospitalStatus(str, Enum):
    operational = "operational"
    limited = "limited"
    overwhelmed = "overwhelmed"
    closed = "closed"

class Shelter(BaseModel):
    id: str
    name: str
    location: GeoPoint
    address: str
    total_capacity: int
    current_occupancy: int
    amenities: List[str]
    contact: Optional[str] = None
    status: ShelterStatus
    distance_km: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Hospital(BaseModel):
    id: str
    name: str
    location: GeoPoint
    address: str
    emergency_capacity: int
    available_beds: int
    specialties: List[str]
    contact: Optional[str] = None
    status: HospitalStatus
    distance_km: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Resource(BaseModel):
    id: str
    type: ResourceType
    quantity: int
    unit: str
    location: GeoPoint
    warehouse_name: str
    allocated_to: Optional[str] = None
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)
