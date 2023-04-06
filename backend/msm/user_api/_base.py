from fastapi import (
    Depends,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .. import (
    __version__,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    schema,
)
from ..db import (
    db_session,
    queries,
)


async def pagination_parameters(
    page: int = Query(default=1, gte=1),
    size: int = Query(default=DEFAULT_PAGE_SIZE, lte=MAX_PAGE_SIZE, gte=1),
) -> dict[str, int]:
    """Make parameters for pagination accessible as a dict"""
    return {"page": page, "size": size, "offset": (page - 1) * size}


async def root() -> dict[str, str]:
    return {"version": __version__}


async def sites(
    city: list[str] | None = Query(default=None, title="Filter for cities"),
    name: list[str] | None = Query(default=None, title="Filter for names"),
    note: list[str] | None = Query(default=None, title="Filter for notes"),
    region: list[str] | None = Query(default=None, title="Filter for regions"),
    street: list[str] | None = Query(default=None, title="Filter for streets"),
    timezone: list[str]
    | None = Query(default=None, title="Filter for timezones"),
    url: list[str] | None = Query(default=None, title="Filter for urls"),
    session: AsyncSession = Depends(db_session),
    pagination_params: dict[str, int] = Depends(pagination_parameters),
) -> schema.PaginatedSites:
    """Return all sites"""
    total, results = await queries.get_filtered_sites(
        session,
        pagination_params["offset"],
        pagination_params["size"],
        city,
        name,
        note,
        region,
        street,
        timezone,
        url,
    )
    return schema.PaginatedSites(
        total=total,
        page=pagination_params["page"],
        size=pagination_params["size"],
        items=list(results),
    )


async def tokens(
    session: AsyncSession = Depends(db_session),
    pagination_params: dict[str, int] = Depends(pagination_parameters),
) -> schema.PaginatedTokens:
    """Return all tokens"""
    total, results = await queries.get_tokens(
        session, pagination_params["offset"], pagination_params["size"]
    )
    return schema.PaginatedTokens(
        total=total,
        page=pagination_params["page"],
        size=pagination_params["size"],
        items=list(results),
    )


async def tokens_post(
    create_request: schema.CreateTokensRequest,
    session: AsyncSession = Depends(db_session),
) -> schema.CreateTokensResponse:
    """
    Create one or more tokens.
    Token duration (TTL) is expressed in seconds.
    """
    expired, tokens = await queries.create_tokens(
        session,
        create_request.duration,
        count=create_request.count,
    )
    return schema.CreateTokensResponse(expired=expired, tokens=tokens)
