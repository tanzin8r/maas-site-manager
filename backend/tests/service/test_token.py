from datetime import (
    datetime,
    timedelta,
)
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.jwt import JWT
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
        expiration, values = await service.create(
            issuer="issuer",
            duration=duration,
            count=10,
        )
        assert len(list(values)) == 10
        assert expiration > now + duration

    async def test_create_value_is_jwt(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        secret_key = "abcde"
        duration = timedelta(minutes=10)
        service = TokenService(db_connection)
        _, [value] = await service.create(
            issuer="issuer", duration=duration, secret_key=secret_key
        )
        decoded_token = JWT.decode(value, secret_key)
        [token] = await factory.get("token")
        assert token["auth_id"] == uuid.UUID(decoded_token.subject)

    async def test_get_includes_only_active(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        uuid1, uuid2, uuid3 = [uuid.uuid4() for _ in range(3)]
        await factory.make_Token(auth_id=uuid1, lifetime=timedelta(hours=-1))
        await factory.make_Token(auth_id=uuid2, lifetime=timedelta(hours=1))
        await factory.make_Token(auth_id=uuid3, lifetime=timedelta(hours=2))

        service = TokenService(db_connection)
        count, tokens = await service.get()
        assert count == 2
        assert {JWT.decode(token.value).subject for token in tokens} == {
            str(uuid2),
            str(uuid3),
        }

    async def test_get_by_auth_id(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        uuid1, uuid2, uuid3 = [uuid.uuid4() for _ in range(3)]
        await factory.make_Token(auth_id=uuid1, lifetime=timedelta(hours=-1))
        await factory.make_Token(auth_id=uuid2, lifetime=timedelta(hours=1))
        service = TokenService(db_connection)
        assert await service.get_by_auth_id(uuid1) is not None
        assert await service.get_by_auth_id(uuid2) is not None
        assert await service.get_by_auth_id(uuid3) is None
