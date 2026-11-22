"""
API v1 root router aggregating all domain endpoints.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    vehicle,
    request,
    alpr,
    notification,
    report,
    admin,
    health,
    gdpr,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(vehicle.router, prefix="/vehicle", tags=["Vehicles"])
api_router.include_router(request.router, prefix="/request", tags=["Obstruction Requests"])
api_router.include_router(alpr.router, prefix="/alpr", tags=["ALPR Recognition"])
api_router.include_router(notification.router, prefix="/notification", tags=["Push Notifications"])
api_router.include_router(report.router, prefix="/report", tags=["Abuse & Reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin & Moderation"])
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(gdpr.router, prefix="/gdpr", tags=["GDPR Compliance"])
