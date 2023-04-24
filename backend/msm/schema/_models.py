from datetime import (
    datetime,
    timedelta,
)
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    SecretStr,
)
from pydantic.fields import Field
import pytz
from strenum import StrEnum

from ._pagination import PaginatedResults

# Enum with timezones accepted by pytz.
TimeZone = StrEnum("TimeZone", pytz.all_timezones)


class ReadUser(BaseModel):
    """
    A MAAS Site Manager User
    We never want to sent the password (hash) around
    """

    email: EmailStr = Field(title="email@example.com")
    full_name: str


class UserWithPassword(ReadUser):
    """
    To create a user we need a password as well.
    """

    # use password.get_secret_value() to retrieve the value
    password: SecretStr = Field(min_length=8, max_length=100)


class User(ReadUser):
    """
    To read a user from the DB it comes with an ID
    """

    id: int


class UserLoginRequest(BaseModel):
    """User login details."""

    username: str
    password: str


class CreateSite(BaseModel):
    """
    A MAAS installation
    """

    name: str
    city: str | None
    country: str | None = Field(min_length=2, max_length=2)
    latitude: str | None
    longitude: str | None
    note: str | None
    region: str | None
    street: str | None
    timezone: TimeZone | None  # type: ignore
    url: str
    # TODO: we will need to add tags


class SiteData(BaseModel):
    """Data for a site"""

    allocated_machines: int
    deployed_machines: int
    ready_machines: int
    error_machines: int
    last_seen: datetime


class Site(CreateSite):
    """
    Site persisted to the database
    """

    id: int
    stats: SiteData | None


class CreateSiteData(SiteData):
    """Site data"""

    site_id: int


class PaginatedSites(PaginatedResults):
    items: list[Site]


class SiteWithData(Site):

    """
    A site, together with its SiteData
    """

    id: int
    site_data: SiteData


class CreateToken(BaseModel):
    """
    To create a token a value and an expiration
    time need to be generated
    """

    site_id: int | None
    value: UUID
    expired: datetime
    created: datetime


class Token(CreateToken):
    """
    A token persisted to the database
    """

    id: int


class JSONWebToken(BaseModel):
    """
    A JSON Web Token for authenticating users.
    """

    access_token: str
    token_type: str


class JSONWebTokenData(BaseModel):
    """
    The payload data for a JWT Token
    """

    email: str


class PaginatedTokens(PaginatedResults):
    items: list[Token]


class CreateTokensRequest(BaseModel):
    """
    Request to create one or more tokens, with a certain validity,
    expressed in seconds.
    """

    count: int = 1
    duration: timedelta


class CreateTokensResponse(BaseModel):
    """List of created tokens, along with their duration."""

    expired: datetime
    tokens: list[UUID]
