"""
Authentication and security utilities for password hashing and JWT token management.
Uses pure bcrypt to prevent passlib 1.7.4 / bcrypt 5.0 __about__ incompatibility.
Fixes:
- Section 99 Issue 9: JWT expiration using timezone-aware UTC timestamp
- Short-lived access token (in minutes) and long-lived refresh token (in days)
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.utils.datetime import now_utc


def hash_password(password: str) -> str:
    """Hash password using direct bcrypt (10 rounds, 72-byte safe truncation)."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate short-lived JWT access token using timezone-aware UTC timestamp."""
    to_encode = data.copy()
    now = now_utc()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate long-lived JWT refresh token using timezone-aware UTC timestamp."""
    to_encode = data.copy()
    now = now_utc()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "refresh"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT token signature and expiration."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode access token, ensuring type is 'access'."""
    payload = decode_token(token)
    if payload and payload.get("type", "access") == "access":
        return payload
    return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode refresh token, ensuring type is 'refresh'."""
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """Extract user UUID string from token."""
    payload = decode_access_token(token)
    if payload:
        return payload.get("userId") or payload.get("sub")
    return None
