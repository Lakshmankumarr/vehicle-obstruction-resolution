"""
Vehicle management and privacy-preserving lookup endpoints.
Fixes:
- Section 99 Issue 13: Fully integrates Vehicle model
- Section 99 Issue 14: Supports managing multiple vehicles per user
- Section 99 Issue 15: Masks plate during lookups to prevent identity scraping
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.audit_log import ActionType
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleIdentifyRequest,
    VehicleIdentifyResponse,
)
from app.utils.vehicle_validation import (
    normalize_vehicle_number,
    mask_vehicle_number,
    validate_vehicle_format,
)
from app.services.alpr_service import alpr_service
from app.services.rate_limit_service import rate_limit_service
from app.services.audit_service import audit_service
from app.utils.datetime import now_utc

router = APIRouter()


@router.post("/identify", response_model=VehicleIdentifyResponse)
def identify_vehicle(
    req: VehicleIdentifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Looks up a blocking vehicle by manual plate input or ALPR image.
    Never exposes owner identity, phone number, or unmasked plate.
    """
    plate_to_check = None
    conf = 100.0

    if req.image:
        alpr_res = alpr_service.recognize_plate(req.image)
        if alpr_res.get("success"):
            plate_to_check = alpr_res.get("plate")
            conf = alpr_res.get("confidence", 90.0)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=alpr_res.get("message", "Unable to detect plate in uploaded image.")
            )
    elif req.vehicleNumber:
        plate_to_check = normalize_vehicle_number(req.vehicleNumber)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either vehicleNumber or image is required."
        )

    if not validate_vehicle_format(plate_to_check):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle license plate format."
        )

    # Check database registration
    veh = db.query(Vehicle).filter(
        Vehicle.vehicleNumber == plate_to_check,
        Vehicle.isActive == True
    ).first()

    is_reg = veh is not None
    masked = mask_vehicle_number(plate_to_check)
    can_send = is_reg and (veh.userId != current_user.id)

    # Check cooldown if sending is possible
    cooldown = 0
    if can_send:
        rem = rate_limit_service.check_target_cooldown(current_user.id, plate_to_check)
        if rem:
            cooldown = rem
            can_send = False

    msg = (
        "Vehicle is registered. You can notify the owner to move it."
        if is_reg else
        "Vehicle is not yet registered on FreeWay Community."
    )
    if is_reg and veh.userId == current_user.id:
        msg = "This vehicle is registered under your own account."

    return VehicleIdentifyResponse(
        success=True,
        maskedVehicleNumber=masked,
        targetVehiclePlate=plate_to_check,
        isRegistered=is_reg,
        canSendRequest=can_send,
        confidence=conf,
        message=msg,
        cooldownRemainingSeconds=cooldown
    )


@router.get("/", response_model=List[VehicleResponse])
def list_my_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves all vehicles registered under caller's account."""
    vehs = db.query(Vehicle).filter(
        Vehicle.userId == current_user.id,
        Vehicle.isActive == True
    ).all()

    return [
        VehicleResponse(
            id=v.id,
            vehicleNumber=v.vehicleNumber,
            maskedNumber=mask_vehicle_number(v.vehicleNumber),
            nickname=v.nickname,
            vehicleType=v.vehicleType,
            isPrimary=v.isPrimary,
            isActive=v.isActive,
            registeredAt=v.registeredAt
        )
        for v in vehs
    ]


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def add_vehicle(
    req: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Adds an additional vehicle to caller's account (Multi-vehicle feature)."""
    norm = normalize_vehicle_number(req.vehicleNumber)
    if not validate_vehicle_format(norm):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle license plate format."
        )

    # Check global uniqueness
    existing = db.query(Vehicle).filter(
        Vehicle.vehicleNumber == norm,
        Vehicle.isActive == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle number is already registered to another owner."
        )

    # If first vehicle or requested primary, adjust existing primary flags
    has_primary = db.query(Vehicle).filter(
        Vehicle.userId == current_user.id,
        Vehicle.isPrimary == True,
        Vehicle.isActive == True
    ).first()

    is_prim = req.isPrimary or (has_primary is None)
    if is_prim and has_primary:
        has_primary.isPrimary = False

    veh = Vehicle(
        userId=current_user.id,
        vehicleNumber=norm,
        nickname=req.nickname,
        vehicleType=req.vehicleType or "CAR",
        isPrimary=is_prim,
        registeredAt=now_utc()
    )
    db.add(veh)

    audit_service.log_action(
        db=db,
        action=ActionType.VEHICLE_ADD.value,
        user_id=current_user.id,
        resource_type="VEHICLE",
        resource_id=norm,
        details=f"Added vehicle {norm}"
    )

    db.commit()
    db.refresh(veh)

    return VehicleResponse(
        id=veh.id,
        vehicleNumber=veh.vehicleNumber,
        maskedNumber=mask_vehicle_number(veh.vehicleNumber),
        nickname=veh.nickname,
        vehicleType=veh.vehicleType,
        isPrimary=veh.isPrimary,
        isActive=veh.isActive,
        registeredAt=veh.registeredAt
    )


@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes or deactivates a vehicle from caller's account."""
    veh = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.userId == current_user.id
    ).first()

    if not veh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    veh.isActive = False
    audit_service.log_action(
        db=db,
        action=ActionType.VEHICLE_DELETE.value,
        user_id=current_user.id,
        resource_type="VEHICLE",
        resource_id=veh.vehicleNumber,
        details=f"Removed vehicle {veh.vehicleNumber}"
    )

    db.commit()
    return {"success": True, "message": "Vehicle removed successfully."}
