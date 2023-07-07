from datetime import (
    datetime,
    timedelta,
)
import uuid

import pytest
from sqlalchemy.ext.asyncio.session import AsyncSession

from msm.service._token import TokenService

from ..fixtures.db import Fixture


@pytest.mark.asyncio
class TestTokenService:
    async def test_create(
        self, fixture: Fixture, session: AsyncSession
    ) -> None:
        now = datetime.utcnow()
        duration = timedelta(minutes=10)
        service = TokenService(session)
        expiration, uuids = await service.create(duration=duration, count=10)
        assert len(uuids) == 10
        assert expiration > now + duration

    async def test_get_active_tokens(
        self, fixture: Fixture, session: AsyncSession
    ) -> None:
        now = datetime.utcnow()
        uuid1, uuid2, uuid3 = [uuid.uuid4() for _ in range(3)]
        _, t2, t3 = await fixture.create(
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
        service = TokenService(session)
        assert [token.value for token in await service.get_active()] == [
            uuid2,
            uuid3,
        ]
