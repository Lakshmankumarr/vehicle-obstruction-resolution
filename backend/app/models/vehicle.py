"""
Vehicle model representing vehicles owned by users.
Fixes:
- Section 99 Issue 13: Vehicle model fully integrated into application
- Section 99 Issue 14: Users can register and switch between multiple vehicles
- Uses timezone-aware UTC timestamps
"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base, GUID
from app.utils.datetime import now_utc


class Vehicle(Base):
    """Vehicle registration model."""
    __tablename__ = "vehicles"

    # Primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign key to user
    userId = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Normalized Indian plate format, e.g. "DL01AB1234"
    vehicleNumber = Column(String(20), unique=True, nullable=False, index=True)
    nickname = Column(String(50), nullable=True)  # e.g., "My Red Swift"
    vehicleType = Column(String(20), default="CAR", nullable=False)  # CAR, BIKE, SUV, COMMERCIAL

    # Flags
    isPrimary = Column(Boolean, default=False, nullable=False)
    isActive = Column(Boolean, default=True, nullable=False)

    # Timestamps (Timezone-aware UTC)
    registeredAt = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    lastIdentifiedAt = Column(DateTime(timezone=True), nullable=True)

    # Relationship to user
    owner = relationship("User", back_populates="vehicles")

    def __repr__(self):
        return f"<Vehicle(id={self.id}, number={self.vehicleNumber}, user={self.userId})>"
