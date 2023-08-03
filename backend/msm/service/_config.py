from sqlalchemy import select

from ..db import models
from ..db.tables import Config
from ._base import Service


class ConfigService(Service):
    async def get(self) -> models.Config:
        """Return the application configuration."""
        config_keys = set(models.Config.model_fields)
        stmt = (
            select(Config.c.name, Config.c.value)
            .select_from(Config)
            .where(Config.c.name.in_(config_keys))
        )
        result = await self.conn.execute(stmt)
        return models.Config(**dict(result.all()))  # type: ignore
