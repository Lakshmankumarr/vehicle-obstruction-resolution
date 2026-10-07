"""
Abuse, false-request, and dispute moderation service.
Fixes:
- Section 99 Issue 10: Safely manages User.isFlagged
- Section 99 Issue 11: Abuse strikes and restrictions are persisted to database
- Section 99 Issue 25: Target user existence is strictly validated before report creation
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from loguru import logger

from app.core.config import settings
from app.models.user import User
from app.models.request import Request
from app.models.report import Report, ReportReason, ReportStatus, AdminAction
from app.models.audit_log import AuditLog, ActionType
from app.utils.datetime import now_utc


class ReportService:
    """Manages community trust, user reporting, and automated abuse penalization."""

    def create_report(
        self,
        db: Session,
        reporter_id: UUID,
        target_user_id: UUID,
        reason: str,
        description: Optional[str] = None,
        request_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Creates an abuse report with target validation and persistent strike tracking.
        """
        # 1. Prevent self-reports
        if reporter_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot report yourself."
            )

        # 2. Validate target user existence (Fixes Issue 25)
        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reported target user does not exist."
            )

        # 3. Validate request existence if provided
        if request_id:
            req_check = db.query(Request).filter(Request.id == request_id).first()
            if not req_check:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Referenced request not found."
                )

        # 4. Enforce daily report limit per reporter
        now = now_utc()
        day_ago = now - timedelta(days=1)
        recent_reports = db.query(Report).filter(
            Report.reporterId == reporter_id,
            Report.createdAt >= day_ago
        ).count()

        if recent_reports >= 10:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily report submission limit reached."
            )

        # 5. Create Report record
        rep = Report(
            reporterId=reporter_id,
            targetUserId=target_user_id,
            requestId=request_id,
            reason=reason,
            description=description,
            status=ReportStatus.PENDING.value,
            createdAt=now
        )
        db.add(rep)

        # 6. Increment reporter counter
        reporter = db.query(User).filter(User.id == reporter_id).first()
        if reporter:
            reporter.reportCount += 1

        # 7. Check cumulative complaints against target user (Fixes Issue 11)
        target_total_reports = db.query(Report).filter(
            Report.targetUserId == target_user_id
        ).count() + 1

        if target_total_reports >= settings.STRIKE_THRESHOLD:
            target_user.isFlagged = True
            target_user.strikeCount += 1
            logger.warning("Target user {} flagged: {} reports, {} strikes", target_user_id, target_total_reports, target_user.strikeCount)
            if target_user.strikeCount >= settings.STRIKE_THRESHOLD:
                target_user.isBanned = True
                logger.error("User {} automatically suspended due to excessive strikes", target_user_id)

        # 8. Record audit log
        audit = AuditLog(
            userId=reporter_id,
            action=ActionType.REPORT_CREATE.value,
            resourceType="REPORT",
            resourceId=str(rep.id),
            details=f"Report against {target_user_id} for {reason}"
        )
        db.add(audit)
        db.commit()
        db.refresh(rep)

        return {
            "success": True,
            "reportId": rep.id,
            "status": rep.status,
            "message": "Report submitted. Our moderation team will review this shortly."
        }

    def list_pending_reports(self, db: Session) -> List[Report]:
        """Lists pending reports for administrative review."""
        return db.query(Report).filter(Report.status == ReportStatus.PENDING.value).all()

    def resolve_report(
        self,
        db: Session,
        admin_id: UUID,
        report_id: UUID,
        action: AdminAction
    ) -> Dict[str, Any]:
        """Administrative review action."""
        rep = db.query(Report).filter(Report.id == report_id).first()
        if not rep:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")

        rep.status = ReportStatus.ACTIONED.value
        rep.action = action.value
        rep.reviewedBy = admin_id
        rep.reviewedAt = now_utc()

        target = db.query(User).filter(User.id == rep.targetUserId).first()
        if target:
            if action in [AdminAction.STRIKE, AdminAction.TEMPORARY_BAN, AdminAction.PERMANENT_BAN]:
                target.strikeCount += 1
                target.isFlagged = True
                if action == AdminAction.PERMANENT_BAN:
                    target.isBanned = True

        db.commit()
        return {"success": True, "message": f"Report actioned with {action.value}"}


report_service = ReportService()
