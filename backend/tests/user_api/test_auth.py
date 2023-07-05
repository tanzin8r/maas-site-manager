from httpx import AsyncClient
import pytest

from ..fixtures.app import AuthAsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,url",
    [
        ("GET", "/requests"),
        ("POST", "/requests"),
        ("GET", "/sites"),
        ("GET", "/tokens"),
        ("POST", "/tokens"),
        ("GET", "/tokens/export"),
        ("GET", "/users"),
        ("POST", "/users"),
        ("GET", "/users/me"),
        ("PATCH", "/users/me"),
        ("POST", "/users/me/password"),
        ("PATCH", "/users/{id}"),
        ("DELETE", "/users/{id}"),
    ],
)
async def test_handler_auth_required(
    user_app_client: AsyncClient, method: str, url: str
) -> None:
    response = await user_app_client.request(method, url)
    assert (
        response.status_code == 401
    ), f"Auth should be required for {method} {url}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,url",
    [
        ("GET", "/users"),
        ("POST", "/users"),
        ("DELETE", "/users/{id}"),
        ("PATCH", "/users/{id}"),
    ],
)
async def test_handler_admin_required(
    authenticated_user_app_client: AuthAsyncClient, method: str, url: str
) -> None:
    response = await authenticated_user_app_client.request(method, url)
    assert (
        response.status_code == 403
    ), f"Admin should be required for {method} {url}"
