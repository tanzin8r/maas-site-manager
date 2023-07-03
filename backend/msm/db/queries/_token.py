from datetime import (
    datetime,
    timedelta,
)
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models
from .._tables import Token
from ._count import row_count


async def get_tokens(
    session: AsyncSession,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[int, list[models.Token]]:
    count = await row_count(session, Token)
    stmt = (
        select(
            Token.c.id,
            Token.c.site_id,
            Token.c.value,
            Token.c.expired,
            Token.c.created,
        )
        .select_from(Token)
        .order_by(Token.c.id)
        .offset(offset)
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return count, [models.Token(**row._asdict()) for row in result.all()]


async def get_active_tokens(session: AsyncSession) -> list[models.Token]:
    result = await session.execute(
        select(
            Token.c.id,
            Token.c.site_id,
            Token.c.value,
            Token.c.expired,
            Token.c.created,
        )
        .select_from(Token)
        .where(Token.c.expired > datetime.utcnow())
        .order_by(Token.c.id)
    )
    return [models.Token(**row._asdict()) for row in result.all()]


async def create_tokens(
    session: AsyncSession, duration: timedelta, count: int = 1
) -> tuple[datetime, list[UUID]]:
    created = datetime.utcnow()
    expired = created + duration
    result = await session.execute(
        Token.insert().returning(Token.c.value),
        [
            {
                "expired": expired,
                "created": created,
            }
            for _ in range(count)
        ],
    )
    return expired, [row[0] for row in result]
