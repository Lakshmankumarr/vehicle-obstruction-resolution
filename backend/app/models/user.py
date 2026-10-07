"""
User model representing platform users and vehicle owners.
Fixes:
- Section 99 Issue 10: defined isFlagged property
- Section 99 Issue 11: abuse restrictions persist (strikeCount, isBanned, isFlagged)
- Section 99 Issue 12: eliminated duplicate User.fcmToken in favor of DeviceToken table
- Section 99 Issue 14: users can own multiple vehicles
- Uses timezone-aware UTC timestamps
"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID
from app.utils.datetime import now_utc


class User(Base):
    """Registered user model."""
    __tablename__ = "users"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Credentials & identification
    phoneNumber = Column(String(20), unique=True, nullable=True, index=True)
    name = Column(String(100), nullable=True)
    passwordHash = Column(String(255), nullable=False)

    # Status flags & abuse moderation (Persisted)
    isActive = Column(Boolean, default=True, nullable=False)
    isBanned = Column(Boolean, default=False, nullable=False)
    isFlagged = Column(Boolean, default=False, nullable=False)
    strikeCount = Column(Integer, default=0, nullable=False)
    reputationScore = Column(Float, default=100.0, nullable=False)

    # Activity counters
    requestCount = Column(Integer, default=0, nullable=False)
    reportCount = Column(Integer, default=0, nullable=False)

    # Timestamps (Timezone-aware UTC)
    createdAt = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    lastLoginAt = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    device_tokens = relationship("DeviceToken", back_populates="user", cascade="all, delete-orphan")
    sent_requests = relationship("Request", foreign_keys="Request.requesterId", back_populates="requester")
    received_requests = relationship("Request", foreign_keys="Request.targetUserId", back_populates="target_user")
    reports_made = relationship("Report", foreign_keys="Report.reporterId", back_populates="reporter")
    reports_received = relationship("Report", foreign_keys="Report.targetUserId", back_populates="target_user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phoneNumber}, banned={self.isBanned})>"
