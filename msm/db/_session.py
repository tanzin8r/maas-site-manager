from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Context manager to run a section with a DB session."""
    async with request.app.state.db.session() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()
