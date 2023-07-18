from typing import (
    Any,
    Iterator,
)

import pytest
from sqlalchemy import ColumnOperators
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.tables import METADATA


class Factory:
    """Helper for creating test fixtures."""

    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def create(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        result = await self.conn.execute(
            METADATA.tables[table].insert().returning("*"), data
        )
        return [row._asdict() for row in result]

    async def get(
        self,
        table: str,
        *filters: ColumnOperators,
    ) -> list[dict[str, Any]]:
        """Take a peak what is in there"""
        result = await self.conn.execute(
            METADATA.tables[table]
            .select()
            .where(*filters)  # type: ignore[arg-type]
        )
        return [row._asdict() for row in result]


@pytest.fixture
def factory(db_connection: AsyncConnection) -> Iterator[Factory]:
    yield Factory(db_connection)
