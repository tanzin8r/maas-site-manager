import pytest
from sqlalchemy.ext.asyncio.session import AsyncSession

from msm.db.queries._user import (
    user_exists,
    user_id_exists,
)

from ...fixtures.db import Fixture


@pytest.mark.asyncio
async def test_user_id_exists(session: AsyncSession, fixture: Fixture) -> None:
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
        commit=True,
    )
    assert await user_id_exists(session, users[0]["id"])
    assert not await user_id_exists(session, -1)


@pytest.mark.asyncio
class TestUserExists:
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
        session: AsyncSession,
        fixture: Fixture,
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
            commit=True,
        )
        assert (
            await user_exists(session, email=email, username=username)
            == exists
        )

    @pytest.mark.parametrize(
        "email,username",
        [
            ("admin@example.com", "admin"),
            ("admin@example.com", "nonexistent_admin"),
            ("nonexistent_admin@example.com", "admin"),
            ("nonexistent_admin@example.com", "nonexistent_admin"),
        ],
    )
    async def test_skip_user(
        self,
        session: AsyncSession,
        fixture: Fixture,
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
            commit=True,
        )
        assert not await user_exists(
            session, email=email, username=username, exclude_id=user["id"]
        )
