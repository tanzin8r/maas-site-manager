from collections.abc import Iterable
from socket import gethostname
from typing import (
    Any,
)

from ..db import models
from ..db.tables import Setting
from ..settings import Settings
from ._base import DBBackedModelService


class SettingsService(DBBackedModelService[models.Settings]):
    """Service to access global settings."""

    db_table = Setting

    def _default_values(self, keys: Iterable[str]) -> list[dict[str, Any]]:
        # override the method to generate the default service URL
        settings = Settings()
        values = {
            "service_url": f"http://{gethostname()}:{settings.api_port}",
        }
        return [{"name": key, "value": values[key]} for key in keys]
