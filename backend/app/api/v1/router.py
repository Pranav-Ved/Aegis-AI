from fastapi import APIRouter
from app.api.v1 import auth, emergency, dashboard, missions, resources, reports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(emergency.router, prefix="/incidents", tags=["Emergency Reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Operational Dashboard"])
api_router.include_router(missions.router, prefix="/missions", tags=["Rescue Missions"])
api_router.include_router(resources.router, prefix="/resources", tags=["Facility Supplies"])
api_router.include_router(reports.router, prefix="/reports", tags=["Briefings & Reports"])
