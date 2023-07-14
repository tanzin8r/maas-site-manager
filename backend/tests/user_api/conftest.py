from typing import (
    AsyncIterable,
    Iterable,
)

from fastapi import FastAPI
import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import Database
from msm.user_api import create_app
from msm.user_api._auth import get_password_hash

from ..fixtures.app import override_dependencies
from ..fixtures.client import Client
from ..fixtures.db import Fixture


@pytest.fixture
def api_app(db: Database, db_connection: AsyncConnection) -> Iterable[FastAPI]:
    """The API for users."""

    from msm.user_api._dependencies import db_connection as orig_db_connection

    deps_map = {orig_db_connection: lambda: db_connection}

    app = create_app(database=db)
    with override_dependencies(app, deps_map):
        yield app


@pytest.fixture
async def app_client(api_app: FastAPI) -> AsyncIterable[Client]:
    """Client for the user API."""
    async with Client(app=api_app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def user_client(
    api_app: FastAPI, fixture: Fixture
) -> AsyncIterable[Client]:
    """Authenticated Client for the user API."""
    email = "admin@example.com"
    password = "admin"
    await fixture.create(
        "user",
        {
            "email": email,
            "username": "admin",
            "full_name": "Admin",
            "password": get_password_hash(password),
            "is_admin": False,
        },
    )
    async with Client(app=api_app, base_url="http://test") as client:
        await client.login(email, password)
        yield client


@pytest.fixture
async def admin_client(
    api_app: FastAPI, fixture: Fixture
) -> AsyncIterable[Client]:
    """Authenticated Client for the user API."""
    email = "admin@example.com"
    password = "admin"
    await fixture.create(
        "user",
        {
            "email": email,
            "username": "admin",
            "full_name": "Admin",
            "password": get_password_hash(password),
            "is_admin": True,
        },
    )

    async with Client(app=api_app, base_url="http://test") as client:
        await client.login(email, password)
        yield client
