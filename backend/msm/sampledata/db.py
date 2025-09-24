import dataclasses
from functools import cached_property
from typing import Any

from sqlalchemy import Table
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.apiserver.db import CUSTOM_IMAGE_SOURCE_ID
from msm.apiserver.db.tables import METADATA


class SampleDataModel:
    """Base class for table-based models."""

    def __getattr__(self, name: str) -> Any:
        # defined to skip type checking dynamic attributes
        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        # defined to skip type checking dynamic attributes
        raise AttributeError(name)


class ModelCollection:
    """Handle inserting, deleting, and returning table entries with the database."""

    def __init__(self, table: str):
        self.table_name = table
        self._entries: list[dict[str, Any]] = []

    @property
    def db_table(self) -> Table:
        """The database table."""
        return METADATA.tables[self.table_name]

    def add(self, **details: Any) -> None:
        """Add an entry to the collection."""
        self._entries.append(details)

    async def purge(
        self, conn: AsyncConnection, retain_custom_source: bool = False
    ) -> None:
        """Purge (empty) a table, optionally keeping the custom images source"""
        stmt = METADATA.tables[self.table_name].delete()
        if retain_custom_source:
            stmt = stmt.where(
                METADATA.tables[self.table_name].c.id != CUSTOM_IMAGE_SOURCE_ID
            )
        await conn.execute(stmt)

    async def create(self, conn: AsyncConnection) -> list[SampleDataModel]:
        """Create current entries in the database.

        This clears cached entries.
        """
        result = await conn.execute(
            METADATA.tables[self.table_name].insert().returning("*"),
            self._entries,
        )
        models = [self._table_model(**row._asdict()) for row in result]
        self._entries.clear()
        return models

    @cached_property
    def _table_model(self) -> type[SampleDataModel]:
        fields = []
        for column in self.db_table.c:
            try:
                python_type = column.type.python_type
                if column.nullable:
                    python_type |= None  # type: ignore
            except NotImplementedError:
                python_type = Any  # type: ignore
            fields.append((column.name, python_type))

        return dataclasses.make_dataclass(
            self.table_name,
            fields,
            bases=(SampleDataModel,),
            frozen=True,
        )
