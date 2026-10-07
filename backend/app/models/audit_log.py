"""
AuditLog model for recording sensitive system actions, logins, and status transitions.
Uses GUID and timezone-aware UTC timestamps.
"""
import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID
from app.utils.datetime import now_utc


class ActionType(str, enum.Enum):
    USER_REGISTER = "USER_REGISTER"
    USER_LOGIN = "USER_LOGIN"
    VEHICLE_ADD = "VEHICLE_ADD"
    VEHICLE_DELETE = "VEHICLE_DELETE"
    REQUEST_CREATE = "REQUEST_CREATE"
    REQUEST_RESPOND = "REQUEST_RESPOND"
    REQUEST_RESOLVE = "REQUEST_RESOLVE"
    REQUEST_CANCEL = "REQUEST_CANCEL"
    REQUEST_EXPIRED = "REQUEST_EXPIRED"
    NOTIFICATION_SENT = "NOTIFICATION_SENT"
    NOTIFICATION_FAILED = "NOTIFICATION_FAILED"
    REPORT_CREATE = "REPORT_CREATE"
    USER_BANNED = "USER_BANNED"


class AuditLog(Base):
    """Audit log record."""
    __tablename__ = "audit_logs"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Actor
    userId = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Action details
    action = Column(String(50), nullable=False, index=True)
    resourceType = Column(String(50), nullable=True)
    resourceId = Column(String(100), nullable=True)

    # Request metadata
    ipAddress = Column(String(50), nullable=True)
    userAgent = Column(String(500), nullable=True)
    details = Column(Text, nullable=True)

    # Timestamps (Timezone-aware UTC)
    createdAt = Column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user={self.userId})>"
