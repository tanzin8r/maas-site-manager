from datetime import (
    datetime,
    timezone,
)


def now_utc() -> datetime:
    """Return the current time in UTC timezone."""
    return datetime.now(timezone.utc)


def utc_from_timestamp(timestamp: str | float) -> datetime:
    """Return UTC time from a timestamp."""
    return datetime.fromtimestamp(float(timestamp), timezone.utc)
