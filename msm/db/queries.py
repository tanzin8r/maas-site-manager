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
    result = await session.execute(
        select(Site.c.id, Site.c.name, Site.c.last_checkin)
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
