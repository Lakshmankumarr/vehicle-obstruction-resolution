"""
Notification API schemas for device token registration and push messaging.
"""
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class RegisterDeviceRequest(BaseModel):
    """Schema for registering a push notification device token."""
    token: str = Field(..., min_length=10, max_length=500, description="FCM / Expo / APNS token")
    deviceType: str = Field("ANDROID", description="ANDROID, IOS, WEB")


class RegisterDeviceResponse(BaseModel):
    """Response confirming token registration."""
    success: bool
    message: str


class NotificationHistoryItem(BaseModel):
    """Notification item in user's in-app notification center."""
    id: UUID
    title: str
    body: str
    requestId: Optional[UUID] = None
    createdAt: str
