"""
Notification and device token registration endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import RegisterDeviceRequest, RegisterDeviceResponse
from app.services.device_token_service import device_token_service

router = APIRouter()


@router.post("/device-token", response_model=RegisterDeviceResponse)
def register_device_token(
    req: RegisterDeviceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registers or updates caller's mobile device push notification token."""
    device_token_service.register_token(
        db=db,
        user_id=current_user.id,
        token=req.token,
        device_type=req.deviceType
    )
    return RegisterDeviceResponse(
        success=True,
        message="Device token registered successfully."
    )


@router.delete("/device-token/{token}", response_model=RegisterDeviceResponse)
def unregister_device_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivates a device token upon logout."""
    device_token_service.deactivate_token(db=db, token=token)
    return RegisterDeviceResponse(
        success=True,
        message="Device token unregistered successfully."
    )

@router.post("/toggle-device-token", response_model=RegisterDeviceResponse)
def toggle_device_token(
    req: RegisterDeviceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggles a device token's active state for the authenticated user."""
    device_token_service.toggle_token(
        db=db,
        user_id=current_user.id,
        token=req.token,
        enabled=req.enabled
    )
    return RegisterDeviceResponse(
        success=True,
        message="Device token toggled successfully."
    )
