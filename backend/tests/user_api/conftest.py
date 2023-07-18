from typing import (
    AsyncIterator,
    Callable,
    Iterator,
)

from fastapi import FastAPI
import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import Database
from msm.db.models import User
from msm.password import hash_password
from msm.user_api import create_app

from ..fixtures.app import override_dependencies
from ..fixtures.client import Client
from ..fixtures.factory import Factory


@pytest.fixture
def api_app(db: Database, db_connection: AsyncConnection) -> Iterator[FastAPI]:
    """The API for users."""

    from msm.user_api._dependencies import db_connection as orig_db_connection

    deps_map = {orig_db_connection: lambda: db_connection}

    app = create_app(database=db)
    with override_dependencies(app, deps_map):
        yield app


@pytest.fixture
async def app_client(api_app: FastAPI) -> AsyncIterator[Client]:
    """Client for the user API."""
    async with Client(app=api_app, base_url="http://test") as client:
        yield client


def make_user_fixture(
    username: str, is_admin: bool = False
) -> Callable[[Factory], AsyncIterator[User]]:
    """Return a fixture for an API user."""

    @pytest.fixture
    async def api_user_fixture(factory: Factory) -> AsyncIterator[User]:
        [user] = await factory.create(
            "user",
            {
                "username": username,
                "email": f"{username}@example.com",
                "full_name": username.capitalize(),
                "password": hash_password(username),
                "is_admin": is_admin,
            },
        )
        yield User(**user)

    return api_user_fixture


API_USER_NAME = "user"
API_ADMIN_NAME = "admin"

api_user = make_user_fixture(API_USER_NAME, is_admin=False)
api_admin = make_user_fixture(API_ADMIN_NAME, is_admin=True)


@pytest.fixture
async def user_client(
    api_app: FastAPI, api_user: User
) -> AsyncIterator[Client]:
    """Authenticated client for the API user."""
    async with Client(app=api_app, base_url="http://test") as client:
        await client.login(api_user.email, api_user.username)
        yield client


@pytest.fixture
async def admin_client(
    api_app: FastAPI, api_admin: User
) -> AsyncIterator[Client]:
    """Authenticated client for the API admin."""
    async with Client(app=api_app, base_url="http://test") as client:
        await client.login(api_admin.email, api_admin.username)
        yield client
