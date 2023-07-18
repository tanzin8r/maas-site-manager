import pytest

from msm.db.models import User

from ...fixtures.client import Client


@pytest.mark.asyncio
async def test_post(app_client: Client, api_admin: User) -> None:
    response = await app_client.post(
        "/login",
        json={"email": api_admin.email, "password": "admin"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_post_fails_with_wrong_password(
    app_client: Client, api_admin: User
) -> None:
    response = await app_client.post(
        "/login",
        json={"email": api_admin.email, "password": "incorrect_pass"},
    )
    assert response.status_code == 401
