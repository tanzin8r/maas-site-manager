from collections.abc import Iterable
from functools import cached_property
from typing import (
    Any,
    Generic,
    TypeVar,
    cast,
)

from pydantic import BaseModel
from sqlalchemy import (
    CursorResult,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql.expression import bindparam

Model = TypeVar("Model", bound=BaseModel)


class Service:
    """Base class for services."""

    def __init__(self, connection: AsyncConnection):
        self.conn = connection

    def objects_from_result(
        self, model: type[Model], result: CursorResult[Any]
    ) -> Iterable[Model]:
        """Return an iterable of model instances from a query result."""
        return (model(**row._asdict()) for row in result.all())


class DBBackedModelService(Service, Generic[Model]):
    """This service allows getting and setting values for a Pydantic model
    backed by a database table.

    The table is expected to have the following columns:
      - name (Text)
      - value (JSONB)

    Subclasses must inherit this as DBBackedModelService[Model] declaring the
    related (Pydantic) Model class.
    """

    # the database table backing the model
    db_table: Table

    @cached_property
    def valid_keys(self) -> frozenset[str]:
        return frozenset(self._model.model_fields)

    async def get(self) -> Model:
        """Return the model instance."""
        stmt = (
            select(self.db_table.c.name, self.db_table.c.value)
            .select_from(self.db_table)
            .where(self.db_table.c.name.in_(self.valid_keys))
        )
        result = await self.conn.execute(stmt)
        return self._model(**dict(result.all()))  # type: ignore

    async def update(self, values: dict[str, Any]) -> None:
        """Update settings.

        Only values that are not null are considered.
        """
        # filter only acceptable values
        query_values = [
            {
                "key": key,
                "value": value,
            }
            for key, value in values.items()
            if key in self.valid_keys and value is not None
        ]
        if not query_values:
            return
        stmt = (
            update(self.db_table)
            .where(self.db_table.c.name == bindparam("key"))
            .values({"value": bindparam("value")})
        )
        await self.conn.execute(stmt, query_values)

    async def ensure(self) -> None:
        """Ensure expected settings are present in the db.

        This also removes extra unknown entries.
        """
        result = await self.conn.execute(
            select(self.db_table.c.name).select_from(self.db_table)
        )
        all_keys = set(result.scalars().all())

        # create entries for missing known keys
        if missing_keys := self.valid_keys - all_keys:
            await self.conn.execute(
                insert(self.db_table),
                self._default_values(missing_keys),
            )

        # delete keys that are not known
        if extra_keys := all_keys - self.valid_keys:
            await self.conn.execute(
                delete(self.db_table).where(
                    self.db_table.c.name.in_(extra_keys)
                )
            )

    @cached_property
    def _model(self) -> type[Model]:
        """The Pydantic model associated to the class.

        Given that the class is a Generic[T], parametric on the Pydantic model
        class, this inspects declared type to find the model class.
        """
        return cast(Model, self.__orig_bases__[0].__args__[0])  # type: ignore

    def _default_values(self, keys: Iterable[str]) -> list[dict[str, Any]]:
        """Provide default values for the specified keys."""
        return [
            {"name": key, "value": self._model.model_fields[key].default}
            for key in keys
        ]
