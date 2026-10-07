"""
Administrative moderation and system metrics endpoints.
"""
from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.request import Request
from app.models.report import Report, ReportStatus, AdminAction
from app.models.audit_log import AuditLog, ActionType
from app.services.report_service import report_service
from app.services.audit_service import audit_service
from app.utils.datetime import now_utc

router = APIRouter()


class BanUserRequest(BaseModel):
    isBanned: bool
    reason: str


class ResolveReportAdminRequest(BaseModel):
    action: AdminAction


@router.get("/flagged-users")
def get_flagged_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists users with strikes or flagged status."""
    users = db.query(User).filter(
        (User.isFlagged == True) | (User.strikeCount > 0) | (User.isBanned == True)
    ).all()

    return [
        {
            "id": u.id,
            "phoneNumber": u.phoneNumber,
            "name": u.name,
            "strikeCount": u.strikeCount,
            "isFlagged": u.isFlagged,
            "isBanned": u.isBanned,
            "reportCount": u.reportCount,
            "reputationScore": u.reputationScore,
            "createdAt": u.createdAt
        }
        for u in users
    ]


@router.get("/reports/pending")
def get_pending_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists pending abuse reports awaiting review."""
    reports = report_service.list_pending_reports(db)
    return [
        {
            "id": r.id,
            "reporterId": r.reporterId,
            "targetUserId": r.targetUserId,
            "requestId": r.requestId,
            "reason": r.reason,
            "description": r.description,
            "status": r.status,
            "createdAt": r.createdAt
        }
        for r in reports
    ]


@router.post("/reports/{report_id}/action")
def action_report(
    report_id: UUID,
    req: ResolveReportAdminRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Applies administrative action (warning, strike, ban) to a reported user."""
    return report_service.resolve_report(
        db=db,
        admin_id=current_user.id,
        report_id=report_id,
        action=req.action
    )


@router.post("/users/{user_id}/ban")
def ban_user(
    user_id: UUID,
    req: BanUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Suspends or reinstates a user account."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    target.isBanned = req.isBanned
    if req.isBanned:
        target.isFlagged = True

    audit_service.log_action(
        db=db,
        action=ActionType.USER_BANNED.value if req.isBanned else "USER_UNBANNED",
        user_id=current_user.id,
        resource_type="USER",
        resource_id=str(target.id),
        details=req.reason
    )

    db.commit()
    return {
        "success": True,
        "userId": target.id,
        "isBanned": target.isBanned,
        "message": f"User {'banned' if req.isBanned else 'unbanned'} successfully."
    }


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Provides high-level platform health metrics."""
    return {
        "totalUsers": db.query(User).count(),
        "totalVehicles": db.query(Vehicle).count(),
        "totalRequests": db.query(Request).count(),
        "totalReports": db.query(Report).count(),
        "bannedUsers": db.query(User).filter(User.isBanned == True).count(),
        "pendingReports": db.query(Report).filter(Report.status == ReportStatus.PENDING.value).count()
    }
