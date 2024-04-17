from collections.abc import Iterable
from socket import gethostname
from typing import (
    Any,
)

from msm.db import models
from msm.db.tables import Setting
from msm.service._base import DBBackedModelService
from msm.settings import Settings


class SettingsService(DBBackedModelService[models.Settings]):
    """Service to access global settings."""

    db_table = Setting

    def _default_values(self, keys: Iterable[str]) -> list[dict[str, Any]]:
        # override the method to generate the default service URL
        settings = Settings()
        values = {
            "service_url": f"http://{gethostname()}:{settings.api_port}",
            "enrolment_url": f"http://{gethostname()}:{settings.api_port}/site/v1/enrol",
        }
        return [{"name": key, "value": values[key]} for key in keys]
