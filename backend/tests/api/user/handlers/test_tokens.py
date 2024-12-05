import asyncio
from datetime import (
    datetime,
    timedelta,
)

import pytest

from msm.api.exceptions.constants import ExceptionCode
from msm.api.exceptions.responses import ErrorResponseModel
from msm.time import now_utc
from tests.api import api_timestamp
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


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
        expired = token["expired"]
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
async def test_tokens_export_by_id(
    user_client: Client, factory: Factory
) -> None:
    tokens = await asyncio.gather(*(factory.make_Token() for _ in range(5)))

    response = await user_client.get(
        "/tokens/export", params={"id": [tokens[0].id, tokens[2].id]}
    )

    assert response.status_code == 200
    assert response.text.count("\r\n") == 2 + 1  # 2 times content + 1 header


@pytest.mark.asyncio
async def test_delete(user_client: Client, factory: Factory) -> None:
    token = await factory.make_Token()
    response = await user_client.delete(f"/tokens/{token.id}")
    assert response.status_code == 204
    get_response = await user_client.get("/tokens")
    assert get_response.json()["total"] == 0


@pytest.mark.asyncio
async def test_delete_many(user_client: Client, factory: Factory) -> None:
    token1 = await factory.make_Token()
    token2 = await factory.make_Token()
    token3 = await factory.make_Token()
    response = await user_client.delete(
        f"/tokens?ids={token1.id}&ids={token2.id}"
    )
    assert response.status_code == 204
    get_response = await user_client.get("/tokens")
    assert get_response.json()["total"] == 1
    assert get_response.json()["items"][0]["id"] == token3.id


async def test_delete_many_no_ids(
    user_client: Client, factory: Factory
) -> None:
    await factory.make_Token()
    response = await user_client.delete("/tokens")
    assert response.status_code == 422
    err = ErrorResponseModel(**response.json())
    assert err.error.code == ExceptionCode.INVALID_PARAMS
    assert err.error.details is not None
    assert err.error.details[0].field == "ids"
    assert err.error.details[0].messages == ["Input should be a valid list"]


# TODO: if the handler raises an exception the db transaction should be rollbacked
# NOTE: this problem is only present in tests
async def test_delete_many_not_found(
    user_client: Client, factory: Factory
) -> None:
    token1 = await factory.make_Token()
    token2 = await factory.make_Token()
    fake_id = 9
    response = await user_client.delete(
        f"/tokens?ids={token2.id}&ids={fake_id}"
    )
    assert response.status_code == 404
    err = ErrorResponseModel(**response.json())
    assert err.error.code == ExceptionCode.MISSING_RESOURCE
    assert err.error.message == f"Some of the requested IDs were not found."
    assert err.error.details is not None
    assert (
        err.error.details[0].messages[0]
        == f"The following IDs were not found: {set([fake_id])}."
    )
    get_response = await user_client.get("/tokens")
    # Here the total should be 2
    assert get_response.json()["total"] == 1
    assert get_response.json()["items"][0]["id"] == token1.id
