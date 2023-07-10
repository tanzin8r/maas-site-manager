from typing import (
    AsyncIterable,
    Iterable,
)

from fastapi import FastAPI
from httpx import (
    AsyncClient,
    Response,
)
import pytest

from msm.db import Database
from msm.user_api import create_app
from msm.user_api._jwt import get_password_hash

from .db import Fixture


class AuthAsyncClient(AsyncClient):
    """Equivalent to AsyncClient, but has the ability to send
    requests from an authorized login"""

    def __init__(self, **kwargs) -> None:  # type: ignore
        super().__init__(**kwargs)
        self.email: str = ""
        self._token: str = ""
        self._token_type: str = ""

    async def login(self, email: str, password: str) -> None:
        """login this client with the email and password"""
        response = await self.post(
            "/login", json={"email": email, "password": password}
        )
        assert (
            response.status_code == 200
        ), f"Could not login user: {response.text}"
        self.email = email
        self._token = response.json()["access_token"]
        self._token_type = response.json()["token_type"].capitalize()

    @property
    def authed(self) -> bool:
        """Are we logged in?"""
        return bool(self._token)

    async def request(self, *args, **kwargs) -> Response:  # type: ignore
        """Generate a request with the authorized payload attached if the user
        has been logged in. All methods (get, post, push, ...) use this in
        the backend to construct their requests"""
        if self.authed:
            kwargs.update(
                {
                    "headers": {
                        "Authorization": f"{self._token_type} {self._token}"
                    },
                }
            )
        return await super().request(*args, **kwargs)


@pytest.fixture
def user_app(db: Database) -> Iterable[FastAPI]:
    """The API for users."""
    yield create_app(database=db)


@pytest.fixture
async def user_app_client(user_app: FastAPI) -> AsyncIterable[AsyncClient]:
    """Client for the user API."""
    async with AsyncClient(app=user_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def authenticated_user_app_client(
    user_app: FastAPI, fixture: Fixture
) -> AsyncIterable[AuthAsyncClient]:
    """Authenticated Client for the user API."""
    password = "admin"
    await fixture.create(
        "user",
        {
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin",
            "password": get_password_hash(password),
            "is_admin": False,
        },
        commit=True,
    )
    async with AuthAsyncClient(app=user_app, base_url="http://test") as client:
        await client.login("admin@example.com", password)
        yield client


@pytest.fixture
async def authenticated_admin_app_client(
    user_app: FastAPI, fixture: Fixture
) -> AsyncIterable[AuthAsyncClient]:
    """Authenticated Client for the user API."""
    password = "admin"
    await fixture.create(
        "user",
        {
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin",
            "password": get_password_hash(password),
            "is_admin": True,
        },
        commit=True,
    )
    async with AuthAsyncClient(app=user_app, base_url="http://test") as client:
        await client.login("admin@example.com", password)
        yield client
