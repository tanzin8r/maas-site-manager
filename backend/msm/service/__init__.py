from sqlalchemy.ext.asyncio import AsyncConnection

from ._config import ConfigService
from ._settings import SettingsService
from ._site import (
    InvalidPendingSites,
    SiteService,
)
from ._token import TokenService
from ._user import UserService


class ServiceCollection:
    """Provide all services."""

    def __init__(self, connection: AsyncConnection):
        self.sites = SiteService(connection)
        self.tokens = TokenService(connection)
        self.users = UserService(connection)
        self.settings = SettingsService(connection)


__all__ = [
    "ConfigService",
    "InvalidPendingSites",
    "ServiceCollection",
    "SettingsService",
    "SiteService",
    "TokenService",
    "UserService",
]
