from typing import AsyncIterator

from fastapi import FastAPI
import pytest

from msm.db.models import User

from ...fixtures.client import Client
from ...fixtures.factory import Factory
from ..conftest import make_api_client

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
    """Authenticated client for the API user, under the /api/v1 prefix."""
    async with make_api_client(api_app, prefix="/api/v1") as client:
        client.authenticate(api_user.auth_id)
        yield client


@pytest.fixture
async def admin_client(
    api_app: FastAPI, api_admin: User
) -> AsyncIterator[Client]:
    """Authenticated client for the API admin, under the /api/v1 prefix."""
    async with make_api_client(api_app, prefix="/api/v1") as client:
        client.authenticate(api_admin.auth_id)
        yield client
