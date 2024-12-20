import pytest

from msm.api.exceptions.constants import ExceptionCode
from msm.api.exceptions.responses import UnauthorizedErrorResponseModel
from msm.db.models import User
from tests.fixtures.client import Client


@pytest.mark.asyncio
async def test_post(app_client: Client, api_admin: User) -> None:
    response = await app_client.post(
        "/api/v1/login",
        data={"username": api_admin.email, "password": "admin"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_post_fails_with_wrong_password(
    app_client: Client, api_admin: User
) -> None:
    response = await app_client.post(
        "/api/v1/login",
        data={"username": api_admin.email, "password": "incorrect_pass"},
    )
    assert response.status_code == 401
    err = UnauthorizedErrorResponseModel(**response.json())
    assert err.error.code == ExceptionCode.INVALID_CREDENTIALS
    assert err.error.message == "Wrong username or password."
