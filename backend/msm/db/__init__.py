from typing import (
    Any,
    Callable,
)

from sqlalchemy.ext.asyncio import create_async_engine

from .tables import METADATA


class Database:
    def __init__(self, dsn: str, echo: bool = False):
        self.dsn = dsn
        self.engine = create_async_engine(dsn, echo=echo)

    async def ensure_schema(self) -> None:
        await self._run_sync_in_transaction(METADATA.create_all)

    async def drop_schema(self) -> None:
        await self._run_sync_in_transaction(METADATA.drop_all)

    async def _run_sync_in_transaction(
        self, func: Callable[[Any], Any]
    ) -> None:
        async with self.engine.connect() as conn:
            async with conn.begin():
                # ensure schema is created
                await conn.run_sync(func)
