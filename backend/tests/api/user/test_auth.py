from typing import Iterator

from fastapi import FastAPI
from fastapi.routing import APIRoute
import pytest

from msm.db.models import User

from ...fixtures.client import Client

AUTHENTICATED_ROUTES = [
    ("GET", "/api/v1/requests"),
    ("POST", "/api/v1/requests"),
    ("GET", "/api/v1/sites"),
    ("GET", "/api/v1/sites/coordinates"),
    ("GET", "/api/v1/sites/{id}"),
    ("PATCH", "/api/v1/sites/{id}"),
    ("DELETE", "/api/v1/sites/{id}"),
    ("GET", "/api/v1/tokens"),
    ("POST", "/api/v1/tokens"),
    ("GET", "/api/v1/tokens/export"),
    ("DELETE", "/api/v1/tokens/{id}"),
    ("GET", "/api/v1/users"),
    ("POST", "/api/v1/users"),
    ("GET", "/api/v1/users/me"),
    ("PATCH", "/api/v1/users/me"),
    ("PATCH", "/api/v1/users/me/password"),
    ("GET", "/api/v1/users/{id}"),
    ("PATCH", "/api/v1/users/{id}"),
    ("DELETE", "/api/v1/users/{id}"),
]

UNAUTHENTICATED_ROUTES = [
    ("GET", "/api/v1/"),
    ("POST", "/api/v1/login"),
    ("GET", "/metrics"),
]

ADMIN_ROUTES = [
    ("GET", "/api/v1/users"),
    ("POST", "/api/v1/users"),
    ("GET", "/api/v1/users/{id}"),
    ("DELETE", "/api/v1/users/{id}"),
    ("PATCH", "/api/v1/users/{id}"),
]


@pytest.fixture
def api_routes(api_app: FastAPI) -> Iterator[set[tuple[str, str]]]:
    routes = set()
    for route in api_app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods:
            routes.add((method, route.path))
    yield routes


def test_all_routes_checked(api_routes: set[tuple[str, str]]) -> None:
    assert api_routes == set(AUTHENTICATED_ROUTES + UNAUTHENTICATED_ROUTES)


@pytest.mark.asyncio
@pytest.mark.parametrize("method,url", AUTHENTICATED_ROUTES)
async def test_handler_auth_required(
    app_client: Client, method: str, url: str
) -> None:
    response = await app_client.request(method, url)
    assert (
        response.status_code == 401
    ), f"Auth should be required for {method} {url}"


@pytest.mark.asyncio
@pytest.mark.parametrize("method,url", UNAUTHENTICATED_ROUTES)
async def test_handler_auth_not_required(
    app_client: Client, method: str, url: str
) -> None:
    response = await app_client.request(method, url)
    assert not response.is_server_error
    assert (
        response.status_code != 401
    ), f"Auth should not be required for {method} {url}"


@pytest.mark.asyncio
@pytest.mark.parametrize("method,url", ADMIN_ROUTES)
async def test_handler_admin_required(
    app_client: Client, api_user: User, method: str, url: str
) -> None:
    app_client.authenticate(api_user.auth_id)
    response = await app_client.request(method, url)
    assert (
        response.status_code == 403
    ), f"Admin should be required for {method} {url}"
