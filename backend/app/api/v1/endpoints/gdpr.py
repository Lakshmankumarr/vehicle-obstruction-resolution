"""
GDPR Compliance Endpoints for FreeWay Community
Data Export (Right to Access) and Account Deletion (Right to be Forgotten)
"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.request import Request
from app.models.report import Report
from app.models.audit_log import AuditLog
from app.models.device_token import DeviceToken
from app.utils.datetime import now_utc

router = APIRouter()


@router.get("/export", response_model=Dict[str, Any])
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GDPR Article 15 - Right of Access
    Export all personal data associated with the user in JSON format.
    """
    user_id = current_user.id

    # Collect all user data
    vehicles = db.query(Vehicle).filter(Vehicle.userId == user_id).all()
    sent_requests = db.query(Request).filter(Request.requesterId == user_id).all()
    received_requests = db.query(Request).filter(Request.targetUserId == user_id).all()
    reports_made = db.query(Report).filter(Report.reporterId == user_id).all()
    reports_received = db.query(Report).filter(Report.targetUserId == user_id).all()
    device_tokens = db.query(DeviceToken).filter(DeviceToken.userId == user_id).all()
    audit_logs = db.query(AuditLog).filter(AuditLog.userId == user_id).order_by(AuditLog.createdAt.desc()).limit(1000).all()

    export_data = {
        "export_metadata": {
            "exported_at": now_utc().isoformat(),
            "user_id": str(user_id),
            "data_controller": "FreeWay Community",
            "purpose": "GDPR Article 15 - Right of Access"
        },
        "user_profile": {
            "id": str(current_user.id),
            "phoneNumber": current_user.phoneNumber,
            "name": current_user.name,
            "isActive": current_user.isActive,
            "isBanned": current_user.isBanned,
            "isFlagged": current_user.isFlagged,
            "strikeCount": current_user.strikeCount,
            "reputationScore": current_user.reputationScore,
            "requestCount": current_user.requestCount,
            "reportCount": current_user.reportCount,
            "createdAt": current_user.createdAt.isoformat() if current_user.createdAt else None,
            "lastLoginAt": current_user.lastLoginAt.isoformat() if current_user.lastLoginAt else None
        },
        "vehicles": [
            {
                "id": str(v.id),
                "vehicleNumber": v.vehicleNumber,
                "nickname": v.nickname,
                "vehicleType": v.vehicleType,
                "isPrimary": v.isPrimary,
                "isActive": v.isActive,
                "registeredAt": v.registeredAt.isoformat() if v.registeredAt else None,
                "lastIdentifiedAt": v.lastIdentifiedAt.isoformat() if v.lastIdentifiedAt else None
            }
            for v in vehicles
        ],
        "sent_requests": [
            {
                "id": str(r.id),
                "targetVehicle": r.targetVehicle,
                "status": r.status,
                "message": r.message,
                "response": r.response,
                "responseMessage": r.responseMessage,
                "etaMinutes": r.etaMinutes,
                "createdAt": r.createdAt.isoformat() if r.createdAt else None,
                "expiresAt": r.expiresAt.isoformat() if r.expiresAt else None,
                "respondedAt": r.respondedAt.isoformat() if r.respondedAt else None,
                "resolvedAt": r.resolvedAt.isoformat() if r.resolvedAt else None
            }
            for r in sent_requests
        ],
        "received_requests": [
            {
                "id": str(r.id),
                "requesterVehicle": r.targetVehicle,  # This is the requester's plate
                "status": r.status,
                "message": r.message,
                "response": r.response,
                "responseMessage": r.responseMessage,
                "etaMinutes": r.etaMinutes,
                "createdAt": r.createdAt.isoformat() if r.createdAt else None,
                "expiresAt": r.expiresAt.isoformat() if r.expiresAt else None,
                "respondedAt": r.respondedAt.isoformat() if r.respondedAt else None,
                "resolvedAt": r.resolvedAt.isoformat() if r.resolvedAt else None
            }
            for r in received_requests
        ],
        "reports_made": [
            {
                "id": str(r.id),
                "targetUserId": str(r.targetUserId),
                "reportedUserId": str(r.targetUserId),
                "reason": r.reason,
                "description": r.description,
                "status": r.status,
                "createdAt": r.createdAt.isoformat() if r.createdAt else None
            }
            for r in reports_made
        ],
        "reports_received": [
            {
                "id": str(r.id),
                "reporterId": str(r.reporterId),
                "reason": r.reason,
                "description": r.description,
                "status": r.status,
                "createdAt": r.createdAt.isoformat() if r.createdAt else None
            }
            for r in reports_received
        ],
        "device_tokens": [
            {
                "id": str(dt.id),
                "platform": dt.platform,
                "isActive": dt.isActive,
                "createdAt": dt.createdAt.isoformat() if dt.createdAt else None,
                "lastUsedAt": dt.lastUsedAt.isoformat() if dt.lastUsedAt else None
            }
            for dt in device_tokens
        ],
        "audit_logs": [
            {
                "id": str(a.id),
                "action": a.action,
                "resourceType": a.resourceType,
                "resourceId": a.resourceId,
                "details": a.details,
                "ipAddress": a.ipAddress,
                "userAgent": a.userAgent,
                "timestamp": a.createdAt.isoformat() if a.createdAt else None
            }
            for a in audit_logs
        ]
    }

    # Log the export action
    from app.models.audit_log import ActionType
    from app.services.audit_service import audit_service
    audit_service.log_action(
        db=db,
        action=ActionType.DATA_EXPORT.value,
        user_id=user_id,
        resource_type="USER",
        resource_id=str(user_id),
        details="User requested data export under GDPR Article 15"
    )
    db.commit()

    return {
        "success": True,
        "message": "Data export completed successfully",
        "data": export_data
    }


@router.delete("/account", status_code=status.HTTP_200_OK)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GDPR Article 17 - Right to Erasure (Right to be Forgotten)
    Permanently delete all user data and anonymize audit logs.
    """
    user_id = current_user.id

    # Log the deletion request before deleting
    from app.models.audit_log import ActionType
    from app.services.audit_service import audit_service
    audit_service.log_action(
        db=db,
        action=ActionType.ACCOUNT_DELETION.value,
        user_id=user_id,
        resource_type="USER",
        resource_id=str(user_id),
        details="User requested account deletion under GDPR Article 17"
    )
    db.commit()

    # Delete in order of dependencies

    # 1. Delete device tokens
    db.query(DeviceToken).filter(DeviceToken.userId == user_id).delete()

    # 2. Delete reports made by user
    db.query(Report).filter(Report.reporterId == user_id).delete()

    # 3. Update reports received (anonymize reporter)
    db.query(Report).filter(Report.targetUserId == user_id).update({
        "reporterId": None,
        "description": "[Account deleted - GDPR Article 17]"
    })

    # 4. Delete requests where user is requester
    db.query(Request).filter(Request.requesterId == user_id).delete()

    # 5. Update requests where user is target (anonymize)
    db.query(Request).filter(Request.targetUserId == user_id).update({
        "targetUserId": None,
        "targetVehicle": "[DELETED]",
        "message": "[Account deleted - GDPR Article 17]"
    })

    # 6. Delete vehicles
    db.query(Vehicle).filter(Vehicle.userId == user_id).delete()

    # 7. Anonymize audit logs (keep for security but remove PII)
    db.query(AuditLog).filter(AuditLog.userId == user_id).update({
        "userId": None,
        "details": func.concat("[ANONYMIZED - GDPR Art 17] ", AuditLog.details)
    })

    # 8. Finally delete the user
    db.delete(current_user)

    db.commit()

    return {
        "success": True,
        "message": "Account and all associated data have been permanently deleted per GDPR Article 17"
    }


@router.get("/privacy-policy", response_model=Dict[str, Any])
async def get_privacy_policy():
    """
    Return the privacy policy for user consent
    """
    return {
        "success": True,
        "version": "1.0",
        "effective_date": "2026-01-01",
        "last_updated": "2026-11-22",
        "policy": {
            "data_controller": "FreeWay Community",
            "contact": "privacy@freeway-community.example.com",
            "data_collected": [
                "Vehicle registration numbers (license plates)",
                "Phone numbers (optional, for account recovery)",
                "Names (for identification)",
                "Device tokens (for push notifications)",
                "IP addresses and user agents (for security/audit)",
                "Images uploaded for ALPR (deleted immediately after processing)",
                "Location data (only when actively using vehicle identification)"
            ],
            "purposes": [
                "Vehicle obstruction resolution notifications",
                "Account authentication and security",
                "Abuse prevention and rate limiting",
                "Audit logging for security investigations",
                "Service improvement (aggregated, anonymized)"
            ],
            "legal_basis": [
                "Legitimate interest (vehicle obstruction resolution)",
                "Contract performance (account management)",
                "Legal obligation (audit logs, abuse prevention)",
                "Consent (push notifications, optional phone)"
            ],
            "data_sharing": "No personal data is shared with third parties. Vehicle numbers are masked in notifications.",
            "retention": {
                "account_data": "Until account deletion",
                "audit_logs": "90 days",
                "device_tokens": "90 days after last use",
                "alpr_images": "Deleted immediately after processing (< 60 seconds)",
                "requests": "Until resolved/expired, then anonymized"
            },
            "user_rights": [
                "Access your data (GET /api/v1/gdpr/export)",
                "Delete your account (DELETE /api/v1/gdpr/account)",
                "Rectify inaccurate data",
                "Restrict processing",
                "Data portability",
                "Object to processing",
                "Withdraw consent (for notifications)"
            ],
            "security_measures": [
                "JWT authentication with 7-day expiry",
                "bcrypt password hashing (10 rounds)",
                "Rate limiting (10/hr, 50/day)",
                "HTTPS enforcement in production",
                "Image auto-deletion after ALPR",
                "Vehicle number masking in all displays"
            ],
            "international_transfers": "None - all data processed within India",
            "automated_decision_making": "None - no profiling or automated decisions",
            "dpo_contact": "dpo@freeway-community.example.com"
        }
    }