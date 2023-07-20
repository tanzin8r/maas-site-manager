from typing import (
    AsyncIterator,
    Iterator,
)

from fastapi import FastAPI
import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import Database
from msm.db.models import User
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


API_USER_NAME = "user"
API_ADMIN_NAME = "admin"


@pytest.fixture
async def api_user(factory: Factory) -> AsyncIterator[User]:
    """An API user (without admin rights)."""
    yield await factory.make_User(username=API_USER_NAME, is_admin=False)


@pytest.fixture
async def api_admin(factory: Factory) -> AsyncIterator[User]:
    """An API administrator)."""
    yield await factory.make_User(username=API_ADMIN_NAME, is_admin=True)


@pytest.fixture
async def user_client(
    api_app: FastAPI, api_user: User
) -> AsyncIterator[Client]:
    """Authenticated client for the API user."""
    async with Client(app=api_app, base_url="http://test") as client:
        client.authenticate(api_user.id)
        yield client


@pytest.fixture
async def admin_client(
    api_app: FastAPI, api_admin: User
) -> AsyncIterator[Client]:
    """Authenticated client for the API admin."""
    async with Client(app=api_app, base_url="http://test") as client:
        client.authenticate(api_admin.id)
        yield client
