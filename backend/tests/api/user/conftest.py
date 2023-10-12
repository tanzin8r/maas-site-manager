from typing import AsyncIterator

from fastapi import FastAPI
import pytest

from msm.db.models import User

from ...fixtures.client import Client
from ..conftest import make_api_client


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
