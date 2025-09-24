from datetime import (
    datetime,
    timedelta,
)

import pytest

from msm.apiserver.db.models import Token
from msm.common.jwt import TokenAudience, TokenPurpose
from msm.common.time import now_utc


class TestToken:
    @pytest.mark.parametrize(
        "expired,is_expired",
        [
            (now_utc() + timedelta(hours=1), False),
            (now_utc() - timedelta(hours=1), True),
        ],
    )
    def test_is_expired(self, expired: datetime, is_expired: bool) -> None:
        token = Token(
            id=1,
            value="a-b-c",
            audience=TokenAudience.SITE,
            purpose=TokenPurpose.ENROLMENT,
            expired=expired,
            created=now_utc(),
        )
        assert token.is_expired() is is_expired
