from httpx import AsyncClient
import pytest

from ...fixtures.db import Fixture


@pytest.mark.asyncio
async def test_post(user_app_client: AsyncClient, fixture: Fixture) -> None:
    phash = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
    userdata = {
        "email": "admin@example.com",
        "username": "admin",
        "full_name": "Admin",
        "password": phash,
        "is_admin": True,
    }
    await fixture.create("user", userdata, commit=True)
    response = await user_app_client.post(
        "/login",
        json={"email": userdata["email"], "password": "admin"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_post_fails_with_wrong_password(
    user_app_client: AsyncClient, fixture: Fixture
) -> None:
    phash = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
    userdata = {
        "email": "admin@example.com",
        "username": "admin",
        "full_name": "Admin",
        "password": phash,
        "is_admin": True,
    }
    await fixture.create("user", userdata, commit=True)

    fail_response = await user_app_client.post(
        "/login",
        json={"email": userdata["email"], "password": "incorrect_pass"},
    )
    assert fail_response.status_code == 401
