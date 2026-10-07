"""
Report model for abuse reporting, spam prevention, and dispute tracking.
Uses GUID and timezone-aware UTC timestamps.
"""
import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID
from app.utils.datetime import now_utc


class ReportReason(str, enum.Enum):
    SPAM = "SPAM"
    HARASSMENT = "HARASSMENT"
    FALSE_REQUEST = "FALSE_REQUEST"
    WRONG_VEHICLE = "WRONG_VEHICLE"
    ABUSE = "ABUSE"
    OTHER = "OTHER"


class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACTIONED = "ACTIONED"
    DISMISSED = "DISMISSED"


class AdminAction(str, enum.Enum):
    WARNING = "WARNING"
    STRIKE = "STRIKE"
    TEMPORARY_BAN = "TEMPORARY_BAN"
    PERMANENT_BAN = "PERMANENT_BAN"
    NO_ACTION = "NO_ACTION"


class Report(Base):
    """User report model."""
    __tablename__ = "reports"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Participants
    reporterId = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    targetUserId = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    requestId = Column(GUID(), ForeignKey("requests.id", ondelete="SET NULL"), nullable=True, index=True)

    # Report details
    reason = Column(String(50), default=ReportReason.SPAM.value, nullable=False)
    description = Column(String(1000), nullable=True)

    # Status tracking
    status = Column(String(30), default=ReportStatus.PENDING.value, nullable=False, index=True)

    # Admin actions
    action = Column(String(30), nullable=True)
    reviewedBy = Column(GUID(), nullable=True)
    reviewedAt = Column(DateTime(timezone=True), nullable=True)

    # Timestamps (Timezone-aware UTC)
    createdAt = Column(DateTime(timezone=True), default=now_utc, nullable=False, index=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporterId], back_populates="reports_made")
    target_user = relationship("User", foreign_keys=[targetUserId], back_populates="reports_received")

    def __repr__(self):
        return f"<Report(id={self.id}, reason={self.reason}, status={self.status})>"
