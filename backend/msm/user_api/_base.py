from fastapi import (
    Depends,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .. import (
    __version__,
    schema,
)
from ..db import (
    db_session,
    queries,
)


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
) -> list[schema.Site]:
    """Return all sites"""
    return list(
        await queries.get_filtered_sites(
            session,
            city,
            name,
            note,
            region,
            street,
            timezone,
            url,
        )
    )


async def tokens(
    session: AsyncSession = Depends(db_session),
) -> list[schema.Token]:
    """Return all tokens"""
    return list(await queries.get_tokens(session))


async def tokens_post(
    create_request: schema.CreateTokensRequest,
    session: AsyncSession = Depends(db_session),
) -> schema.CreateTokensResponse:
    """
    Create one or more tokens.
    Token duration (TTL) is expressed in seconds.
    """
    expiration, tokens = await queries.create_tokens(
        session,
        create_request.duration,
        count=create_request.count,
    )
    return schema.CreateTokensResponse(expiration=expiration, tokens=tokens)
