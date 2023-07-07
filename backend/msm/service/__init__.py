from sqlalchemy.ext.asyncio import AsyncSession

from ._token import TokenService


class ServiceCollection:
    """Provide all services."""

    def __init__(self, session: AsyncSession):
        self.tokens = TokenService((session))


__all__ = ["ServiceCollection"]
