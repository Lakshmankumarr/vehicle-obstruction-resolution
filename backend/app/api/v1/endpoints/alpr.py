"""
ALPR license plate recognition API endpoint.
Supports Base64 JSON and multipart image uploads with India region processing.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
import base64
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.vehicle import Vehicle
from app.schemas.alpr import ALPRScanResponse, PlateCandidate
from app.services.alpr_service import alpr_service
from app.utils.vehicle_validation import mask_vehicle_number, normalize_vehicle_number

router = APIRouter()


class Base64ScanRequest(BaseModel):
    image: str  # Base64 encoded image string


@router.post("/scan", response_model=ALPRScanResponse)
def scan_plate_base64(
    req: Base64ScanRequest,
    db: Session = Depends(get_db)
):
    """Scans license plate image via Base64 string."""
    res = alpr_service.recognize_plate(req.image)
    if not res.get("success") or not res.get("plate"):
        return ALPRScanResponse(
            success=False,
            primaryPlate=None,
            maskedPlate=None,
            confidence=0.0,
            candidates=[],
            isRegistered=False,
            provider=res.get("provider", "mock"),
            message=res.get("message", "Could not detect license plate.")
        )

    plate = res["plate"]
    masked = res["maskedPlate"]
    conf = res["confidence"]

    # Check registration
    is_reg = db.query(Vehicle).filter(
        Vehicle.vehicleNumber == plate,
        Vehicle.isActive == True
    ).first() is not None

    candidate = PlateCandidate(
        plate=plate,
        maskedPlate=masked,
        confidence=conf,
        isRegistered=is_reg
    )

    return ALPRScanResponse(
        success=True,
        primaryPlate=plate,
        maskedPlate=masked,
        confidence=conf,
        candidates=[candidate],
        isRegistered=is_reg,
        provider=res.get("provider", "mock"),
        message=res.get("message", "Plate scanned successfully.")
    )


@router.post("/upload", response_model=ALPRScanResponse)
async def scan_plate_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Scans license plate image uploaded via Multipart form."""
    content = await file.read()
    b64_str = base64.b64encode(content).decode("utf-8")
    res = alpr_service.recognize_plate(b64_str)

    if not res.get("success") or not res.get("plate"):
        return ALPRScanResponse(
            success=False,
            primaryPlate=None,
            maskedPlate=None,
            confidence=0.0,
            candidates=[],
            isRegistered=False,
            provider=res.get("provider", "mock"),
            message=res.get("message", "Could not detect license plate.")
        )

    plate = res["plate"]
    masked = res["maskedPlate"]
    conf = res["confidence"]

    is_reg = db.query(Vehicle).filter(
        Vehicle.vehicleNumber == plate,
        Vehicle.isActive == True
    ).first() is not None

    return ALPRScanResponse(
        success=True,
        primaryPlate=plate,
        maskedPlate=masked,
        confidence=conf,
        candidates=[PlateCandidate(plate=plate, maskedPlate=masked, confidence=conf, isRegistered=is_reg)],
        isRegistered=is_reg,
        provider=res.get("provider", "mock"),
        message=res.get("message", "Plate scanned successfully.")
    )
