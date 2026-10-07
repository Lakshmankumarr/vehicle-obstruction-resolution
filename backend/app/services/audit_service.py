"""
Audit logging service for tracking critical security and application events.
"""
from typing import Optional, Dict, Any
from uuid import UUID
import json
from sqlalchemy.orm import Session
from loguru import logger

from app.models.audit_log import AuditLog, ActionType
from app.utils.datetime import now_utc


class AuditService:
    """Service to record system actions for compliance, debugging, and auditability."""

    def log_action(
        self,
        db: Session,
        action: str,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Records an audit log entry in the database."""
        try:
            entry = AuditLog(
                userId=user_id,
                action=action,
                resourceType=resource_type,
                resourceId=resource_id,
                details=details,
                ipAddress=ip_address,
                userAgent=user_agent,
                createdAt=now_utc()
            )
            db.add(entry)
            db.commit()
            return entry
        except Exception as e:
            logger.error("Failed to write audit log entry: {}", e)
            db.rollback()
            return None


audit_service = AuditService()
