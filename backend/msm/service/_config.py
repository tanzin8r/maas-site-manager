from typing import (
    Any,
    Iterable,
)

from sqlalchemy import (
    delete,
    insert,
    select,
)

from ..db import models
from ..db.tables import Config
from ..jwt import generate_key
from ._base import Service

CONFIG_KEYS = frozenset(models.Config.model_fields)


class ConfigService(Service):
    async def get(self) -> models.Config:
        """Return the application configuration."""
        stmt = (
            select(Config.c.name, Config.c.value)
            .select_from(Config)
            .where(Config.c.name.in_(CONFIG_KEYS))
        )
        result = await self.conn.execute(stmt)
        return models.Config(**dict(result.all()))  # type: ignore

    async def ensure(self) -> None:
        """Ensure expected settings are present in the db.

        This also removes extra unknown entries.
        """
        result = await self.conn.execute(
            select(Config.c.name).select_from(Config)
        )
        all_keys = set(result.scalars().all())

        # create entries for missing known keys
        if missing_keys := CONFIG_KEYS - all_keys:
            await self.conn.execute(
                insert(Config),
                self._insert_values(missing_keys),
            )

        # delete keys that are not known
        if extra_keys := all_keys - CONFIG_KEYS:
            await self.conn.execute(
                delete(Config).where(Config.c.name.in_(extra_keys))
            )

    def _insert_values(self, keys: Iterable[str]) -> list[dict[str, Any]]:
        values = {
            "token_secret_key": generate_key(),
        }
        return [{"name": key, "value": values[key]} for key in keys]
