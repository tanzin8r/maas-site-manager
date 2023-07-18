from datetime import (
    datetime,
    timedelta,
)
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.service._token import TokenService

from ..fixtures.factory import Factory


@pytest.mark.asyncio
class TestTokenService:
    async def test_create(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        now = datetime.utcnow()
        duration = timedelta(minutes=10)
        service = TokenService(db_connection)
        expiration, uuids = await service.create(duration=duration, count=10)
        assert len(uuids) == 10
        assert expiration > now + duration

    async def test_get_active_tokens(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        now = datetime.utcnow()
        uuid1, uuid2, uuid3 = [uuid.uuid4() for _ in range(3)]
        _, t2, t3 = await factory.create(
            "token",
            [
                {
                    "value": uuid1,
                    "expired": now - timedelta(hours=1),
                },
                {
                    "value": uuid2,
                    "expired": now + timedelta(hours=1),
                },
                {
                    "value": uuid3,
                    "expired": now + timedelta(hours=2),
                },
            ],
        )
        service = TokenService(db_connection)
        assert [token.value for token in await service.get_active()] == [
            uuid2,
            uuid3,
        ]
