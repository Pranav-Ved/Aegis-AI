from typing import List, Optional
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.resource import Shelter, Hospital, Resource
from app.services.resource_service import ResourceService
from app.mcp_servers.firestore_mcp import firestore_mcp
from app.websocket.manager import manager
from app.core.exceptions import NotFoundError

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/shelters", response_model=List[Shelter])
async def get_shelters(
    lat: Optional[float] = Query(None, description="Latitude for distance calculations"),
    lng: Optional[float] = Query(None, description="Longitude for distance calculations"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """List relief camps, optionally sorted by distance to coordinates."""
    service = ResourceService(firestore_mcp)
    return await service.get_shelters(lat, lng)

@router.get("/shelters/{shelter_id}", response_model=Shelter)
async def get_shelter(shelter_id: str, current_user: Optional[User] = Depends(get_current_user)):
    """Retrieve details for a specific shelter."""
    res = await firestore_mcp.get_document("shelters", shelter_id)
    doc = res.get("data")
    if not doc:
        raise NotFoundError(f"Shelter {shelter_id} not found")
    return Shelter(**doc)

@router.patch("/shelters/{shelter_id}/occupancy", response_model=Shelter)
async def update_shelter_occupancy(
    shelter_id: str,
    occupancy_update: dict,  # e.g. {"delta": 5}
    current_user: User = Depends(require_role(["volunteer", "ngo", "government", "admin"]))
):
    """
    Adjust shelter occupied count (+ or - delta).
    Restricted to Responders and Admins.
    """
    delta = occupancy_update.get("delta", 0)
    service = ResourceService(firestore_mcp)
    updated = await service.update_shelter_occupancy(shelter_id, delta)
    
    # Broadcast to dashboard
    await manager.broadcast("dashboard", {
        "event": "shelter_updated",
        "data": updated.model_dump()
    })
    
    return updated

@router.get("/hospitals", response_model=List[Hospital])
async def get_hospitals(
    lat: Optional[float] = Query(None, description="Latitude for distance calculations"),
    lng: Optional[float] = Query(None, description="Longitude for distance calculations"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """List medical facilities with bed counts."""
    service = ResourceService(firestore_mcp)
    return await service.get_hospitals(lat, lng)

@router.get("/hospitals/{hospital_id}", response_model=Hospital)
async def get_hospital(hospital_id: str, current_user: Optional[User] = Depends(get_current_user)):
    """Retrieve details for a specific hospital."""
    res = await firestore_mcp.get_document("hospitals", hospital_id)
    doc = res.get("data")
    if not doc:
        raise NotFoundError(f"Hospital {hospital_id} not found")
    return Hospital(**doc)

@router.patch("/hospitals/{hospital_id}/beds", response_model=Hospital)
async def update_hospital_beds(
    hospital_id: str,
    beds_update: dict,  # e.g. {"available_beds": 15}
    current_user: User = Depends(require_role(["government", "admin"]))
):
    """
    Set available emergency bed count.
    Restricted to Government Officials and Admins.
    """
    available_beds = beds_update.get("available_beds")
    if available_beds is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing available_beds field")
        
    service = ResourceService(firestore_mcp)
    updated = await service.update_hospital_beds(hospital_id, available_beds)
    
    # Broadcast to dashboard
    await manager.broadcast("dashboard", {
        "event": "hospital_updated",
        "data": updated.model_dump()
    })
    
    return updated

@router.get("/inventory")
async def get_inventory(current_user: User = Depends(get_current_user)):
    """Get active resource warehouse stock grouped by category."""
    service = ResourceService(firestore_mcp)
    return await service.get_resource_inventory()

@router.get("/warehouses")
async def get_warehouses(current_user: User = Depends(get_current_user)):
    """Get all warehouses."""
    res = await firestore_mcp.query_collection("warehouses", limit=100)
    return res.get("data", [])

@router.patch("/warehouses/{warehouse_id}")
async def update_warehouse(
    warehouse_id: str,
    update_data: dict,
    current_user: User = Depends(require_role(["government", "admin"]))
):
    """Update warehouse inventory quantities."""
    res = await firestore_mcp.get_document("warehouses", warehouse_id)
    doc = res.get("data")
    if not doc:
        raise NotFoundError(f"Warehouse {warehouse_id} not found")
    await firestore_mcp.update_document("warehouses", warehouse_id, update_data)
    updated_res = await firestore_mcp.get_document("warehouses", warehouse_id)
    updated = updated_res.get("data", {})
    await manager.broadcast("dashboard", {"event": "warehouse_updated", "data": updated})
    return updated

@router.get("/vehicles")
async def get_vehicles(current_user: User = Depends(get_current_user)):
    """Get all vehicles."""
    res = await firestore_mcp.query_collection("vehicles", limit=100)
    return res.get("data", [])

@router.patch("/vehicles/{vehicle_id}")
async def update_vehicle(
    vehicle_id: str,
    update_data: dict,
    current_user: User = Depends(require_role(["government", "admin"]))
):
    """Update vehicle status/assignment."""
    res = await firestore_mcp.get_document("vehicles", vehicle_id)
    doc = res.get("data")
    if not doc:
        raise NotFoundError(f"Vehicle {vehicle_id} not found")
    await firestore_mcp.update_document("vehicles", vehicle_id, update_data)
    updated_res = await firestore_mcp.get_document("vehicles", vehicle_id)
    updated = updated_res.get("data", {})
    await manager.broadcast("dashboard", {"event": "vehicle_updated", "data": updated})
    return updated

@router.get("/volunteers")
async def get_volunteers(current_user: User = Depends(get_current_user)):
    """Get all volunteers."""
    res = await firestore_mcp.query_collection("volunteers", limit=100)
    return res.get("data", [])

@router.patch("/volunteers/{volunteer_id}")
async def update_volunteer(
    volunteer_id: str,
    update_data: dict,
    current_user: User = Depends(require_role(["government", "admin"]))
):
    """Update volunteer availability/assignment."""
    res = await firestore_mcp.get_document("volunteers", volunteer_id)
    doc = res.get("data")
    if not doc:
        raise NotFoundError(f"Volunteer {volunteer_id} not found")
    await firestore_mcp.update_document("volunteers", volunteer_id, update_data)
    updated_res = await firestore_mcp.get_document("volunteers", volunteer_id)
    updated = updated_res.get("data", {})
    return updated

@router.patch("/shelters/{shelter_id}")
async def update_shelter(
    shelter_id: str,
    update_data: dict,
    current_user: User = Depends(require_role(["volunteer", "ngo", "government", "admin"]))
):
    """Update shelter name, capacity, status, or address."""
    res = await firestore_mcp.get_document("shelters", shelter_id)
    doc = res.get("data")
    if not doc:
        raise NotFoundError(f"Shelter {shelter_id} not found")
    await firestore_mcp.update_document("shelters", shelter_id, update_data)
    updated_res = await firestore_mcp.get_document("shelters", shelter_id)
    updated = updated_res.get("data", {})
    await manager.broadcast("dashboard", {"event": "shelter_updated", "data": updated})
    return updated

@router.patch("/hospitals/{hospital_id}")
async def update_hospital(
    hospital_id: str,
    update_data: dict,
    current_user: User = Depends(require_role(["government", "admin"]))
):
    """Update hospital name, capacity, or status."""
    res = await firestore_mcp.get_document("hospitals", hospital_id)
    doc = res.get("data")
    if not doc:
        raise NotFoundError(f"Hospital {hospital_id} not found")
    await firestore_mcp.update_document("hospitals", hospital_id, update_data)
    updated_res = await firestore_mcp.get_document("hospitals", hospital_id)
    updated = updated_res.get("data", {})
    await manager.broadcast("dashboard", {"event": "hospital_updated", "data": updated})
    return updated
