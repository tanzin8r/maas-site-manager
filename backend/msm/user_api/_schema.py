from datetime import (
    datetime,
    timedelta,
)
from uuid import UUID

from pydantic import BaseModel

from ..db.models import (
    PendingSite,
    Site,
    Token,
)
from ..schema import PaginatedResults


class RootGetResponse(BaseModel):
    """Root handler response."""

    version: str


class TokensGetResponse(PaginatedResults):
    """List of existing tokens."""

    items: list[Token]


class TokensPostRequest(BaseModel):
    """
    Request to create one or more tokens, with a certain validity,
    expressed in seconds.
    """

    count: int = 1
    duration: timedelta


class TokensPostResponse(BaseModel):
    """List of created tokens, along with their duration."""

    expired: datetime
    tokens: list[UUID]


class SitesGetResponse(PaginatedResults):
    items: list[Site]


class PendingSitesGetResponse(PaginatedResults):
    items: list[PendingSite]


class PendingSitesPostRequest(BaseModel):
    """Request to accept/reject sites."""

    ids: list[int]
    accept: bool


class LoginPostRequest(BaseModel):
    """User login request schema."""

    username: str
    password: str


class LoginPostResponse(BaseModel):
    """User login response with JSON Web Token."""

    access_token: str
    token_type: str
