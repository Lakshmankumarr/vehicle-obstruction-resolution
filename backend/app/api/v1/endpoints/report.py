"""
Abuse reporting and trust status API endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.report import CreateReportRequest, CreateReportResponse
from app.services.report_service import report_service

router = APIRouter()


class StrikeStatusResponse(BaseModel):
    isFlagged: bool
    strikeCount: int
    reputationScore: float
    maxStrikes: int = 3
    isBanned: bool


@router.post("/", response_model=CreateReportResponse, status_code=status.HTTP_201_CREATED)
def submit_report(
    req: CreateReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submits an abuse or false-request report against a user."""
    res = report_service.create_report(
        db=db,
        reporter_id=current_user.id,
        target_user_id=req.targetUserId,
        reason=req.reason.value if hasattr(req.reason, "value") else str(req.reason),
        description=req.description,
        request_id=req.requestId
    )
    return CreateReportResponse(**res)


@router.get("/status", response_model=StrikeStatusResponse)
def get_strike_status(current_user: User = Depends(get_current_user)):
    """Retrieves caller's current community standing and strikes."""
    return StrikeStatusResponse(
        isFlagged=current_user.isFlagged,
        strikeCount=current_user.strikeCount,
        reputationScore=current_user.reputationScore,
        isBanned=current_user.isBanned
    )
