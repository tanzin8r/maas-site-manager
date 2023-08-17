from datetime import (
    datetime,
    timedelta,
)
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)
from pydantic import BaseModel

from ...db.models import (
    Token,
    User,
)
from ...schema import (
    PaginatedResults,
    pagination_params,
    PaginationParams,
)
from ...service import ServiceCollection
from .._auth import authenticated_user
from .._csv import CSVResponse
from .._dependencies import services

v1_router = APIRouter(prefix="/v1")


class TokensGetResponse(PaginatedResults):
    """List of existing tokens."""

    items: list[Token]


@v1_router.get("/tokens")
async def get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    pagination_params: PaginationParams = Depends(pagination_params),
) -> TokensGetResponse:
    """Return all tokens."""
    total, results = await services.tokens.get(
        pagination_params.offset, pagination_params.size
    )
    return TokensGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=results,
    )


class TokensPostRequest(BaseModel):
    """Request to create one or more tokens, with a certain validity."""

    count: int = 1
    duration: timedelta


class TokensPostResponse(BaseModel):
    """List of created tokens, along with their duration."""

    expired: datetime
    tokens: list[UUID]


@v1_router.post("/tokens")
async def post(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    create_request: TokensPostRequest,
) -> TokensPostResponse:
    """Create one or more tokens.

    Token duration (TTL) is expressed as an ISO-8601 duration string.
    """
    expired, tokens = await services.tokens.create(
        create_request.duration,
        count=create_request.count,
    )
    return TokensPostResponse(expired=expired, tokens=list(tokens))


@v1_router.get("/tokens/export")
async def get_export(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
) -> CSVResponse:
    """Return the list of active tokens in CSV format."""
    tokens = await services.tokens.get_active()
    return CSVResponse(content=tokens)


@v1_router.delete("/tokens/{id}", status_code=204)
async def delete(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[Token, Depends(authenticated_user)],
    id: int,
) -> None:
    """Delete a token from the database."""
    await services.tokens.delete(id)
    return None
