from datetime import (
    datetime,
    timedelta,
)
from typing import (
    Any,
    Iterable,
)
import uuid

from sqlalchemy import (
    delete,
    select,
    Select,
)

from ..db import (
    models,
    queries,
)
from ..db.tables import Token
from ..jwt import JWT
from ._base import Service


class TokenService(Service):
    async def create(
        self,
        issuer: str,
        duration: timedelta,
        count: int = 1,
        secret_key: str = "",
    ) -> tuple[datetime, Iterable[str]]:
        """Create tokens, returning their expiration and values."""
        created = datetime.utcnow()
        expired = created + duration
        tokens_data = []
        token_values = []
        for _ in range(count):
            auth_id = uuid.uuid4()
            token = JWT.create(
                issuer=issuer,
                subject=str(auth_id),
                key=secret_key,
                duration=duration,
            )
            token_values.append(token.encoded)
            tokens_data.append(
                {
                    "expired": token.expiration,
                    "created": created,
                    "value": token.encoded,
                    "auth_id": auth_id,
                }
            )
        await self.conn.execute(Token.insert(), tokens_data)
        return expired, token_values

    async def get(
        self,
        offset: int = 0,
        limit: int | None = None,
    ) -> tuple[int, Iterable[models.Token]]:
        """Return active tokens."""
        expired_filter = Token.c.expired > datetime.utcnow()
        count = await queries.row_count(self.conn, Token, expired_filter)
        stmt = (
            self._select_statement()
            .where(expired_filter)
            .order_by(Token.c.id)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.conn.execute(stmt)
        return count, self.objects_from_result(models.Token, result)

    async def get_by_auth_id(self, auth_id: uuid.UUID) -> models.Token | None:
        """Get a token by authentication ID.

        The token is returned even if it's expired.
        """
        stmt = self._select_statement().where(Token.c.auth_id == auth_id)
        result = await self.conn.execute(stmt)
        if row := result.one_or_none():
            return models.Token(**row._asdict())
        return None

    async def delete(self, id: int) -> None:
        """Deletes a token by ID."""
        stmt = delete(Token).where(Token.c.id == id)
        await self.conn.execute(stmt)

    def _select_statement(self) -> Select[Any]:
        return select(
            Token.c.id,
            Token.c.value,
            Token.c.expired,
            Token.c.created,
        ).select_from(Token)
