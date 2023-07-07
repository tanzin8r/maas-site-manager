from datetime import (
    datetime,
    timedelta,
)
from uuid import UUID

from sqlalchemy import select

from ..db import (
    models,
    queries,
)
from ..db.tables import Token
from ._base import Service


class TokenService(Service):
    async def create(
        self, duration: timedelta, count: int = 1
    ) -> tuple[datetime, list[UUID]]:
        """Create tokens, returning their expiration and UUIDs."""
        created = datetime.utcnow()
        expired = created + duration
        result = await self.conn.execute(
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

    async def get(
        self,
        offset: int = 0,
        limit: int | None = None,
    ) -> tuple[int, list[models.Token]]:
        count = await queries.row_count(self.conn, Token)
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
        result = await self.conn.execute(stmt)
        return count, [models.Token(**row._asdict()) for row in result.all()]

    async def get_active(self) -> list[models.Token]:
        result = await self.conn.execute(
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
