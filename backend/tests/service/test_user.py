import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import UserWithPassword
from msm.service._user import UserService

from ..fixtures.db import Fixture


@pytest.mark.asyncio
class TestUserService:
    async def test_id_exists(
        self, fixture: Fixture, db_connection: AsyncConnection
    ) -> None:
        phash1 = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
        users = await fixture.create(
            "user",
            [
                {
                    "email": "admin@example.com",
                    "username": "admin",
                    "full_name": "Admin",
                    "password": phash1,
                    "is_admin": True,
                }
            ],
        )
        service = UserService(db_connection)
        assert await service.id_exists(users[0]["id"])
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
        fixture: Fixture,
        db_connection: AsyncConnection,
        email: str,
        username: str,
        exists: bool,
    ) -> None:
        phash1 = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
        user_details = {
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin",
            "password": phash1,
            "is_admin": True,
        }
        await fixture.create(
            "user",
            [user_details],
        )
        service = UserService(db_connection)
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
        fixture: Fixture,
        db_connection: AsyncConnection,
        email: str,
        username: str,
    ) -> None:
        phash1 = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
        user_details = {
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin",
            "password": phash1,
            "is_admin": True,
        }
        [user] = await fixture.create(
            "user",
            [user_details],
        )
        service = UserService(db_connection)
        assert not await service.exists(
            email=email, username=username, exclude_id=user["id"]
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
        fixture: Fixture,
        db_connection: AsyncConnection,
        id: int,
        exists: bool,
    ) -> None:
        phash1 = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
        user_details = {
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin",
            "password": phash1,
            "is_admin": True,
        }
        [user] = await fixture.create("user", [user_details])
        service = UserService(db_connection)
        assert await service.get_by_id(id) == (
            UserWithPassword(**user) if exists else None
        )
