from collections.abc import AsyncIterator
from typing import (
    Annotated,
    Iterator,
)

from fastapi import (
    Depends,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..service import ServiceCollection


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


def services(
    session: Annotated[AsyncSession, Depends(db_session)]
) -> Iterator[ServiceCollection]:
    """Provide the ServiceCollection to access services."""
    yield ServiceCollection(session)
