"""
Report schemas for abuse and dispute reporting.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.report import ReportReason, ReportStatus


class CreateReportRequest(BaseModel):
    """Schema for filing an abuse or false-request report."""
    targetUserId: UUID = Field(..., description="UUID of user being reported")
    requestId: Optional[UUID] = Field(None, description="Optional request UUID tied to dispute")
    reason: ReportReason = Field(default=ReportReason.SPAM, description="SPAM, HARASSMENT, FALSE_REQUEST, WRONG_VEHICLE, ABUSE, OTHER")
    description: Optional[str] = Field(None, max_length=1000, description="Additional context")


class CreateReportResponse(BaseModel):
    """Report creation response."""
    success: bool
    reportId: UUID
    status: str
    message: str


class ReportDetailResponse(BaseModel):
    """Report details for moderation and review."""
    id: UUID
    reporterId: UUID
    targetUserId: UUID
    requestId: Optional[UUID] = None
    reason: str
    description: Optional[str] = None
    status: str
    action: Optional[str] = None
    createdAt: datetime

    class Config:
        from_attributes = True
