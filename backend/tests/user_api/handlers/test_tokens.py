from datetime import (
    datetime,
    timedelta,
)

import pytest

from ...fixtures.app import AuthAsyncClient
from ...fixtures.db import Fixture


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
    time_format: str, authenticated_user_app_client: AuthAsyncClient
) -> None:
    seconds = 100
    expiry = timedelta(seconds=seconds)
    formatted_expiry = duration_format(expiry, time_format)

    response = await authenticated_user_app_client.post(
        "/tokens", json={"duration": formatted_expiry}
    )
    assert response.status_code == 200
    result = response.json()
    assert datetime.fromisoformat(result["expired"]) < (
        datetime.utcnow() + expiry
    )


@pytest.mark.asyncio
async def test_tokens_get(
    authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
) -> None:
    tokens = await fixture.create(
        "token",
        [
            {
                "site_id": None,
                "value": "c54e5ba6-d214-40dd-b601-01ebb1019c07",
                "expired": datetime.fromisoformat(
                    "2023-02-23T09:09:51.103703"
                ),
                "created": datetime.fromisoformat(
                    "2023-02-22T03:14:15.926535"
                ),
            },
            {
                "site_id": None,
                "value": "b67c449e-fcf6-4014-887d-909859f9fb70",
                "expired": datetime.fromisoformat(
                    "2023-02-23T11:28:54.382456"
                ),
                "created": datetime.fromisoformat(
                    "2023-02-22T03:14:15.926535"
                ),
            },
        ],
    )
    for token in tokens:
        token["expired"] = token["expired"].isoformat()
        token["created"] = token["created"].isoformat()
        token["value"] = str(token["value"])
    response = await authenticated_user_app_client.get("/tokens")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["items"] == tokens
