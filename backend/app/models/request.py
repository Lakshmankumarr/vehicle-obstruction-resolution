"""
Request model representing vehicle obstruction resolution requests.
Fixes:
- Section 99 Issue 7: Pure timezone-aware UTC timestamps
- Section 99 Issue 8: Replaced naive IST datetime with DateTime(timezone=True)
- Section 99 Issue 28: requester's message field is explicitly persisted
- Supports full resolution lifecycle (PENDING -> ACKNOWLEDGED / ON_MY_WAY / CANNOT_MOVE -> RESOLVED / EXPIRED / CANCELLED)
"""
import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, CheckConstraint, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID
from app.utils.datetime import now_utc


class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    ON_MY_WAY = "ON_MY_WAY"
    MOVING = "MOVING"
    CANNOT_MOVE = "CANNOT_MOVE"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ResponseType(str, enum.Enum):
    ON_MY_WAY = "ON_MY_WAY"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    CANNOT_MOVE = "CANNOT_MOVE"
    MESSAGE = "MESSAGE"
    KEYS_WITH_GUARD = "KEYS_WITH_GUARD"


class Request(Base):
    """Obstruction resolution request model."""
    __tablename__ = "requests"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Participants
    requesterId = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    targetUserId = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Normalized target vehicle plate
    targetVehicle = Column(String(20), nullable=False, index=True)

    # Status & content
    status = Column(String(20), default=RequestStatus.PENDING.value, nullable=False, index=True)
    message = Column(String(500), nullable=True)  # Section 99 Issue 28: requester message persisted

    # Response details
    response = Column(String(50), nullable=True)
    responseMessage = Column(String(500), nullable=True)
    etaMinutes = Column(Integer, nullable=True)  # ETA in minutes if ON_MY_WAY

    # Timestamps (Timezone-aware UTC)
    createdAt = Column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)
    expiresAt = Column(DateTime(timezone=True), nullable=False, index=True)
    respondedAt = Column(DateTime(timezone=True), nullable=True)
    resolvedAt = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    requester = relationship("User", foreign_keys=[requesterId], back_populates="sent_requests")
    target_user = relationship("User", foreign_keys=[targetUserId], back_populates="received_requests")

    __table_args__ = (
        CheckConstraint('"requesterId" != "targetUserId"', name="check_different_users"),
        Index("idx_requester_created", "requesterId", "createdAt"),
        Index("idx_target_status", "targetUserId", "status"),
    )

    def __repr__(self):
        return f"<Request(id={self.id}, status={self.status}, vehicle={self.targetVehicle})>"
