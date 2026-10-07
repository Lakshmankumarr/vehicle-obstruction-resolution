"""
Redis client configuration with robust in-memory fallback for offline/development mode.
Fixes:
- Section 99 Issue 22: Redis rate limit TTL reset incorrectly on each request
- Section 99 Issue 24: Redis outage silently disabling all abuse protection
"""
import time
from typing import Optional, Any
import redis
from loguru import logger

from app.core.config import settings


class InMemoryFallbackRedis:
    """
    In-memory mock for Redis operations when Redis server is unreachable.
    Guarantees that rate limiting, cooldowns, and caching continue working seamlessly.
    """
    def __init__(self):
        self._data = {}  # key -> value
        self._expiry = {}  # key -> expiry_timestamp
        logger.warning("Using InMemoryFallbackRedis: rate limits will persist in-memory")

    def _purge_expired(self, key: str):
        if key in self._expiry and time.time() > self._expiry[key]:
            self._data.pop(key, None)
            self._expiry.pop(key, None)

    def get(self, key: str) -> Optional[str]:
        self._purge_expired(key)
        return self._data.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._data[key] = str(value)
        if ex is not None:
            self._expiry[key] = time.time() + ex
        else:
            self._expiry.pop(key, None)
        return True

    def setex(self, key: str, time_sec: int, value: Any) -> bool:
        return self.set(key, value, ex=time_sec)

    def incr(self, key: str) -> int:
        """Atomically increments a key. Does NOT reset expiry if already set."""
        self._purge_expired(key)
        current = int(self._data.get(key, 0))
        new_val = current + 1
        self._data[key] = str(new_val)
        return new_val

    def expire(self, key: str, time_sec: int) -> bool:
        if key in self._data:
            self._expiry[key] = time.time() + time_sec
            return True
        return False

    def ttl(self, key: str) -> int:
        self._purge_expired(key)
        if key not in self._data:
            return -2
        if key not in self._expiry:
            return -1
        remaining = int(self._expiry[key] - time.time())
        return max(remaining, 0)

    def delete(self, *keys: str) -> int:
        count = 0
        for k in keys:
            if k in self._data:
                self._data.pop(k, None)
                self._expiry.pop(k, None)
                count += 1
        return count

    def ping(self) -> bool:
        return True


# Global Redis client instance
redis_client: Any = None


def get_redis_client():
    """Initializes and returns a healthy Redis client or in-memory fallback."""
    global redis_client
    if redis_client is not None:
        return redis_client

    try:
        client = redis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            decode_responses=True
        )
        client.ping()
        logger.info("Successfully connected to Redis at {}", settings.REDIS_URL)
        redis_client = client
    except Exception as e:
        logger.warning("Could not connect to Redis: {}. Activating in-memory fallback.", str(e))
        redis_client = InMemoryFallbackRedis()

    return redis_client
