from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .. import __version__
from ..db import (
    db_session,
    queries,
)
from ..schema import (
    CreateTokensRequest,
    CreateTokensResponse,
    PaginatedSites,
    PaginatedTokens,
    pagination_params,
    PaginationParams,
)
from ._forms import (
    site_filter_parameters,
    SiteFilterParams,
)


async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"version": __version__}


async def sites(
    session: AsyncSession = Depends(db_session),
    pagination_params: PaginationParams = Depends(pagination_params),
    filter_params: SiteFilterParams = Depends(site_filter_parameters),
) -> PaginatedSites:
    """Return all sites."""
    total, results = await queries.get_filtered_sites(
        session,
        offset=pagination_params.offset,
        limit=pagination_params.size,
        **filter_params._asdict(),
    )
    return PaginatedSites(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


async def tokens(
    session: AsyncSession = Depends(db_session),
    pagination_params: PaginationParams = Depends(pagination_params),
) -> PaginatedTokens:
    """Return all tokens"""
    total, results = await queries.get_tokens(
        session, pagination_params.offset, pagination_params.size
    )
    return PaginatedTokens(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


async def tokens_post(
    create_request: CreateTokensRequest,
    session: AsyncSession = Depends(db_session),
) -> CreateTokensResponse:
    """
    Create one or more tokens.
    Token duration (TTL) is expressed in seconds.
    """
    expired, tokens = await queries.create_tokens(
        session,
        create_request.duration,
        count=create_request.count,
    )
    return CreateTokensResponse(expired=expired, tokens=tokens)
