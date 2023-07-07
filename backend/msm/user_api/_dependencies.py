from collections.abc import AsyncIterator
from typing import (
    Annotated,
    Iterator,
)

from fastapi import (
    Depends,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncConnection

from ..service import ServiceCollection


async def db_connection(request: Request) -> AsyncIterator[AsyncConnection]:
    """Provide a DB connection to execute queries, within a transaction."""
    async with request.app.state.db.engine.connect() as conn:
        async with conn.begin():
            yield conn


def services(
    connection: Annotated[AsyncConnection, Depends(db_connection)]
) -> Iterator[ServiceCollection]:
    """Provide the ServiceCollection to access services."""
    yield ServiceCollection(connection)
