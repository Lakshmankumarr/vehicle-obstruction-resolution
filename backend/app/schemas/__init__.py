"""
Pydantic schemas exports for FreeWay Community API.
"""
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserProfileResponse,
    AuthResponse,
    RefreshTokenRequest,
)
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleIdentifyRequest,
    VehicleIdentifyResponse,
)
from app.schemas.request import (
    CreateRequestRequest,
    CreateRequestResponse,
    RespondRequestRequest,
    RequestActionResponse,
    RequestDetailResponse,
    RequestHistoryResponse,
)
from app.schemas.report import (
    CreateReportRequest,
    CreateReportResponse,
    ReportDetailResponse,
)
from app.schemas.notification import (
    RegisterDeviceRequest,
    RegisterDeviceResponse,
)
from app.schemas.alpr import (
    PlateCandidate,
    ALPRScanResponse,
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserProfileResponse",
    "AuthResponse",
    "RefreshTokenRequest",
    "VehicleCreate",
    "VehicleResponse",
    "VehicleIdentifyRequest",
    "VehicleIdentifyResponse",
    "CreateRequestRequest",
    "CreateRequestResponse",
    "RespondRequestRequest",
    "RequestActionResponse",
    "RequestDetailResponse",
    "RequestHistoryResponse",
    "CreateReportRequest",
    "CreateReportResponse",
    "ReportDetailResponse",
    "RegisterDeviceRequest",
    "RegisterDeviceResponse",
    "PlateCandidate",
    "ALPRScanResponse",
]
