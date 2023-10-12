from datetime import (
    datetime,
    timedelta,
)
import uuid

from msm.api._csv import CSVResponse
from msm.db.models import Token


def isoformat(t: datetime) -> str:
    return t.isoformat(sep=" ")


def test_csv_response() -> None:
    uuid1 = str(uuid.uuid4())
    uuid2 = str(uuid.uuid4())
    now = datetime.utcnow()
    created1 = now - timedelta(hours=1)
    expired1 = now + timedelta(hours=1)
    created2 = now - timedelta(hours=2)
    expired2 = now + timedelta(hours=2)
    tokens = [
        Token(id=1, value=uuid1, expired=expired1, created=created1),
        Token(id=2, value=uuid2, expired=expired2, created=created2),
    ]
    response = CSVResponse(content=tokens)

    assert response.body.decode() == (
        "id,value,expired,created\r\n"
        f"1,{uuid1},{isoformat(expired1)},{isoformat(created1)}\r\n"
        f"2,{uuid2},{isoformat(expired2)},{isoformat(created2)}\r\n"
    )
