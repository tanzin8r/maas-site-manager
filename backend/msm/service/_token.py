from datetime import (
    datetime,
    timedelta,
)
from typing import Iterable
from uuid import UUID

from sqlalchemy import (
    delete,
    select,
)

from ..db import (
    models,
    queries,
)
from ..db.tables import Token
from ._base import Service


class TokenService(Service):
    async def create(
        self, duration: timedelta, count: int = 1
    ) -> tuple[datetime, Iterable[UUID]]:
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
        return expired, (row[0] for row in result)

    async def get(
        self,
        offset: int = 0,
        limit: int | None = None,
    ) -> tuple[int, Iterable[models.Token]]:
        count = await queries.row_count(self.conn, Token)
        stmt = (
            select(
                Token.c.id,
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
        return count, self.objects_from_result(models.Token, result)

    async def delete(self, token_id: int) -> None:
        """Deletes a token by ID."""
        stmt = delete(Token).where(Token.c.id == token_id)
        await self.conn.execute(stmt)

    async def get_active(self) -> Iterable[models.Token]:
        result = await self.conn.execute(
            select(
                Token.c.id,
                Token.c.value,
                Token.c.expired,
                Token.c.created,
            )
            .select_from(Token)
            .where(Token.c.expired > datetime.utcnow())
            .order_by(Token.c.id)
        )
        return self.objects_from_result(models.Token, result)
