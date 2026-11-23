"""
Push notification delivery service for FreeWay Community.
Fixes:
- Section 99 Issue 12: Uses DeviceToken table exclusively
- Section 99 Issue 27: Asynchronous delivery via background thread, never blocks API thread
- Provides robust Mock/Console notification provider for offline/development/test modes
"""
import threading
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.orm import Session
from loguru import logger

from app.core.config import settings
from app.models.user import User
from app.models.device_token import DeviceToken


class NotificationService:
    """Manages push notification dispatch across platforms."""

    def __init__(self):
        self.provider = settings.NOTIFICATION_PROVIDER
        self.in_memory_notifications: List[Dict[str, Any]] = []

    def _deliver_in_background(self, tokens: List[str], title: str, body: str, data: Dict[str, Any]):
        """Worker thread logic for non-blocking push dispatch."""
        try:
            if self.provider == "firebase" and settings.FIREBASE_CREDENTIALS_PATH:
                from app.services.firebase_service import firebase_service
                # Ensure Firebase is initialized
                if not firebase_service.is_initialized():
                    firebase_service.initialize()
                for t in tokens:
                    firebase_service.send_push(token=t, title=title, body=body, data=data)
            else:
                # Mock / Console mode
                logger.info("[PUSH NOTIFICATION] To {} tokens | Title: {} | Body: {} | Data: {}", len(tokens), title, body, data)
                self.in_memory_notifications.append({
                    "title": title,
                    "body": body,
                    "data": data,
                    "token_count": len(tokens)
                })
        except Exception as e:
            logger.error("Background notification delivery error: {}", e)

    def dispatch_notification(
        self,
        db: Session,
        user_id: UUID,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Retrieves active device tokens and spawns a daemon thread for delivery.
        Guarantees that notification network latency never blocks the HTTP response.
        """
        payload_data = data or {}
        # Fetch active device tokens
        tokens = [
            dt.token for dt in db.query(DeviceToken).filter(
                DeviceToken.userId == user_id,
                DeviceToken.isActive == True
            ).all()
        ]

        if not tokens:
            logger.info("No active device tokens found for user {}; recorded in-app only", user_id)
            # Record in-memory for testing
            self.in_memory_notifications.append({
                "title": title,
                "body": body,
                "data": payload_data,
                "user_id": str(user_id)
            })
            return

        # Fire and forget in daemon thread (Fixes Issue 27)
        worker = threading.Thread(
            target=self._deliver_in_background,
            args=(tokens, title, body, payload_data),
            daemon=True
        )
        worker.start()

    def send_obstruction_alert(
        self,
        db: Session,
        target_user: User,
        request_id: UUID,
        vehicle_plate: str,
        message: Optional[str]
    ):
        """Alerts the blocking vehicle owner that someone needs them to move."""
        title = "🚗 Vehicle Move Request"
        body = f"Your vehicle {vehicle_plate} is blocking someone. Please move it."
        data = {
            "type": "OBSTRUCTION_REQUEST",
            "requestId": str(request_id),
            "vehicle": vehicle_plate,
            "message": message or ""
        }
        self.dispatch_notification(db=db, user_id=target_user.id, title=title, body=body, data=data)

    def send_response_alert(
        self,
        db: Session,
        requester: User,
        request_id: UUID,
        response_type: str,
        eta_minutes: Optional[int],
        message: Optional[str]
    ):
        """Alerts the requester about the vehicle owner's response and ETA."""
        title = "⚡ Vehicle Owner Responded"
        if response_type == "ON_MY_WAY":
            body = f"Owner is on the way! Estimated time: {eta_minutes or 5} mins."
        elif response_type == "KEYS_WITH_GUARD":
            body = "Keys are with security/guard. You can move the vehicle."
        elif response_type == "CANNOT_MOVE":
            body = "Owner cannot move the vehicle right now: " + (message or "See details in app")
        else:
            body = message or "Owner sent an update regarding your request."

        data = {
            "type": "REQUEST_RESPONSE",
            "requestId": str(request_id),
            "response": response_type,
            "eta": str(eta_minutes or 0)
        }
        self.dispatch_notification(db=db, user_id=requester.id, title=title, body=body, data=data)


notification_service = NotificationService()
