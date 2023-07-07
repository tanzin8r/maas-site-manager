from sqlalchemy.ext.asyncio import AsyncSession


class Service:
    """Base class for services."""

    def __init__(self, session: AsyncSession):
        self.session = session
