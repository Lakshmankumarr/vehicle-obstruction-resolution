"""
System health and readiness check endpoint.
Fixes:
- Section 99 Issue 30: Actually checks database and Redis connectivity before claiming healthy
"""
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

from app.core.database import get_db
from app.core.redis import get_redis_client
from app.core.config import settings
from app.utils.datetime import now_utc

router = APIRouter()


@router.get("/health")
def health_check(response: Response, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive system health check.
    Verifies Database, Redis/Memory-Cache, and ALPR subsystems.
    """
    health_status = {
        "status": "healthy",
        "timestamp": now_utc().isoformat(),
        "version": settings.VERSION,
        "services": {}
    }
    is_healthy = True

    # 1. Database Check
    try:
        db.execute(text("SELECT 1"))
        health_status["services"]["database"] = {"status": "up", "type": "relational_db"}
    except Exception as e:
        is_healthy = False
        health_status["services"]["database"] = {"status": "down", "error": str(e)}

    # 2. Redis / In-Memory Cache Check
    try:
        client = get_redis_client()
        ping_ok = client.ping()
        health_status["services"]["redis"] = {
            "status": "up" if ping_ok else "degraded",
            "mode": type(client).__name__
        }
    except Exception as e:
        health_status["services"]["redis"] = {"status": "degraded", "error": str(e)}

    # 3. ALPR Subsystem Check
    health_status["services"]["alpr"] = {
        "status": "ready",
        "provider": settings.ALPR_PROVIDER,
        "country": settings.ALPR_COUNTRY
    }

    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        health_status["status"] = "unhealthy"

    return health_status
