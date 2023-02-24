from collections.abc import Iterable
from datetime import (
    datetime,
    timedelta,
)
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ._tables import (
    Site,
    Token,
)


async def get_sites(session: AsyncSession) -> Iterable[dict[str, Any]]:
    stmt = select(
        Site.c.id,
        Site.c.name,
        Site.c.identifier,
        Site.c.city,
        Site.c.latitude,
        Site.c.longitude,
        Site.c.note,
        Site.c.region,
        Site.c.street,
        Site.c.timezone,
        Site.c.url,
    )
    result = await session.execute(stmt)
    return (row._asdict() for row in result.all())


async def get_tokens(session: AsyncSession) -> Iterable[dict[str, Any]]:
    result = await session.execute(
        select(Token.c.id, Token.c.site_id, Token.c.value, Token.c.expiration)
    )
    return (row._asdict() for row in result.all())


async def create_tokens(
    session: AsyncSession, duration: timedelta, count: int = 1
) -> tuple[datetime, list[UUID]]:
    expiration = datetime.utcnow() + duration
    result = await session.execute(
        Token.insert().returning(Token.c.value),
        [
            {
                "expiration": expiration,
            }
            for _ in range(count)
        ],
    )
    return expiration, [row[0] for row in result]
