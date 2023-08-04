from typing import cast

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import Database


@pytest.mark.asyncio
class TestDatabase:
    async def test_execute_in_transaction(self, db: Database) -> None:
        async def get_txid(conn: AsyncConnection) -> int:
            result = await conn.execute(text("SELECT txid_current()"))
            return cast(int, result.scalar())

        txid1 = await db.execute_in_transaction(get_txid)
        txid2 = await db.execute_in_transaction(get_txid)
        assert txid1 != txid2
