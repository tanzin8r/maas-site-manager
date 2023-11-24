from datetime import (
    datetime,
    timedelta,
)

import pytest

from msm.time import now_utc

from ... import api_timestamp
from ....fixtures.client import Client
from ....fixtures.factory import Factory


def iso8601_duration(duration: timedelta) -> str:
    s = int(duration.total_seconds())
    return f"PT{s // 60 // 60}H{s // 60 % 60}M{s % 60}S"


@pytest.mark.asyncio
class TestTokensPost:
    async def test_create_tokens(
        self, user_client: Client, factory: Factory
    ) -> None:
        response = await user_client.post(
            "/tokens", json={"duration": "1D", "count": 2}
        )
        assert response.status_code == 200
        tokens = response.json()["items"]
        assert len(tokens) == 2
        values = {token["value"] for token in await factory.get("token")}
        assert {token["value"] for token in tokens} == values

    async def test_time_format(self, user_client: Client) -> None:
        expiry = timedelta(seconds=100)
        response = await user_client.post(
            "/tokens", json={"duration": iso8601_duration(expiry)}
        )
        assert response.status_code == 200
        [token] = response.json()["items"]

        # XXX Python3.10 doesn't support parsing ISO timestamps without
        # microseconds and with Z instead of offset. This can be dropped when
        # switching to Python3.11 or later
        expired = token["expired"].replace("Z", ".000000+00:00")
        assert datetime.fromisoformat(expired) < (now_utc() + expiry)


@pytest.mark.asyncio
async def test_tokens_get(user_client: Client, factory: Factory) -> None:
    tokens = [
        await factory.make_Token(),
        await factory.make_Token(),
    ]

    expected = []
    for token in tokens:
        entry = token.model_dump()
        entry["expired"] = api_timestamp(token.expired)
        entry["created"] = api_timestamp(token.created)
        entry["value"] = str(token.value)
        expected.append(entry)

    response = await user_client.get("/tokens")
    assert response.status_code == 200
    assert response.json()["total"] == len(expected)
    assert response.json()["items"] == expected


@pytest.mark.asyncio
async def test_delete(user_client: Client, factory: Factory) -> None:
    token = await factory.make_Token()
    response = await user_client.delete(f"/tokens/{token.id}")
    assert response.status_code == 204
    get_response = await user_client.get("/tokens")
    assert get_response.json()["total"] == 0
