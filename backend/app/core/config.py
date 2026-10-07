"""
Application configuration settings for FreeWay Community.
All configuration is loaded via Pydantic Settings with secure defaults and .env support.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """FreeWay Community Core Configuration Settings"""
    
    # Project Info
    PROJECT_NAME: str = "FreeWay Community API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Security & JWT
    SECRET_KEY: str = Field(
        default="freeway-jwt-secret-key-production-ready-32-chars-minimum-token",
        description="Secret key used for HMAC JWT signature"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Section 99 Issue 9: access token in minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database (Defaults to SQLite for seamless local dev & pytest; Postgres in Docker/Prod)
    DATABASE_URL: str = Field(
        default="sqlite:///./freeway.db",
        description="Database connection URI"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis (with graceful fallback if unavailable)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: float = 2.0
    
    # Push Notifications
    NOTIFICATION_PROVIDER: str = "mock"  # "mock", "console", "firebase"
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # ALPR (Automatic License Plate Recognition)
    ALPR_PROVIDER: str = "mock"  # "mock", "plate_recognizer", "openalpr"
    ALPR_COUNTRY: str = "in"  # Section 99 Issue 21: India region
    PLATE_RECOGNIZER_API_KEY: Optional[str] = None
    OPENALPR_SECRET_KEY: Optional[str] = None
    ALPR_CONFIDENCE_THRESHOLD: float = 70.0
    
    # Image Settings
    MAX_IMAGE_SIZE_MB: int = 10  # Section 99 Issue 31: Enforced during upload
    MAX_IMAGE_DIMENSION: int = 1920
    
    # Rate Limiting
    RATE_LIMIT_HOURLY: int = 30
    RATE_LIMIT_DAILY: int = 150
    REQUEST_COOLDOWN_SECONDS: int = 120  # Cooldown between duplicate requests to same target
    
    # Request Settings
    REQUEST_EXPIRY_MINUTES: int = 30
    
    # Abuse Detection & Moderation
    STRIKE_THRESHOLD: int = 3  # 3 valid reports trigger auto-restriction
    MAX_UNRESOLVED_REQUESTS: int = 5
    
    # Data Retention
    DATA_RETENTION_DAYS: int = 90
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:19006",
        "http://127.0.0.1:8081",
        "*"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
