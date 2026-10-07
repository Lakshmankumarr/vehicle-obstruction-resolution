"""
Obstruction resolution request API endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.request import (
    CreateRequestRequest,
    CreateRequestResponse,
    RespondRequestRequest,
    RequestActionResponse,
    RequestDetailResponse,
    RequestHistoryResponse,
)
from app.services.request_service import request_service

router = APIRouter()


@router.post("/", response_model=CreateRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    req: CreateRequestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initiates an obstruction resolution call request to a blocking vehicle owner."""
    res = request_service.create_request(
        db=db,
        requester=current_user,
        target_vehicle=req.targetVehicle,
        message=req.message,
        is_emergency=req.isEmergency or False
    )
    return CreateRequestResponse(**res)


@router.post("/respond", response_model=RequestActionResponse)
def respond_request(
    req: RespondRequestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Blocking vehicle owner responds with action (e.g. On My Way with ETA)."""
    res = request_service.respond_to_request(
        db=db,
        target_user=current_user,
        request_id=req.requestId,
        response_type=req.response,
        response_message=req.responseMessage,
        eta_minutes=req.etaMinutes
    )
    return RequestActionResponse(**res)


@router.post("/{request_id}/resolve", response_model=RequestActionResponse)
def resolve_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marks obstruction resolved when vehicle has successfully moved."""
    res = request_service.resolve_request(db=db, user=current_user, request_id=request_id)
    return RequestActionResponse(**res)


@router.post("/{request_id}/cancel", response_model=RequestActionResponse)
def cancel_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancels a pending obstruction resolution request."""
    res = request_service.cancel_request(db=db, requester=current_user, request_id=request_id)
    return RequestActionResponse(**res)


@router.get("/history", response_model=RequestHistoryResponse)
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves caller's sent and received obstruction requests."""
    res = request_service.get_user_history(db=db, user=current_user)
    return RequestHistoryResponse(**res)


@router.get("/{request_id}", response_model=RequestDetailResponse)
def get_request_status(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves real-time status and countdown timer for an active request."""
    res = request_service.get_request_detail(db=db, user=current_user, request_id=request_id)
    return RequestDetailResponse(**res)
