from datetime import (
    datetime,
    timedelta,
)
from uuid import UUID

from pydantic import BaseModel


class CreateSite(BaseModel):
    """
    A MAAS installation
    """

    name: str
    identifier: str
    city: str | None
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
    total_machines: int
    # TODO: might include more states in future
    occupied_machines: int  # TODO: name might change
    ready_machines: int
    error_machines: int
    last_seen: datetime


class SiteData(CreateSiteData):
    """
    SiteData persisted to the database
    """

    id: int


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
    expiration: datetime


class Token(CreateToken):
    """
    A token persisted to the database
    """

    id: int


class CreateTokensRequest(BaseModel):
    """
    Request to create one or more tokens, with a certain validity,
    expressed in seconds.
    """

    count: int = 1
    duration: timedelta


class CreateTokensResponse(BaseModel):
    """List of created tokens, along with their duration."""

    expiration: datetime
    tokens: list[UUID]
