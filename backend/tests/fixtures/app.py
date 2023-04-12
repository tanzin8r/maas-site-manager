from typing import (
    AsyncIterable,
    Iterable,
)

from fastapi import FastAPI
from httpx import AsyncClient
import pytest

from msm.db import Database
from msm.user_api import create_app


@pytest.fixture
def user_app(db: Database) -> Iterable[FastAPI]:
    """The API for users."""
    yield create_app(db.dsn)


@pytest.fixture
async def user_app_client(user_app: FastAPI) -> AsyncIterable[AsyncClient]:
    """Client for the user API."""
    async with AsyncClient(app=user_app, base_url="http://test") as client:
        yield client
