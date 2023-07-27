from datetime import (
    datetime,
    timedelta,
)

import pytest

from ...fixtures.client import Client
from ...fixtures.factory import Factory


def iso8601_duration(duration: timedelta) -> str:
    s = int(duration.total_seconds())
    return f"PT{s // 60 // 60}H{s // 60 % 60}M{s % 60}S"


@pytest.mark.asyncio
async def test_token_time_format(user_client: Client) -> None:
    expiry = timedelta(seconds=100)
    response = await user_client.post(
        "/tokens", json={"duration": iso8601_duration(expiry)}
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
        entry = token.model_dump()
        entry["expired"] = token.expired.isoformat()
        entry["created"] = token.created.isoformat()
        entry["value"] = str(token.value)
        expected.append(entry)

    response = await user_client.get("/tokens")
    assert response.status_code == 200
    assert response.json()["total"] == len(expected)
    assert response.json()["items"] == expected
