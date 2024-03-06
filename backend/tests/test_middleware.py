from collections.abc import AsyncIterator, Iterator
from typing import (
    Any,
)

from fastapi import (
    FastAPI,
    Request,
)
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import Database
from msm.middleware import DatabaseMetricsMiddleware
from tests.fixtures.client import Client


@pytest.fixture
def app(
    db: Database,
    db_connection: AsyncConnection,
    transaction_middleware_class: type,
) -> Iterator[FastAPI]:
    app = FastAPI()
    app.add_middleware(DatabaseMetricsMiddleware, db=db)
    app.add_middleware(transaction_middleware_class, db=db)

    @app.get("/{count}")
    async def get(request: Request, count: int) -> Any:
        for _ in range(count):
            await db_connection.execute(text("SELECT 1"))
        return request.state.query_metrics

    yield app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[Client]:
    """Client for the API."""
    async with Client(
        app=app, base_url="http://test", trust_env=False
    ) as client:
        yield client


class TestDatabaseMetricsMiddleware:
    @pytest.mark.parametrize("count", [1, 3])
    async def test_query_metrics(self, client: Client, count: int) -> None:
        metrics = (await client.get(f"/{count}")).json()
        assert metrics["count"] == count
        assert metrics["latency"] > 0.0
