from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    create_async_engine,
)

from ._tables import METADATA


class Database:
    dsn: str
    conn: AsyncConnection | None

    def __init__(self, dsn: str):
        self.dsn = dsn
        self._engine = create_async_engine(dsn)
        self.conn = None

    async def connect(self) -> None:
        if self.conn is not None:
            await self.conn.close()
        self.conn = await self._engine.connect()
        # ensure schema is created
        await self.conn.run_sync(METADATA.create_all)
        await self.conn.commit()

    async def disconnect(self) -> None:
        if self.conn is None:
            return
        await self.conn.close()
        await self._engine.dispose()

    def session(self) -> AsyncSession:
        return AsyncSession(self._engine)
