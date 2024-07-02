from datetime import (
    UTC,
    datetime,
)


def now_utc() -> datetime:
    """Return the current time in UTC timezone."""
    return datetime.now(UTC)


def utc_from_timestamp(timestamp: str | float) -> datetime:
    """Return UTC time from a timestamp."""
    return datetime.fromtimestamp(float(timestamp), UTC)
