"""
Firebase Cloud Messaging service
Validates: Requirements 10.1, 16.1, 16.2, 16.3
"""
import firebase_admin
from firebase_admin import credentials, messaging
from typing import Optional
from loguru import logger
import os

from app.core.config import settings


class FirebaseService:
    """
    Firebase Cloud Messaging service for push notifications

    Validates:
    - Requirement 10.1: Push notification delivery via Firebase
    - Requirement 16.1: Device token storage and management
    - Requirement 16.2: Multiple device support per user
    - Requirement 16.3: Platform type recording (iOS/Android)
    """

    _instance: Optional['FirebaseService'] = None
    _initialized: bool = False

    def __new__(cls):
        """Singleton pattern to ensure only one Firebase instance"""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        """Initialize Firebase Admin SDK (lazy initialization)"""
        if FirebaseService._initialized:
            logger.info("Firebase already initialized, skipping")
            return

        try:
            # Check if credentials file exists
            if not os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                logger.warning(
                    f"Firebase credentials file not found: {settings.FIREBASE_CREDENTIALS_PATH}. "
                    "Firebase notifications will not work."
                )
                return

            # Check if Firebase app already exists
            try:
                firebase_admin.get_app()
                logger.info("Firebase Admin SDK already initialized")
            except ValueError:
                # No app exists, initialize it
                if not os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                    logger.warning(
                        f"Firebase credentials file not found: {settings.FIREBASE_CREDENTIALS_PATH}. "
                        "Firebase notifications will not work."
                    )
                    return

                # Initialize Firebase with service account credentials
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")

            FirebaseService._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            raise

    def is_initialized(self) -> bool:
        """Check if Firebase is initialized"""
        return FirebaseService._initialized

    def send_push(self, token: str, title: str, body: str, data: dict = None):
        """Send push notification to a single device token"""
        if not self.is_initialized():
            logger.warning("Firebase not initialized, cannot send push")
            return False

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        channel_id="freeway_notifications",
                        priority="high",
                        default_sound=True,
                        default_vibrate_timings=True,
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound="default",
                            badge=1,
                            content_available=True,
                        )
                    ),
                ),
            )
            response = messaging.send(message)
            logger.info(f"Push notification sent: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            # Log specific error for debugging
            if "registration token" in str(e).lower() or "invalid" in str(e).lower():
                logger.warning(f"Invalid FCM token: {token[:20]}...")
            return False


# Global Firebase service instance
firebase_service = FirebaseService()