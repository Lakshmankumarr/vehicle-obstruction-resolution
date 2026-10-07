"""
Time and timezone utilities for FreeWay Community.
Fixes:
- Section 99 Issue 7: UTC and IST mixed in database
- Section 99 Issue 8: timezone-naive datetime storage
- Section 99 Issue 9: JWT expiration using ambiguous naive datetime
- Provides ensure_utc() helper to normalize SQLite/Postgres datetimes
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import pytz

UTC = timezone.utc
IST = pytz.timezone("Asia/Kolkata")


def now_utc() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensures datetime is timezone-aware UTC (fixes SQLite naive datetime readback)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def to_ist(utc_dt: Optional[datetime]) -> Optional[datetime]:
    """Converts a UTC datetime into IST (Asia/Kolkata)."""
    if utc_dt is None:
        return None
    dt = ensure_utc(utc_dt)
    return dt.astimezone(IST)


def format_ist(utc_dt: Optional[datetime], fmt: str = "%d/%m/%Y, %I:%M %p IST") -> str:
    """Formats a UTC datetime for human-readable Indian Standard Time display."""
    if utc_dt is None:
        return "N/A"
    ist_dt = to_ist(utc_dt)
    return ist_dt.strftime(fmt)


def to_iso_utc(utc_dt: Optional[datetime]) -> Optional[str]:
    """Converts a UTC datetime into an ISO 8601 string with 'Z' suffix."""
    if utc_dt is None:
        return None
    dt = ensure_utc(utc_dt)
    return dt.isoformat().replace("+00:00", "Z")
