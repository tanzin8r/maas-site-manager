from datetime import (
    datetime,
    timedelta,
)

import pytest

from ...fixtures.client import Client
from ...fixtures.factory import Factory


def duration_format(delta: timedelta, time_format: str) -> str:
    s = int(delta.total_seconds())
    match time_format:
        case "iso8601":
            return f"PT{s // 60 // 60}H{s // 60 % 60}M{s % 60}S"
        case "float":
            return str(s)
        case _:
            raise ValueError(f"Invalid time format {time_format}")


@pytest.mark.asyncio
@pytest.mark.parametrize("time_format", ["iso8601", "float"])
async def test_token_time_format(
    time_format: str, user_client: Client
) -> None:
    seconds = 100
    expiry = timedelta(seconds=seconds)
    formatted_expiry = duration_format(expiry, time_format)

    response = await user_client.post(
        "/tokens", json={"duration": formatted_expiry}
    )
    assert response.status_code == 200
    result = response.json()
    assert datetime.fromisoformat(result["expired"]) < (
        datetime.utcnow() + expiry
    )


@pytest.mark.asyncio
async def test_tokens_get(user_client: Client, factory: Factory) -> None:
    tokens = [
        await factory.make_Token(),
        await factory.make_Token(),
    ]

    expected = []
    for token in tokens:
        entry = token.dict()
        entry["expired"] = token.expired.isoformat()
        entry["created"] = token.created.isoformat()
        entry["value"] = str(token.value)
        expected.append(entry)

    response = await user_client.get("/tokens")
    assert response.status_code == 200
    assert response.json()["total"] == len(expected)
    assert response.json()["items"] == expected
