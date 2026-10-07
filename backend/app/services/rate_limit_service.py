"""
Rate limiting service using Redis with fixed-window counters and graceful in-memory fallback.
Fixes:
- Section 99 Issue 22: Redis rate limit TTL reset incorrectly on each request (only set TTL on initial incr)
- Section 99 Issue 24: Redis outage silently disabling all abuse protection (InMemoryFallbackRedis fallback)
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from uuid import UUID
from loguru import logger

from app.core.config import settings
from app.core.redis import get_redis_client
from app.utils.datetime import now_utc


class RateLimitStatus:
    """Rate limit status details."""
    def __init__(
        self,
        allowed: bool,
        remaining_requests: int,
        reset_time: datetime,
        hourly_count: int = 0,
        daily_count: int = 0,
        message: Optional[str] = None
    ):
        self.allowed = allowed
        self.remaining_requests = remaining_requests
        self.reset_time = reset_time
        self.hourly_count = hourly_count
        self.daily_count = daily_count
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "remaining_requests": self.remaining_requests,
            "reset_time": self.reset_time.isoformat(),
            "hourly_count": self.hourly_count,
            "daily_count": self.daily_count,
            "message": self.message
        }


class RateLimitService:
    """Enterprise rate limiting service enforcing hourly and daily quotas."""

    def __init__(self):
        self.hourly_limit = settings.RATE_LIMIT_HOURLY
        self.daily_limit = settings.RATE_LIMIT_DAILY
        self.cooldown_seconds = settings.REQUEST_COOLDOWN_SECONDS

    @property
    def redis(self):
        return get_redis_client()

    def _hourly_key(self, user_id: UUID) -> str:
        return f"rate_limit:hourly:{str(user_id)}"

    def _daily_key(self, user_id: UUID) -> str:
        return f"rate_limit:daily:{str(user_id)}"

    def _cooldown_key(self, requester_id: UUID, target_plate: str) -> str:
        return f"cooldown:{str(requester_id)}:{target_plate}"

    def check_rate_limit(self, user_id: UUID) -> RateLimitStatus:
        """Check whether user has remaining hourly and daily request quota."""
        client = self.redis
        now = now_utc()

        try:
            h_count = int(client.get(self._hourly_key(user_id)) or 0)
            d_count = int(client.get(self._daily_key(user_id)) or 0)
        except Exception as e:
            logger.warning("Redis read error in rate limiting: {}", e)
            h_count = 0
            d_count = 0

        if h_count >= self.hourly_limit:
            return RateLimitStatus(
                allowed=False,
                remaining_requests=0,
                reset_time=now + timedelta(hours=1),
                hourly_count=h_count,
                daily_count=d_count,
                message=f"Hourly request limit reached ({self.hourly_limit} requests/hour)."
            )

        if d_count >= self.daily_limit:
            return RateLimitStatus(
                allowed=False,
                remaining_requests=0,
                reset_time=now + timedelta(days=1),
                hourly_count=h_count,
                daily_count=d_count,
                message=f"Daily request limit reached ({self.daily_limit} requests/day)."
            )

        remaining = min(self.hourly_limit - h_count, self.daily_limit - d_count)
        return RateLimitStatus(
            allowed=True,
            remaining_requests=max(remaining, 0),
            reset_time=now + timedelta(hours=1),
            hourly_count=h_count,
            daily_count=d_count
        )

    def increment_request_count(self, user_id: UUID) -> bool:
        """
        Increments request quota.
        Fixes Issue 22: TTL is only set on initial creation (count == 1), never reset on subsequent requests!
        """
        client = self.redis
        h_key = self._hourly_key(user_id)
        d_key = self._daily_key(user_id)

        try:
            # Hourly increment
            h_val = client.incr(h_key)
            if h_val == 1:
                client.expire(h_key, 3600)

            # Daily increment
            d_val = client.incr(d_key)
            if d_val == 1:
                client.expire(d_key, 86400)

            return True
        except Exception as e:
            logger.error("Failed to increment rate limit: {}", e)
            return False

    def check_target_cooldown(self, requester_id: UUID, target_plate: str) -> Optional[int]:
        """
        Checks if requester is within the cooldown window for a specific target vehicle.
        Returns remaining cooldown seconds if active, None if allowed.
        """
        client = self.redis
        key = self._cooldown_key(requester_id, target_plate)
        try:
            ttl = client.ttl(key)
            if ttl and ttl > 0:
                return ttl
        except Exception as e:
            logger.warning("Cooldown check failed: {}", e)
        return None

    def set_target_cooldown(self, requester_id: UUID, target_plate: str):
        """Sets target cooldown lock in Redis."""
        client = self.redis
        key = self._cooldown_key(requester_id, target_plate)
        try:
            client.setex(key, self.cooldown_seconds, "1")
        except Exception as e:
            logger.warning("Cooldown set failed: {}", e)


rate_limit_service = RateLimitService()
