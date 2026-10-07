"""
Core business logic service for vehicle obstruction resolution requests.
Fixes:
- Section 99 Issue 15: Masked vehicle plates returned to preserve privacy
- Section 99 Issue 28: Requester message is persisted
- Section 99 Issue 29: License plate is normalized prior to processing
- Uses ensure_utc to safely compare timestamps across SQLite and Postgres
"""
from datetime import timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from loguru import logger

from app.core.config import settings
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.request import Request, RequestStatus, ResponseType
from app.models.audit_log import AuditLog, ActionType
from app.utils.datetime import now_utc, format_ist, ensure_utc
from app.utils.vehicle_validation import normalize_vehicle_number, mask_vehicle_number, validate_vehicle_format
from app.services.rate_limit_service import rate_limit_service
from app.services.notification_service import notification_service


class RequestService:
    """Manages obstruction request lifecycle: creation, response, resolution, and cancellation."""

    def create_request(
        self,
        db: Session,
        requester: User,
        target_vehicle: str,
        message: Optional[str] = None,
        is_emergency: bool = False
    ) -> Dict[str, Any]:
        """Initiates a call request to notify a blocking vehicle owner."""
        # 1. Normalize and validate vehicle plate (Fixes Issue 29)
        norm_plate = normalize_vehicle_number(target_vehicle)
        if not norm_plate or not validate_vehicle_format(norm_plate):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid vehicle registration number format."
            )

        # 2. Check requester abuse / ban status
        if requester.isBanned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is suspended due to community guideline violations."
            )

        # 3. Rate limiting check
        rate_status = rate_limit_service.check_rate_limit(requester.id)
        if not rate_status.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=rate_status.message or "Request limit reached. Please wait before trying again."
            )

        # 4. Target cooldown check
        cooldown_rem = rate_limit_service.check_target_cooldown(requester.id, norm_plate)
        if cooldown_rem:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {cooldown_rem} seconds before notifying this vehicle again."
            )

        # 5. Lookup target vehicle in database
        target_veh_record = db.query(Vehicle).filter(
            Vehicle.vehicleNumber == norm_plate,
            Vehicle.isActive == True
        ).first()

        if not target_veh_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle is not registered on FreeWay Community."
            )

        target_user = db.query(User).filter(User.id == target_veh_record.userId).first()
        if not target_user or not target_user.isActive:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle owner account is currently inactive."
            )

        # 6. Prevent self-obstruction requests
        if target_user.id == requester.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot create an obstruction request for your own vehicle."
            )

        # 7. Check for duplicate pending request
        existing_pending = db.query(Request).filter(
            Request.requesterId == requester.id,
            Request.targetUserId == target_user.id,
            Request.status == RequestStatus.PENDING.value
        ).first()

        if existing_pending:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active request is already awaiting response from this vehicle owner."
            )

        # 8. Create Request record (Fixes Issue 28: persists message)
        now = now_utc()
        expires = now + timedelta(minutes=settings.REQUEST_EXPIRY_MINUTES)
        req_record = Request(
            requesterId=requester.id,
            targetUserId=target_user.id,
            targetVehicle=norm_plate,
            status=RequestStatus.PENDING.value,
            message=message or "Vehicle is blocking access/driveway, please move it.",
            createdAt=now,
            expiresAt=expires
        )
        db.add(req_record)

        requester.requestCount += 1
        target_veh_record.lastIdentifiedAt = now

        audit = AuditLog(
            userId=requester.id,
            action=ActionType.REQUEST_CREATE.value,
            resourceType="REQUEST",
            resourceId=str(req_record.id),
            details=f"Obstruction request created for {mask_vehicle_number(norm_plate)}"
        )
        db.add(audit)
        db.commit()
        db.refresh(req_record)

        # 9. Rate limiting quota & cooldown
        rate_limit_service.increment_request_count(requester.id)
        rate_limit_service.set_target_cooldown(requester.id, norm_plate)

        # 10. Dispatch notification
        masked_plate = mask_vehicle_number(norm_plate)
        notification_service.send_obstruction_alert(
            db=db,
            target_user=target_user,
            request_id=req_record.id,
            vehicle_plate=masked_plate,
            message=req_record.message
        )

        return {
            "success": True,
            "requestId": req_record.id,
            "maskedTargetVehicle": masked_plate,
            "status": req_record.status,
            "expiresAt": req_record.expiresAt,
            "message": "Vehicle owner notified successfully."
        }

    def respond_to_request(
        self,
        db: Session,
        target_user: User,
        request_id: UUID,
        response_type: ResponseType,
        response_message: Optional[str] = None,
        eta_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Handles response from blocking vehicle owner."""
        req = db.query(Request).filter(Request.id == request_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")

        if req.targetUserId != target_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized.")

        if req.status not in [RequestStatus.PENDING.value, RequestStatus.ACKNOWLEDGED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot respond to request with status '{req.status}'."
            )

        now = now_utc()
        req.response = response_type.value
        req.responseMessage = response_message
        req.etaMinutes = eta_minutes
        req.respondedAt = now
        req.status = (
            RequestStatus.ON_MY_WAY.value if response_type == ResponseType.ON_MY_WAY
            else RequestStatus.ACKNOWLEDGED.value
        )

        requester = db.query(User).filter(User.id == req.requesterId).first()
        if requester:
            notification_service.send_response_alert(
                db=db,
                requester=requester,
                request_id=req.id,
                response_type=req.response,
                eta_minutes=eta_minutes,
                message=response_message
            )

        db.commit()
        return {
            "success": True,
            "requestId": req.id,
            "status": req.status,
            "message": "Response submitted successfully."
        }

    def resolve_request(self, db: Session, user: User, request_id: UUID) -> Dict[str, Any]:
        """Marks obstruction resolved when vehicle has moved."""
        req = db.query(Request).filter(Request.id == request_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")

        if req.requesterId != user.id and req.targetUserId != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized.")

        now = now_utc()
        req.status = RequestStatus.RESOLVED.value
        req.resolvedAt = now
        db.commit()

        return {
            "success": True,
            "requestId": req.id,
            "status": req.status,
            "message": "Obstruction resolved. Thank you!"
        }

    def cancel_request(self, db: Session, requester: User, request_id: UUID) -> Dict[str, Any]:
        """Cancels a pending request."""
        req = db.query(Request).filter(Request.id == request_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")

        if req.requesterId != requester.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized.")

        req.status = RequestStatus.CANCELLED.value
        db.commit()

        return {
            "success": True,
            "requestId": req.id,
            "status": req.status,
            "message": "Request cancelled successfully."
        }

    def get_request_detail(self, db: Session, user: User, request_id: UUID) -> Dict[str, Any]:
        """Retrieves request details with live remaining time calculation."""
        req = db.query(Request).filter(Request.id == request_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")

        if req.requesterId != user.id and req.targetUserId != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized.")

        now = now_utc()
        exp_utc = ensure_utc(req.expiresAt)
        if req.status == RequestStatus.PENDING.value and exp_utc and now > exp_utc:
            req.status = RequestStatus.EXPIRED.value
            db.commit()

        rem_secs = max(int((exp_utc - now).total_seconds()), 0) if exp_utc else 0

        return {
            "id": req.id,
            "requesterId": req.requesterId,
            "targetUserId": req.targetUserId,
            "maskedTargetVehicle": mask_vehicle_number(req.targetVehicle),
            "status": req.status,
            "message": req.message,
            "response": req.response,
            "responseMessage": req.responseMessage,
            "etaMinutes": req.etaMinutes,
            "createdAt": req.createdAt,
            "expiresAt": req.expiresAt,
            "respondedAt": req.respondedAt,
            "resolvedAt": req.resolvedAt,
            "isRequester": (req.requesterId == user.id),
            "isTarget": (req.targetUserId == user.id),
            "remainingSeconds": rem_secs,
            "formattedCreatedIST": format_ist(req.createdAt)
        }

    def get_user_history(self, db: Session, user: User) -> Dict[str, Any]:
        """Retrieves user's sent and received requests."""
        now = now_utc()
        sent_recs = db.query(Request).filter(Request.requesterId == user.id).order_by(Request.createdAt.desc()).limit(50).all()
        recv_recs = db.query(Request).filter(Request.targetUserId == user.id).order_by(Request.createdAt.desc()).limit(50).all()

        sent_list = []
        for r in sent_recs:
            exp_utc = ensure_utc(r.expiresAt)
            if r.status == RequestStatus.PENDING.value and exp_utc and now > exp_utc:
                r.status = RequestStatus.EXPIRED.value
            rem = max(int((exp_utc - now).total_seconds()), 0) if exp_utc else 0
            sent_list.append({
                "id": r.id,
                "requesterId": r.requesterId,
                "targetUserId": r.targetUserId,
                "maskedTargetVehicle": mask_vehicle_number(r.targetVehicle),
                "status": r.status,
                "message": r.message,
                "response": r.response,
                "responseMessage": r.responseMessage,
                "etaMinutes": r.etaMinutes,
                "createdAt": r.createdAt,
                "expiresAt": r.expiresAt,
                "respondedAt": r.respondedAt,
                "resolvedAt": r.resolvedAt,
                "isRequester": True,
                "isTarget": False,
                "remainingSeconds": rem,
                "formattedCreatedIST": format_ist(r.createdAt)
            })

        recv_list = []
        for r in recv_recs:
            exp_utc = ensure_utc(r.expiresAt)
            if r.status == RequestStatus.PENDING.value and exp_utc and now > exp_utc:
                r.status = RequestStatus.EXPIRED.value
            rem = max(int((exp_utc - now).total_seconds()), 0) if exp_utc else 0
            recv_list.append({
                "id": r.id,
                "requesterId": r.requesterId,
                "targetUserId": r.targetUserId,
                "maskedTargetVehicle": mask_vehicle_number(r.targetVehicle),
                "status": r.status,
                "message": r.message,
                "response": r.response,
                "responseMessage": r.responseMessage,
                "etaMinutes": r.etaMinutes,
                "createdAt": r.createdAt,
                "expiresAt": r.expiresAt,
                "respondedAt": r.respondedAt,
                "resolvedAt": r.resolvedAt,
                "isRequester": False,
                "isTarget": True,
                "remainingSeconds": rem,
                "formattedCreatedIST": format_ist(r.createdAt)
            })

        db.commit()
        return {
            "success": True,
            "sent": sent_list,
            "received": recv_list,
            "total": len(sent_list) + len(recv_list)
        }


request_service = RequestService()
