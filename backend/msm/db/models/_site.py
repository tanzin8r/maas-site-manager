from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

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

    machines_total: int
    machines_allocated: int
    machines_deployed: int
    machines_ready: int
    machines_error: int
    machines_other: int
    last_seen: datetime


class SiteUpdate(BaseModel):
    """The allowed updates to a Site from a user."""

    city: str | None = None
    country: str | None = Field(default=None, min_length=2, max_length=2)
    coordinates: tuple[
        float, float
    ] | None  # first item is the lon, second is the lat
    note: str | None = None
    state: str | None = None
    address: str | None = None
    postal_code: str | None = None
    # XXX: mypy can't grok that this is an str/enum with lots of members
    timezone: TimeZone | None = None  # type: ignore[valid-type]


class Site(BaseModel):
    """A MAAS installation."""

    id: int
    name: str
    city: str = ""
    country: str = ""
    coordinates: tuple[
        float, float
    ] | None  # first item is the lon, second is the lat
    note: str = ""
    state: str = ""
    address: str = ""
    postal_code: str = ""
    # XXX: mypy can't grok that this is an str/enum with lots of members
    timezone: TimeZone | Literal[""] = ""  # type: ignore[valid-type]
    url: str = ""
    name_unique: bool
    connection_status: ConnectionStatus
    stats: SiteData | None = None


class SiteCoordinates(BaseModel):
    """Coordinates for a MAAS site."""

    id: int
    coordinates: tuple[
        float, float
    ] | None = None  # first item is the lon, second is the lat


class PendingSite(BaseModel):
    """A pending MAAS site."""

    id: int
    name: str
    url: str
    created: datetime


class EnrollingSite(BaseModel):
    """Details for a site that's in the enrollment process."""

    id: int
    accepted: bool


class PendingSiteCreate(BaseModel):
    """Details to create a pending site."""

    name: str
    url: str
    auth_id: UUID
