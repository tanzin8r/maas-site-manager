from collections.abc import Iterable
from typing import (
    Any,
)
from uuid import uuid4

from msm.db import models
from msm.db.tables import Config
from msm.jwt import generate_key
from msm.service._base import DBBackedModelService


class ConfigService(DBBackedModelService[models.Config]):
    db_table = Config

    def _default_values(self, keys: Iterable[str]) -> list[dict[str, Any]]:
        # override the method to generate a default key.
        values = {
            "service_identifier": str(uuid4()),
            "token_secret_key": generate_key(),
        }
        return [{"name": key, "value": values[key]} for key in keys]
