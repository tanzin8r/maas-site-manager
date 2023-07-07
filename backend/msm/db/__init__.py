from sqlalchemy.ext.asyncio import create_async_engine

from .tables import METADATA


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.engine = create_async_engine(dsn)

    async def setup(self) -> None:
        async with self.engine.connect() as conn:
            async with conn.begin():
                # ensure schema is created
                await conn.run_sync(METADATA.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()
