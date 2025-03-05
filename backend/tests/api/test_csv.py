from datetime import (
    datetime,
    timedelta,
)
import uuid

from msm.api.csv import CSVResponse
from msm.db.models import Token
from msm.jwt import TokenAudience, TokenPurpose
from msm.time import now_utc


def isoformat(t: datetime) -> str:
    return t.isoformat(sep=" ")


def test_csv_response() -> None:
    uuid1 = str(uuid.uuid4())
    uuid2 = str(uuid.uuid4())
    now = now_utc()
    created1 = now - timedelta(hours=1)
    expired1 = now + timedelta(hours=1)
    created2 = now - timedelta(hours=2)
    expired2 = now + timedelta(hours=2)
    tokens = [
        Token(
            id=1,
            value=uuid1,
            audience=TokenAudience.SITE,
            purpose=TokenPurpose.ENROLMENT,
            expired=expired1,
            created=created1,
        ),
        Token(
            id=2,
            value=uuid2,
            audience=TokenAudience.SITE,
            purpose=TokenPurpose.ENROLMENT,
            expired=expired2,
            created=created2,
        ),
    ]
    response = CSVResponse(content=tokens)

    assert (
        response.body.decode()  # type: ignore
        == (
            "id,value,audience,purpose,expired,created,site_id\r\n"
            f"1,{uuid1},site,enrollment,{isoformat(expired1)},{isoformat(created1)},\r\n"
            f"2,{uuid2},site,enrollment,{isoformat(expired2)},{isoformat(created2)},\r\n"
        )
    )
