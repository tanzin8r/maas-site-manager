from typing import cast

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.apiserver.db import Database


async def get_txid(conn: AsyncConnection) -> int:
    """Return the current transction ID."""
    result = await conn.execute(text("SELECT txid_current()"))
    return cast(int, result.scalar())


@pytest.mark.asyncio
class TestDatabase:
    async def test_execute_in_transaction(self, db: Database) -> None:
        txid1 = await db.execute_in_transaction(get_txid)
        txid2 = await db.execute_in_transaction(get_txid)
        assert txid1 != txid2

    async def test_transaction_context_manager(self, db: Database) -> None:
        async with db.transaction() as conn:
            txid1 = await get_txid(conn)
        async with db.transaction() as conn:
            txid2 = await get_txid(conn)
        assert txid1 != txid2
