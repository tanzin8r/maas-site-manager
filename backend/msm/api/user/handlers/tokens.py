from datetime import timedelta
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from pydantic import BaseModel

from msm.api._csv import CSVResponse
from msm.api._dependencies import (
    config,
    services,
)
from msm.api.exceptions.catalog import NotFoundException
from msm.api.exceptions.constants import ExceptionCode
from msm.api.user._auth import authenticated_user
from msm.api.user._forms import (
    TokenFilterParams,
    token_filter_parameters,
)
from msm.db.models import (
    Config,
    Token,
    User,
)
from msm.schema import (
    PaginatedResults,
    PaginationParams,
)
from msm.service import ServiceCollection

v1_router = APIRouter(prefix="/v1")


class TokensGetResponse(PaginatedResults):
    """List of existing tokens."""

    items: list[Token]


@v1_router.get("/tokens")
async def get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    pagination_params: Annotated[PaginationParams, Depends()],
    filter_params: Annotated[
        TokenFilterParams, Depends(token_filter_parameters)
    ],
) -> TokensGetResponse:
    """Return all tokens."""
    total, results = await services.tokens.get(
        pagination_params.offset, pagination_params.size, *filter_params
    )
    return TokensGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        **filter_params._asdict(),
        items=list(results),
    )


class TokensPostRequest(BaseModel):
    """Request to create one or more tokens, with a certain validity."""

    count: int = 1
    duration: timedelta


class TokensPostResponse(BaseModel):
    """Response containing generated tokens."""

    items: list[Token]


@v1_router.post("/tokens")
async def post(
    config: Annotated[Config, Depends(config)],
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    post_request: TokensPostRequest,
) -> TokensPostResponse:
    """Create enrolment tokens for sites.

    Token duration (TTL) is expressed as an ISO-8601 duration string.
    """
    service_url = await services.settings.get_service_url()
    tokens = await services.tokens.create(
        issuer=config.service_identifier,
        duration=post_request.duration,
        count=post_request.count,
        secret_key=config.token_secret_key,
        service_url=service_url,
    )
    return TokensPostResponse(items=list(tokens))


@v1_router.get("/tokens/export")
async def get_export(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    pagination_params: Annotated[PaginationParams, Depends()],
    filter_params: Annotated[
        TokenFilterParams, Depends(token_filter_parameters)
    ],
) -> CSVResponse:
    """Return the list of active tokens in CSV format."""
    _, tokens = await services.tokens.get(
        pagination_params.offset, pagination_params.size, *filter_params
    )
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


@v1_router.delete("/tokens", status_code=204)
async def delete_many(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[Token, Depends(authenticated_user)],
    ids: Annotated[list[int], Query()],
) -> None:
    """Delete several tokens from the database"""
    requested_ids = set(ids)
    deleted_ids = await services.tokens.delete_many(ids)
    if deleted_ids != requested_ids:
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message=f"The following ID's were not found: {requested_ids - deleted_ids}.",
        )
    return None
