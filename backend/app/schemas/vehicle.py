"""
Vehicle schemas for adding vehicles, management, and privacy-preserving lookup.
Fixes:
- Section 99 Issue 13: Vehicle model fully supported
- Section 99 Issue 14: Multiple vehicle management
- Section 99 Issue 15: Target vehicle number masked for privacy
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.utils.vehicle_validation import normalize_vehicle_number, mask_vehicle_number, validate_vehicle_format


class VehicleCreate(BaseModel):
    """Schema for adding a vehicle to user account."""
    vehicleNumber: str = Field(..., min_length=4, max_length=20, description="Indian vehicle license plate")
    nickname: Optional[str] = Field(None, max_length=50, description="e.g. My Blue Creta")
    vehicleType: Optional[str] = Field("CAR", description="CAR, TWO_WHEELER, SUV, COMMERCIAL")
    isPrimary: Optional[bool] = Field(False, description="Set as primary vehicle")

    @field_validator("vehicleNumber")
    @classmethod
    def clean_plate(cls, v: str) -> str:
        clean = normalize_vehicle_number(v)
        if not validate_vehicle_format(clean):
            raise ValueError("Invalid vehicle plate format. Example: DL01AB1234 or 22BH1234AA")
        return clean


class VehicleResponse(BaseModel):
    """Vehicle details response."""
    id: UUID
    vehicleNumber: str
    maskedNumber: str
    nickname: Optional[str] = None
    vehicleType: str
    isPrimary: bool
    isActive: bool
    registeredAt: datetime

    class Config:
        from_attributes = True


class VehicleIdentifyRequest(BaseModel):
    """Request schema for vehicle identification lookup."""
    vehicleNumber: Optional[str] = Field(None, description="Manual vehicle number")
    image: Optional[str] = Field(None, description="Base64 encoded image")


class VehicleIdentifyResponse(BaseModel):
    """
    Privacy-preserving response for vehicle identification.
    Never exposes target owner identity, phone number, or unmasked plate to unauthorized viewers.
    """
    success: bool
    maskedVehicleNumber: str
    targetVehiclePlate: str  # Normalized plate for backend request initiation
    isRegistered: bool
    canSendRequest: bool
    confidence: Optional[float] = None
    message: str
    cooldownRemainingSeconds: Optional[int] = 0
