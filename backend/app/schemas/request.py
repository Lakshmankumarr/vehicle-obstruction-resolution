"""
Obstruction resolution request schemas.
Fixes:
- Section 99 Issue 28: Persists message field
- Section 99 Issue 29: Normalizes vehicle plate upon request creation
- Includes ETA, live status, response actions, and history schemas
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.models.request import RequestStatus, ResponseType
from app.utils.vehicle_validation import normalize_vehicle_number, mask_vehicle_number


class CreateRequestRequest(BaseModel):
    """Schema for initiating an obstruction resolution call request."""
    targetVehicle: str = Field(..., min_length=4, max_length=20, description="License plate of blocking vehicle")
    message: Optional[str] = Field("Vehicle is blocking access/driveway, please move it.", max_length=500)
    isEmergency: Optional[bool] = Field(False, description="Emergency priority flag")

    @field_validator("targetVehicle")
    @classmethod
    def clean_target(cls, v: str) -> str:
        clean = normalize_vehicle_number(v)
        if not clean:
            raise ValueError("Target vehicle plate cannot be empty")
        return clean


class CreateRequestResponse(BaseModel):
    """Response schema upon request creation."""
    success: bool
    requestId: UUID
    maskedTargetVehicle: str
    status: str
    expiresAt: datetime
    message: str


class RespondRequestRequest(BaseModel):
    """Schema for blocking vehicle owner's response."""
    requestId: UUID
    response: ResponseType = Field(..., description="ON_MY_WAY, CANNOT_MOVE, KEYS_WITH_GUARD, MESSAGE")
    responseMessage: Optional[str] = Field(None, max_length=500)
    etaMinutes: Optional[int] = Field(None, ge=1, le=120, description="Estimated minutes to move vehicle")


class RequestActionResponse(BaseModel):
    """Response returned upon resolving, responding, or cancelling."""
    success: bool
    requestId: UUID
    status: str
    message: str


class RequestDetailResponse(BaseModel):
    """Comprehensive request detail schema."""
    id: UUID
    requesterId: UUID
    targetUserId: UUID
    maskedTargetVehicle: str
    status: str
    message: Optional[str] = None
    response: Optional[str] = None
    responseMessage: Optional[str] = None
    etaMinutes: Optional[int] = None
    createdAt: datetime
    expiresAt: datetime
    respondedAt: Optional[datetime] = None
    resolvedAt: Optional[datetime] = None
    isRequester: bool = False
    isTarget: bool = False
    remainingSeconds: int = 0
    formattedCreatedIST: Optional[str] = None


class RequestHistoryResponse(BaseModel):
    """List of sent/received requests."""
    success: bool
    sent: List[RequestDetailResponse]
    received: List[RequestDetailResponse]
    total: int
