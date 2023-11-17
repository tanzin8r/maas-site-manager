from datetime import timedelta
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
        duration = timedelta(minutes=10)
        service = TokenService(db_connection)
        tokens = list(
            await service.create(
                issuer="issuer",
                duration=duration,
                count=10,
            )
        )
        assert len(tokens) == 10
        for token in tokens:
            assert token.expired - token.created == duration
        db_tokens = await factory.get("token")
        assert {token.value for token in tokens} == {
            token["value"] for token in db_tokens
        }

    async def test_create_value_is_jwt(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        issuer = "issuer"
        secret_key = "abcde"
        duration = timedelta(minutes=10)
        service = TokenService(db_connection)
        [token] = await service.create(
            issuer=issuer, duration=duration, secret_key=secret_key
        )
        decoded_token = JWT.decode(
            token.value,
            key=secret_key,
            issuer=issuer,
        )
        [db_token] = await factory.get("token")
        assert db_token["auth_id"] == uuid.UUID(decoded_token.subject)

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
        assert {
            JWT.decode(token.value, issuer="issuer").subject
            for token in tokens
        } == {
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
