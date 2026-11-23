"""
FreeWay Community Backend API
Production FastAPI Application Entrypoint.
"""
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.v1 import api_router
from app.services.request_service import request_service
from app.services.device_token_service import device_token_service
from app.models.request import Request, RequestStatus
from app.utils.datetime import now_utc

# Configure structured logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL,
    serialize=False
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL,
    serialize=True
)

scheduler = BackgroundScheduler()


def run_scheduled_maintenance():
    """Background task to expire old pending requests and purge stale tokens."""
    db = SessionLocal()
    try:
        # 1. Expire requests older than expiresAt
        now = now_utc()
        expired_count = db.query(Request).filter(
            Request.status == RequestStatus.PENDING.value,
            Request.expiresAt <= now
        ).update({"status": RequestStatus.EXPIRED.value})
        db.commit()
        if expired_count > 0:
            logger.info("Auto-expired {} pending obstruction requests", expired_count)

        # 2. Cleanup stale push tokens (Section 99 Issue 26)
        device_token_service.cleanup_stale_tokens(db, max_inactive_days=settings.DATA_RETENTION_DAYS)
    except Exception as e:
        logger.error("Maintenance task error: {}", e)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks."""
    logger.info("Initializing FreeWay Community API v{}", settings.VERSION)

    # Create tables on startup for local / test environments
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized.")
    except Exception as e:
        logger.error("Database schema initialization warning: {}", e)

    # Start background scheduler
    try:
        scheduler.add_job(
            run_scheduled_maintenance,
            "interval",
            minutes=2,
            id="maintenance_job",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Background maintenance scheduler started (every 2 minutes)")
    except Exception as e:
        logger.warning("Could not start scheduler: {}", e)

    yield

    logger.info("Shutting down FreeWay Community API...")
    try:
        scheduler.shutdown(wait=False)
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Privacy-focused Vehicle Obstruction Resolution Platform",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API V1 Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "apiPrefix": settings.API_V1_PREFIX
    }


@app.get("/health")
def health():
    """Liveness probe - returns OK if application is running"""
    return {"status": "ok"}


@app.get("/ready")
def ready():
    """Readiness probe - returns OK if application can serve traffic"""
    from app.core.database import engine
    from app.core.redis import get_redis_client
    from sqlalchemy import text

    # Check database connectivity
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("Database readiness check failed: {}", e)
        return {"status": "not_ready", "database": "disconnected", "error": str(e)}

    # Check Redis connectivity (optional - has fallback)
    redis_status = "connected"
    try:
        redis_client = get_redis_client()
        redis_client.ping()
    except Exception as e:
        logger.warning("Redis readiness check failed (using fallback): {}", e)
        redis_status = "fallback"

    return {
        "status": "ready",
        "database": "connected",
        "redis": redis_status,
        "version": settings.VERSION
    }
