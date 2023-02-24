from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import _schema as schema
from .. import __version__
from ..db import (
    db_session,
    queries,
)


async def root() -> dict[str, str]:
    return {"version": __version__}


async def sites(
    session: AsyncSession = Depends(db_session),
) -> list[schema.Site]:
    """Return all sites"""
    return [schema.Site(**entry) for entry in await queries.get_sites(session)]


async def tokens(
    session: AsyncSession = Depends(db_session),
) -> list[schema.Token]:
    """Return all tokens"""
    return [
        schema.Token(**entry) for entry in await queries.get_tokens(session)
    ]


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
