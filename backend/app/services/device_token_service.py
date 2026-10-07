"""
DeviceToken management and stale token cleanup service.
Fixes:
- Section 99 Issue 12: Manages push tokens in DeviceToken table
- Section 99 Issue 26: Provides automated stale token cleanup function
"""
from typing import Optional, List
from uuid import UUID
from datetime import timedelta
from sqlalchemy.orm import Session
from loguru import logger

from app.models.device_token import DeviceToken
from app.utils.datetime import now_utc


class DeviceTokenService:
    """Manages FCM / Expo push device tokens and lifecycle."""

    def register_token(
        self,
        db: Session,
        user_id: UUID,
        token: str,
        device_type: str = "ANDROID"
    ) -> DeviceToken:
        """Registers or activates a device token for a user."""
        existing = db.query(DeviceToken).filter(DeviceToken.token == token).first()
        now = now_utc()

        if existing:
            existing.userId = user_id
            existing.deviceType = device_type
            existing.isActive = True
            existing.lastUsedAt = now
            db.commit()
            db.refresh(existing)
            return existing

        new_token = DeviceToken(
            userId=user_id,
            token=token,
            deviceType=device_type,
            isActive=True,
            createdAt=now,
            lastUsedAt=now
        )
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        return new_token

    def deactivate_token(self, db: Session, token: str) -> bool:
        """Deactivates a token upon logout or uninstall."""
        tok = db.query(DeviceToken).filter(DeviceToken.token == token).first()
        if tok:
            tok.isActive = False
            db.commit()
            return True
        return False

    def cleanup_stale_tokens(self, db: Session, max_inactive_days: int = 90) -> int:
        """
        Removes inactive or expired device tokens older than max_inactive_days.
        Fixes Section 99 Issue 26: Stale token cleanup logic.
        """
        cutoff = now_utc() - timedelta(days=max_inactive_days)
        deleted = db.query(DeviceToken).filter(
            (DeviceToken.isActive == False) | (DeviceToken.lastUsedAt < cutoff)
        ).delete(synchronize_session=False)
        db.commit()
        logger.info("Purged {} stale push notification tokens", deleted)
        return deleted


device_token_service = DeviceTokenService()
