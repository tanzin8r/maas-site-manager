from sqlalchemy.ext.asyncio import AsyncConnection

from msm.service._config import ConfigService
from msm.service._settings import SettingsService
from msm.service._site import (
    InvalidPendingSites,
    SiteService,
)
from msm.service._token import TokenService
from msm.service._user import UserService


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
