"""
Authentication API endpoints: registration, login, token refresh, and profile retrieval.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.audit_log import ActionType
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserProfileResponse,
    AuthResponse,
    RefreshTokenRequest,
)
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.utils.vehicle_validation import normalize_vehicle_number, validate_vehicle_format
from app.utils.datetime import now_utc
from app.services.device_token_service import device_token_service
from app.services.audit_service import audit_service

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user and binds their primary vehicle."""
    norm_plate = normalize_vehicle_number(req.vehicleNumber)
    if not validate_vehicle_format(norm_plate):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle number format. Expected format e.g. DL01AB1234 or 22BH1234AA"
        )

    # Check if vehicle already registered
    existing_veh = db.query(Vehicle).filter(Vehicle.vehicleNumber == norm_plate).first()
    if existing_veh:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle number is already registered in FreeWay Community."
        )

    # Check phone number if provided
    if req.phoneNumber:
        existing_phone = db.query(User).filter(User.phoneNumber == req.phoneNumber).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number is already associated with another account."
            )

    # Create user
    now = now_utc()
    user = User(
        phoneNumber=req.phoneNumber,
        name=req.name,
        passwordHash=hash_password(req.password),
        createdAt=now,
        lastLoginAt=now
    )
    db.add(user)
    db.flush()

    # Create primary vehicle
    veh = Vehicle(
        userId=user.id,
        vehicleNumber=norm_plate,
        isPrimary=True,
        vehicleType="CAR",
        registeredAt=now
    )
    db.add(veh)

    # Register push token if provided
    if req.deviceToken:
        device_token_service.register_token(
            db=db,
            user_id=user.id,
            token=req.deviceToken,
            device_type=req.deviceType or "ANDROID"
        )

    audit_service.log_action(
        db=db,
        action=ActionType.USER_REGISTER.value,
        user_id=user.id,
        resource_type="USER",
        resource_id=str(user.id),
        details=f"Registered with primary vehicle {norm_plate}"
    )

    db.commit()
    db.refresh(user)

    # Generate tokens
    token_data = {"userId": str(user.id), "vehicleNumber": norm_plate}
    access_tok = create_access_token(token_data)
    refresh_tok = create_refresh_token(token_data)

    user_prof = UserProfileResponse(
        id=user.id,
        phoneNumber=user.phoneNumber,
        name=user.name,
        isFlagged=user.isFlagged,
        strikeCount=user.strikeCount,
        reputationScore=user.reputationScore,
        createdAt=user.createdAt,
        primaryVehicle=norm_plate,
        vehicleCount=1
    )

    return AuthResponse(
        success=True,
        tokens=TokenResponse(
            accessToken=access_tok,
            refreshToken=refresh_tok,
            expiresInSeconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        user=user_prof,
        message="Registration successful. Welcome to FreeWay Community!"
    )


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Logs in an existing user via vehicle number or phone number."""
    identifier = req.vehicleNumber or req.identifier
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle number or phone number is required."
        )

    clean_id = normalize_vehicle_number(identifier)

    # Find user either via registered vehicle or via phone
    veh = db.query(Vehicle).filter(Vehicle.vehicleNumber == clean_id).first()
    user = None
    primary_plate = clean_id

    if veh:
        user = db.query(User).filter(User.id == veh.userId).first()
    else:
        # Try finding by phone
        user = db.query(User).filter(User.phoneNumber == identifier).first()
        if user and user.vehicles:
            primary_veh = next((v for v in user.vehicles if v.isPrimary), user.vehicles[0])
            primary_plate = primary_veh.vehicleNumber

    if not user or not verify_password(req.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check your vehicle number and password."
        )

    if user.isBanned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended for violating community guidelines."
        )

    user.lastLoginAt = now_utc()

    if req.deviceToken:
        device_token_service.register_token(
            db=db,
            user_id=user.id,
            token=req.deviceToken,
            device_type=req.deviceType or "ANDROID"
        )

    audit_service.log_action(
        db=db,
        action=ActionType.USER_LOGIN.value,
        user_id=user.id,
        resource_type="USER",
        resource_id=str(user.id),
        details="User logged in"
    )

    db.commit()
    db.refresh(user)

    token_data = {"userId": str(user.id), "vehicleNumber": primary_plate}
    access_tok = create_access_token(token_data)
    refresh_tok = create_refresh_token(token_data)

    user_prof = UserProfileResponse(
        id=user.id,
        phoneNumber=user.phoneNumber,
        name=user.name,
        isFlagged=user.isFlagged,
        strikeCount=user.strikeCount,
        reputationScore=user.reputationScore,
        createdAt=user.createdAt,
        primaryVehicle=primary_plate,
        vehicleCount=len(user.vehicles)
    )

    return AuthResponse(
        success=True,
        tokens=TokenResponse(
            accessToken=access_tok,
            refreshToken=refresh_tok,
            expiresInSeconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        user=user_prof,
        message="Login successful."
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refreshes expired access token using valid refresh token."""
    payload = decode_refresh_token(req.refreshToken)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    user_id = payload.get("userId")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.isBanned or not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User session invalid."
        )

    token_data = {"userId": str(user.id), "vehicleNumber": payload.get("vehicleNumber")}
    new_access_tok = create_access_token(token_data)
    new_refresh_tok = create_refresh_token(token_data)

    return TokenResponse(
        accessToken=new_access_tok,
        refreshToken=new_refresh_tok,
        expiresInSeconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Returns current authenticated user details."""
    primary_plate = None
    if current_user.vehicles:
        prim = next((v for v in current_user.vehicles if v.isPrimary), current_user.vehicles[0])
        primary_plate = prim.vehicleNumber

    return UserProfileResponse(
        id=current_user.id,
        phoneNumber=current_user.phoneNumber,
        name=current_user.name,
        isFlagged=current_user.isFlagged,
        strikeCount=current_user.strikeCount,
        reputationScore=current_user.reputationScore,
        createdAt=current_user.createdAt,
        primaryVehicle=primary_plate,
        vehicleCount=len(current_user.vehicles)
    )
