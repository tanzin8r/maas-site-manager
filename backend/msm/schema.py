from collections.abc import Sequence
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

from msm import MAX_PAGE_SIZE


class PaginatedResults(BaseModel):
    """
    Base class to wrap objects in a pagination.
    Derived classes should overwrite the items property
    """

    total: int = Field(min=0)
    page: int = Field(min=0)
    size: int = Field(min=0, max=MAX_PAGE_SIZE)
    items: Sequence[BaseModel]


class CreateUser(BaseModel):
    """
    A MAAS Site Manager User
    """

    email: EmailStr = Field(title="email@example.com")
    full_name: str
    # use password.get_secret_value() to retrieve the value
    password: SecretStr = Field(min_length=8, max_length=50)
    disabled: bool


class User(CreateUser):
    id: int


class CreateSite(BaseModel):
    """
    A MAAS installation
    """

    name: str
    city: str | None
    country: str | None
    latitude: str | None
    longitude: str | None
    note: str | None
    region: str | None
    street: str | None
    timezone: str | None
    url: str
    # TODO: we will need to add tags


class Site(CreateSite):
    """
    Site persisted to the database
    """

    id: int


class CreateSiteData(BaseModel):
    """
    All SiteData is obligatory
    """

    site_id: int
    allocated_machines: int
    deployed_machines: int
    ready_machines: int
    error_machines: int
    last_seen: datetime


class SiteData(CreateSiteData):
    """
    SiteData persisted to the database
    """

    id: int


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
