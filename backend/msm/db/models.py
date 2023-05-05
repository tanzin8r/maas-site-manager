from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
)

from ..schema import TimeZone


class SiteData(BaseModel):
    """Data for a site."""

    allocated_machines: int
    deployed_machines: int
    ready_machines: int
    error_machines: int
    last_seen: datetime


class Site(BaseModel):
    """A MAAS installation."""

    id: int
    name: str
    city: str | None
    country: str | None = Field(min_length=2, max_length=2)
    latitude: str | None
    longitude: str | None
    note: str | None
    region: str | None
    street: str | None
    timezone: TimeZone | None
    url: str
    stats: SiteData | None


class PendingSite(BaseModel):
    """A pending MAAS site."""

    id: int
    name: str
    url: str
    created: datetime


class Token(BaseModel):
    """A registration token for a site."""

    id: int
    value: UUID
    site_id: int | None
    expired: datetime
    created: datetime


class User(BaseModel):
    """A user."""

    id: int
    email: EmailStr = Field(title="email@example.com")
    full_name: str


class UserWithPassword(User):
    """A user with its password."""

    # use password.get_secret_value() to retrieve the value
    password: SecretStr = Field(min_length=8, max_length=100)
