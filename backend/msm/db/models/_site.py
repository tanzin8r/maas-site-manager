from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
)

from ...schema import TimeZone


class ConnectionStatus(str, Enum):
    STABLE = "stable"
    LOST = "lost"
    UNKNOWN = "unknown"


class SiteData(BaseModel):
    """Data for a site."""

    total_machines: int
    allocated_machines: int
    deployed_machines: int
    ready_machines: int
    error_machines: int
    other_machines: int
    last_seen: datetime


class Site(BaseModel):
    """A MAAS installation."""

    id: int
    name: str
    name_unique: bool
    city: str | None = None
    country: str | None = Field(default=None, min_length=2, max_length=2)
    latitude: str | None = None
    longitude: str | None = None
    note: str | None = None
    region: str | None = None
    street: str | None = None
    # XXX: mypy can't grok that this is an str/enum with lots of members
    timezone: TimeZone | None = None  # type: ignore
    url: str
    connection_status: ConnectionStatus
    stats: SiteData | None = None


class SiteCoordinates(BaseModel):
    """Coordinates for a MAAS site."""

    id: int
    latitude: str | None = None
    longitude: str | None = None


class PendingSite(BaseModel):
    """A pending MAAS site."""

    id: int
    name: str
    url: str
    created: datetime
