from typing import (
    AsyncIterator,
    Iterator,
)

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import User
from msm.password import hash_password
from msm.service._user import UserService

from ..fixtures.factory import Factory


@pytest.fixture
def service(db_connection: AsyncConnection) -> Iterator[UserService]:
    yield UserService(db_connection)


@pytest.fixture
async def user(factory: Factory) -> AsyncIterator[User]:
    [user] = await factory.create(
        "user",
        [
            {
                "email": "admin@example.com",
                "username": "admin",
                "full_name": "Admin",
                "password": hash_password("secret"),
                "is_admin": True,
            }
        ],
    )
    yield User(**user)


@pytest.mark.asyncio
class TestUserService:
    async def test_id_exists(self, user: User, service: UserService) -> None:
        assert await service.id_exists(user.id)
        assert not await service.id_exists(-1)

    @pytest.mark.parametrize(
        "email,username,exists",
        [
            ("", "", False),
            ("admin@example.com", "admin", True),
            ("admin@example.com", "nonexistent_admin", True),
            ("nonexistent_admin@example.com", "admin", True),
            ("nonexistent_admin@example.com", "nonexistent_admin", False),
        ],
    )
    async def test_exists(
        self,
        user: User,
        service: UserService,
        email: str,
        username: str,
        exists: bool,
    ) -> None:
        assert await service.exists(email=email, username=username) == exists

    @pytest.mark.parametrize(
        "email,username",
        [
            ("admin@example.com", "admin"),
            ("admin@example.com", "nonexistent_admin"),
            ("nonexistent_admin@example.com", "admin"),
            ("nonexistent_admin@example.com", "nonexistent_admin"),
        ],
    )
    async def test_exists_exclude_id(
        self,
        user: User,
        service: UserService,
        email: str,
        username: str,
    ) -> None:
        assert not await service.exists(
            email=email, username=username, exclude_id=user.id
        )

    @pytest.mark.parametrize(
        "id,exists",
        [
            (1, True),
            (-1, False),
        ],
    )
    async def test_get_by_id(
        self,
        user: User,
        service: UserService,
        id: int,
        exists: bool,
    ) -> None:
        assert await service.get_by_id(id) == (user if exists else None)

    async def test_password_matches(
        self,
        user: User,
        service: UserService,
    ) -> None:
        assert await service.password_matches(user.id, "secret")
        assert not await service.password_matches(user.id, "other-secret")

    async def test_update_password(
        self,
        user: User,
        service: UserService,
    ) -> None:
        new_password = "new-secret"
        await service.update_password(user.id, new_password)
        assert await service.password_matches(user.id, new_password)
