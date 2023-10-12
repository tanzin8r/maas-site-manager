from typing import (
    AsyncIterator,
    Iterator,
)

from fastapi import FastAPI
from prometheus_client import CollectorRegistry
import pytest

from msm.api import create_app
from msm.db import Database

from ..fixtures.client import Client


def make_api_client(app: FastAPI, prefix: str = "") -> Client:
    return Client(app=app, base_url=f"http://test{prefix}")


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
async def app_client(api_app: FastAPI) -> AsyncIterator[Client]:
    """Client for the API."""
    async with make_api_client(api_app) as client:
        yield client
