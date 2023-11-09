from typing import (
    Any,
    Iterable,
)
from uuid import uuid4

from ..db import models
from ..db.tables import Config
from ..jwt import generate_key
from ._base import DBBackedModelService


class ConfigService(DBBackedModelService[models.Config]):
    db_table = Config

    def _default_values(self, keys: Iterable[str]) -> list[dict[str, Any]]:
        # override the method to generate a default key.
        values = {
            "service_identifier": str(uuid4()),
            "token_secret_key": generate_key(),
        }
        return [{"name": key, "value": values[key]} for key in keys]
