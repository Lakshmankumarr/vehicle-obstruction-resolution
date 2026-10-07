"""
ALPR API request and response schemas.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class PlateCandidate(BaseModel):
    """License plate candidate from recognition engine."""
    plate: str = Field(..., description="Normalized plate string")
    maskedPlate: str = Field(..., description="Privacy masked plate string")
    confidence: float = Field(..., description="Recognition confidence percentage (0-100)")
    isRegistered: bool = Field(False, description="Whether registered in FreeWay Community")


class ALPRScanResponse(BaseModel):
    """Response returned upon scanning a license plate image."""
    success: bool
    primaryPlate: Optional[str] = None
    maskedPlate: Optional[str] = None
    confidence: float = 0.0
    candidates: List[PlateCandidate] = []
    isRegistered: bool = False
    provider: str = "mock"
    message: str
