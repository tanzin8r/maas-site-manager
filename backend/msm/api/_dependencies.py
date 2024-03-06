from collections.abc import AsyncIterator, Iterator
from typing import (
    Annotated,
)

from fastapi import (
    Depends,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import Config
from msm.service import (
    ConfigService,
    ServiceCollection,
)


async def db_connection(request: Request) -> AsyncIterator[AsyncConnection]:
    """Provide a DB connection to execute queries, within a transaction.

    Requires the TransactionMiddleware to be used.
    """
    yield request.state.conn


def services(
    connection: Annotated[AsyncConnection, Depends(db_connection)]
) -> Iterator[ServiceCollection]:
    """Provide the ServiceCollection to access services."""
    yield ServiceCollection(connection)


async def config(
    connection: Annotated[AsyncConnection, Depends(db_connection)]
) -> AsyncIterator[Config]:
    """Return the application configuration."""
    service = ConfigService(connection)
    yield await service.get()
