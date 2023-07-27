import pytest

from ..fixtures.client import Client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,url",
    [
        ("GET", "/requests"),
        ("POST", "/requests"),
        ("GET", "/sites"),
        ("GET", "/sites/coordinates"),
        ("GET", "/sites/{id}"),
        ("GET", "/tokens"),
        ("POST", "/tokens"),
        ("GET", "/tokens/export"),
        ("GET", "/users"),
        ("POST", "/users"),
        ("GET", "/users/me"),
        ("PATCH", "/users/me"),
        ("PATCH", "/users/me/password"),
        ("GET", "/users/{id}"),
        ("PATCH", "/users/{id}"),
        ("DELETE", "/users/{id}"),
    ],
)
async def test_handler_auth_required(
    app_client: Client, method: str, url: str
) -> None:
    response = await app_client.request(method, url)
    assert (
        response.status_code == 401
    ), f"Auth should be required for {method} {url}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,url",
    [
        ("GET", "/users"),
        ("POST", "/users"),
        ("GET", "/users/{id}"),
        ("DELETE", "/users/{id}"),
        ("PATCH", "/users/{id}"),
    ],
)
async def test_handler_admin_required(
    user_client: Client, method: str, url: str
) -> None:
    response = await user_client.request(method, url)
    assert (
        response.status_code == 403
    ), f"Admin should be required for {method} {url}"
