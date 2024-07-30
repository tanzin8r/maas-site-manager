from collections.abc import Iterable
import os
from socket import gethostname
from typing import (
    Any,
)

from msm.db import models
from msm.db.tables import Setting
from msm.jwt import DEFAULT_TOKEN_DURATION
from msm.service._base import DBBackedModelService
from msm.settings import Settings


class SettingsService(DBBackedModelService[models.Settings]):
    """Service to access global settings."""

    db_table = Setting

    def _default_values(self, keys: Iterable[str]) -> list[dict[str, Any]]:
        # override the method to generate the default service URL
        settings = Settings()
        base_path = os.environ.get(
            "MSM_BASE_PATH", f"http://{gethostname()}:{settings.api_port}"
        )
        values = {
            "service_url": base_path,
            "enrolment_url": f"{base_path}/site/v1/enrol",
            "token_lifetime_minutes": DEFAULT_TOKEN_DURATION.total_seconds()
            // 60,
            "token_rotation_interval_minutes": (
                (DEFAULT_TOKEN_DURATION.total_seconds()) // 60
            )
            // 2,
        }
        return [{"name": key, "value": values[key]} for key in keys]
