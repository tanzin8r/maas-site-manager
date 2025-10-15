from collections.abc import AsyncIterator, Iterator
from typing import cast
from unittest.mock import AsyncMock

from fastapi import FastAPI
from httpx import ASGITransport
from prometheus_client import CollectorRegistry
import pytest
from pytest_mock import MockerFixture, MockType
from sqlalchemy.ext.asyncio import AsyncConnection
from temporalio.client import (
    Client as TemporalClient,
    ScheduleHandle,
    ScheduleListDescription,
)

from msm.apiserver.db import Database
from msm.apiserver.db.models import Config
from msm.apiserver.main import create_app
from msm.apiserver.service import (
    ConfigService,
    ServiceCollection,
)
from tests.fixtures.client import Client


def make_api_client(app: FastAPI, config: Config, prefix: str = "") -> Client:
    """Return a Client configured for the application API."""
    client = Client(
        transport=ASGITransport(app=app),
        base_url=f"http://test{prefix}",
        trust_env=False,
    )
    client.set_token_config(config.service_identifier, config.token_secret_key)
    return client


@pytest.fixture
async def temporal_client() -> MockType:
    mock_client = AsyncMock(spec=TemporalClient)
    mock_handle = AsyncMock(spec=ScheduleHandle)
    mock_sched_list = AsyncMock(spec=Iterator[ScheduleListDescription])
    mock_client.list_schedules.return_value = mock_sched_list
    mock_client.create_schedule.return_value = mock_handle
    mock_client.get_schedule_handle.return_value = mock_handle
    return cast(MockType, mock_client)


@pytest.fixture
def api_app(
    db: Database,
    transaction_middleware_class: type,
    temporal_client: TemporalClient,
    mocker: MockerFixture,
) -> Iterator[FastAPI]:
    """The API for users."""
    mocker.patch(
        "msm.apiserver.middleware.TemporalClientProxy.get_client",
        return_value=temporal_client,
    )
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
def api_services(
    db_connection: AsyncConnection,
    temporal_client: TemporalClient,
) -> Iterator[ServiceCollection]:
    """A ServiceCollection using the current DB connection."""
    yield ServiceCollection(db_connection, temporal_client)


@pytest.fixture
async def app_client(
    api_app: FastAPI, api_config: Config
) -> AsyncIterator[Client]:
    """Client for the API."""
    async with make_api_client(api_app, api_config) as client:
        yield client
