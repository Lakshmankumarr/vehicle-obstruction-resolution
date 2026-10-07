"""
DeviceToken model for mobile/web push notifications (FCM / APNS / Expo).
Fixes:
- Section 99 Issue 12: Consolidates push tokens into DeviceToken table
- Supports multiple devices per user and token lifecycle management
- Uses timezone-aware UTC timestamps
"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID
from app.utils.datetime import now_utc


class DeviceToken(Base):
    """Mobile and web push notification device tokens."""
    __tablename__ = "device_tokens"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key to user
    userId = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Unique push device token
    token = Column(String(500), unique=True, nullable=False, index=True)
    deviceType = Column(String(20), default="ANDROID", nullable=False)  # ANDROID, IOS, WEB

    # Lifecycle status
    isActive = Column(Boolean, default=True, nullable=False)

    # Timestamps (Timezone-aware UTC)
    createdAt = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    lastUsedAt = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    user = relationship("User", back_populates="device_tokens")

    def __repr__(self):
        return f"<DeviceToken(id={self.id}, user={self.userId}, type={self.deviceType})>"
