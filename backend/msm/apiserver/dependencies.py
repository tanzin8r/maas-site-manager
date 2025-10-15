from collections.abc import AsyncIterator, Iterator
from typing import (
    Annotated,
)

from fastapi import (
    Depends,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncConnection
from temporalio.client import Client as TemporalClient

from msm.apiserver.db.models import Config
from msm.apiserver.service import (
    ServiceCollection,
)


async def db_connection(request: Request) -> AsyncIterator[AsyncConnection]:
    """Provide a DB connection to execute queries, within a transaction.

    Requires the TransactionMiddleware to be used.
    """
    yield request.state.conn


async def temporal_client(request: Request) -> AsyncIterator[TemporalClient]:
    """Provide the Temporal client from the request state.

    Requires the TemporalMiddleware to be used."""
    yield request.state.temporal_client


def services(
    connection: Annotated[AsyncConnection, Depends(db_connection)],
    temporal_client: Annotated[TemporalClient, Depends(temporal_client)],
) -> Iterator[ServiceCollection]:
    """Provide the ServiceCollection to access services."""
    yield ServiceCollection(connection, temporal_client)


async def config(
    services: Annotated[ServiceCollection, Depends(services)],
) -> AsyncIterator[Config]:
    """Return the application configuration."""
    yield await services.config.get()
