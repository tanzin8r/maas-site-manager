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


class PaginatedSites(PaginatedResults):
    items: list[Site]


class PaginatedPendingSites(PaginatedResults):
    items: list[PendingSite]


class PaginatedTokens(PaginatedResults):
    items: list[Token]


class UserLoginRequest(BaseModel):
    """User login request schema."""

    username: str
    password: str


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
