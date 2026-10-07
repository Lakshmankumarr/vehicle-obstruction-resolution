"""
FreeWay Community Backend API
Production FastAPI Application Entrypoint.
"""
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
