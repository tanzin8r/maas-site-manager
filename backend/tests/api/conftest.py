from typing import (
    AsyncIterator,
    Iterator,
)

from fastapi import FastAPI
from prometheus_client import CollectorRegistry
import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.api import create_app
from msm.db import Database
from msm.db.models import (
    Config,
    User,
)
from msm.service import ConfigService

from ..fixtures.client import Client
from ..fixtures.factory import Factory


def make_api_client(app: FastAPI, config: Config, prefix: str = "") -> Client:
    """Return a Client configured for the application API."""
    client = Client(app=app, base_url=f"http://test{prefix}")
    client.set_token_config(config.service_identifier, config.token_secret_key)
    return client


@pytest.fixture
def api_app(
    db: Database, transaction_middleware_class: type
) -> Iterator[FastAPI]:
    """The API for users."""
    yield create_app(
        db=db,
        transaction_middleware_class=transaction_middleware_class,
        prometheus_registry=CollectorRegistry(),
    )


@pytest.fixture
async def api_config(db_connection: AsyncConnection) -> AsyncIterator[Config]:
    """The API service configuration."""
    service = ConfigService(db_connection)
    await service.ensure()
    yield await service.get()


@pytest.fixture
async def app_client(
    api_app: FastAPI, api_config: Config
) -> AsyncIterator[Client]:
    """Client for the API."""
    async with make_api_client(api_app, api_config) as client:
        yield client


API_USER_NAME = "user"
API_ADMIN_NAME = "admin"


@pytest.fixture
async def api_user(factory: Factory) -> AsyncIterator[User]:
    """An API user (without admin rights)."""
    yield await factory.make_User(username=API_USER_NAME, is_admin=False)


@pytest.fixture
async def api_admin(factory: Factory) -> AsyncIterator[User]:
    """An API administrator."""
    yield await factory.make_User(username=API_ADMIN_NAME, is_admin=True)
