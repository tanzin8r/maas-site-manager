from typing import Iterator
from uuid import uuid4

from fastapi import (
    FastAPI,
    HTTPException,
)
from fastapi.routing import APIRoute
from httpx import Request
import pytest

from msm.api._auth import (
    auth_id_from_token,
    bearer_token,
    token_response,
)
from msm.db.models import (
    Config,
    User,
)
from msm.jwt import (
    JWT,
    TokenAudience,
)

from ..fixtures.client import Client

AUTHENTICATED_ROUTES = [
    # user API
    ("GET", "/api/v1/sites"),
    ("GET", "/api/v1/sites/coordinates"),
    ("GET", "/api/v1/sites/pending"),
    ("POST", "/api/v1/sites/pending"),
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
    # site API
    ("GET", "/site/v1/enroll"),
    ("POST", "/site/v1/enroll"),
]

UNAUTHENTICATED_ROUTES = [
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
    """Return all API routes as tuples of (method, path)."""
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
    app_client: Client,
    api_user: User,
    method: str,
    url: str,
) -> None:
    app_client.authenticate(api_user.auth_id)
    response = await app_client.request(method, url)
    assert (
        response.status_code == 403
    ), f"Admin should be required for {method} {url}"


def test_token_response(api_config: Config) -> None:
    auth_id = uuid4()
    response = token_response(api_config, auth_id, TokenAudience.API)
    assert response.token_type == "Bearer"
    token = JWT.decode(
        response.access_token,
        key=api_config.token_secret_key,
        issuer=api_config.service_identifier,
        audience=TokenAudience.API,
    )
    assert token.subject == str(auth_id)
    assert token.audience == [TokenAudience.API]


@pytest.mark.asyncio
class TestBearerToken:
    async def test_valid_token(self) -> None:
        request = Request(
            "GET", "/test", headers={"Authorization": "Bearer ABCD"}
        )
        assert await bearer_token(request) == "ABCD"  # type: ignore[arg-type]

    async def test_no_token(self) -> None:
        request = Request("GET", "/test")
        with pytest.raises(HTTPException) as error:
            await bearer_token(request)  # type: ignore[arg-type]
        assert error.value.status_code == 401
        assert error.value.headers == {"WWW-Authenticate": "Bearer"}


class TestAuthIDFromToken:
    def test_valid_token(self, api_config: Config) -> None:
        auth_id = uuid4()
        token = JWT.create(
            issuer=api_config.service_identifier,
            subject=str(auth_id),
            audience=TokenAudience.API,
            key=api_config.token_secret_key,
        )
        get_auth_id = auth_id_from_token(bearer_token, TokenAudience.API)
        assert get_auth_id(api_config, token.encoded) == auth_id

    def test_invalid_token(self, api_config: Config) -> None:
        get_auth_id = auth_id_from_token(bearer_token, TokenAudience.API)
        with pytest.raises(HTTPException) as error:
            get_auth_id(api_config, "invalid")
        assert error.value.status_code == 401
