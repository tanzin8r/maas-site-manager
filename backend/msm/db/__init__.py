from typing import (
    Any,
    Awaitable,
    Callable,
    TypeVar,
)

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    create_async_engine,
)

from .tables import METADATA

FuncResult = TypeVar("FuncResult")


class Database:
    def __init__(self, dsn: URL, echo: bool = False):
        self.dsn = dsn
        self.engine = create_async_engine(dsn, echo=echo)

    async def ensure_schema(self) -> None:
        await self._run_sync_in_transaction(METADATA.create_all)

    async def drop_schema(self) -> None:
        await self._run_sync_in_transaction(METADATA.drop_all)

    async def execute_in_transaction(
        self, func: Callable[[AsyncConnection], Awaitable[FuncResult]]
    ) -> FuncResult:
        """Execute the given async function in a transaction."""
        async with self.engine.connect() as conn:
            async with conn.begin():
                return await func(conn)

    async def _run_sync_in_transaction(
        self, func: Callable[[Any], FuncResult]
    ) -> FuncResult:
        async with self.engine.connect() as conn:
            async with conn.begin():
                return await conn.run_sync(func)
