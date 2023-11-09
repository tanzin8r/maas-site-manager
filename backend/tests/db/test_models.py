from datetime import (
    datetime,
    timedelta,
)

import pytest

from msm.db.models import Token


class TestToken:
    @pytest.mark.parametrize(
        "expired,is_expired",
        [
            (datetime.utcnow() + timedelta(hours=1), False),
            (datetime.utcnow() - timedelta(hours=1), True),
        ],
    )
    def test_is_expired(self, expired: datetime, is_expired: bool) -> None:
        token = Token(
            id=1, value="a-b-c", expired=expired, created=datetime.utcnow()
        )
        assert token.is_expired() is is_expired
