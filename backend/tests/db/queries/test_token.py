from datetime import (
    datetime,
    timedelta,
)
import uuid

import pytest
from sqlalchemy.ext.asyncio.session import AsyncSession

from msm.db.queries._token import get_active_tokens

from ...fixtures.db import Fixture


@pytest.mark.asyncio
async def test_get_active_tokens(
    fixture: Fixture, session: AsyncSession
) -> None:
    now = datetime.utcnow()
    uuid1, uuid2, uuid3 = [uuid.uuid4() for _ in range(3)]
    _, t2, t3 = await fixture.create(
        "token",
        [
            {
                "value": uuid1,
                "expired": now - timedelta(hours=1),
            },
            {
                "value": uuid2,
                "expired": now + timedelta(hours=1),
            },
            {
                "value": uuid3,
                "expired": now + timedelta(hours=2),
            },
        ],
    )
    assert [token.value for token in await get_active_tokens(session)] == [
        uuid2,
        uuid3,
    ]
