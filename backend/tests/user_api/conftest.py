from typing import (
    AsyncIterator,
    Iterator,
)

from fastapi import FastAPI
import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import Database
from msm.password import hash_password
from msm.user_api import create_app

from ..fixtures.app import override_dependencies
from ..fixtures.client import Client
from ..fixtures.db import Fixture


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


@pytest.fixture
async def user_client(
    api_app: FastAPI, fixture: Fixture
) -> AsyncIterator[Client]:
    """Authenticated Client for the user API."""
    email = "admin@example.com"
    password = "admin"
    await fixture.create(
        "user",
        {
            "email": email,
            "username": "admin",
            "full_name": "Admin",
            "password": hash_password(password),
            "is_admin": False,
        },
    )
    async with Client(app=api_app, base_url="http://test") as client:
        await client.login(email, password)
        yield client


@pytest.fixture
async def admin_client(
    api_app: FastAPI, fixture: Fixture
) -> AsyncIterator[Client]:
    """Authenticated Client for the user API."""
    email = "admin@example.com"
    password = "admin"
    await fixture.create(
        "user",
        {
            "email": email,
            "username": "admin",
            "full_name": "Admin",
            "password": hash_password(password),
            "is_admin": True,
        },
    )

    async with Client(app=api_app, base_url="http://test") as client:
        await client.login(email, password)
        yield client
