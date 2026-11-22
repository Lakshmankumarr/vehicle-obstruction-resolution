"""
Authentication request and response schemas for FreeWay Community.
Supports vehicle-based and phone-based registration/login with JWT access + refresh tokens.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from app.utils.vehicle_validation import normalize_vehicle_number, validate_vehicle_format


class RegisterRequest(BaseModel):
    """User registration schema."""
    vehicleNumber: str = Field(..., min_length=4, max_length=20, description="Primary vehicle registration number")
    password: str = Field(..., min_length=6, description="Password")
    phoneNumber: Optional[str] = Field(None, description="Optional phone number")
    name: Optional[str] = Field(None, description="Optional display name")
    deviceToken: Optional[str] = Field(None, description="Optional push device token")
    deviceType: Optional[str] = Field("ANDROID", description="Device platform (ANDROID, IOS, WEB)")

    @field_validator("vehicleNumber")
    @classmethod
    def clean_plate(cls, v: str) -> str:
        clean = normalize_vehicle_number(v)
        if not clean:
            raise ValueError("Vehicle number cannot be empty")
        return clean


class LoginRequest(BaseModel):
    """User login schema (login via vehicle number or phone number)."""
    identifier: Optional[str] = Field(None, description="Vehicle number or phone number")
    vehicleNumber: Optional[str] = Field(None, description="Vehicle registration number")
    password: str = Field(..., min_length=1, description="Password")
    deviceToken: Optional[str] = Field(None, description="FCM / Expo device push token")
    deviceType: Optional[str] = Field("ANDROID", description="ANDROID, IOS, WEB")

    @field_validator("vehicleNumber")
    @classmethod
    def clean_vehicle(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return normalize_vehicle_number(v)
        return v


class TokenResponse(BaseModel):
    """JWT tokens returned on login / registration."""
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"
    expiresInSeconds: int


class UserProfileResponse(BaseModel):
    """User profile details."""
    id: UUID
    phoneNumber: Optional[str] = None
    name: Optional[str] = None
    isFlagged: bool = False
    strikeCount: int = 0
    reputationScore: float = 100.0
    createdAt: datetime
    primaryVehicle: Optional[str] = None
    vehicleCount: int = 0

    # Frontend aliases (snake_case)
    phone_number: Optional[str] = None
    vehicle_number: Optional[str] = None
    created_at: Optional[datetime] = None
    reputation_score: Optional[float] = None
    total_requests: Optional[int] = 0
    resolved_requests: Optional[int] = 0

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Comprehensive authentication response."""
    success: bool
    tokens: TokenResponse
    user: UserProfileResponse
    message: str


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refreshToken: str
