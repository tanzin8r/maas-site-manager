from datetime import (
    datetime,
    timedelta,
)

# from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

from ...testing.db import Fixture


def duration_format(time: timedelta, time_format: str) -> str:
    # check if the format matches any pre-defined forms
    match time_format.lower().split()[0]:
        case "iso":
            d, s = time.days, time.seconds
            isostring = {
                "P": True,
                "Y": d // 365,
                "D": d % 365,
                "T": s > 0 or d == 0,
                "H": s // 60 // 60,
                "M": s // 60 % 60,
                "S": s % 60 or "0",
            }
            return "".join(
                f"{val}{char}" if val else ""
                for char, val in isostring.items()
            ).replace("True", "")
    return str(int(time.total_seconds()))


@pytest.mark.asyncio
async def test_root(user_app_client: AsyncClient) -> None:
    response = await user_app_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"version": "0.0.1"}


@pytest.mark.asyncio
async def test_list_sites(
    user_app_client: AsyncClient, fixture: Fixture
) -> None:
    site1 = {
        "id": 1,
        "name": "LondonHQ",
        "city": "London",
        "country": "gb",
        "latitude": "51.509865",
        "longitude": "-0.118092",
        "note": "the first site",
        "region": "Blue Fin Bldg",
        "street": "110 Southwark St",
        "timezone": "0.00",
        "url": "https://londoncalling.example.com",
    }
    site2 = site1.copy()
    site2["id"] = 2
    site2["name"] = "BerlinHQ"
    site2["timezone"] = "1.00"
    site2["city"] = "Berlin"
    site2["country"] = "de"
    await fixture.create("sites", [site1, site2])
    page1 = await user_app_client.get("/sites")
    assert page1.status_code == 200
    assert page1.json() == {
        "page": 1,
        "size": 20,
        "total": 2,
        "items": [site1, site2],
    }
    filtered = await user_app_client.get("/sites?city=onDo")  # vs London
    assert filtered.status_code == 200
    assert filtered.json() == {
        "page": 1,
        "size": 20,
        "total": 1,
        "items": [site1],
    }
    paginated = await user_app_client.get("/sites?page=2&size=1")
    assert paginated.status_code == 200
    assert paginated.json() == {
        "page": 2,
        "size": 1,
        "total": 2,
        "items": [site2],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("time_format", ["ISO 8601", "Float"])
async def test_token_time_format(
    time_format: str, user_app_client: AsyncClient
) -> None:
    seconds = 100
    expiry = timedelta(seconds=seconds)
    formatted_expiry = duration_format(expiry, time_format)

    response = await user_app_client.post(
        "/tokens", json={"count": 5, "duration": formatted_expiry}
    )
    assert response.status_code == 200
    result = response.json()
    assert datetime.fromisoformat(result["expired"]) < (
        datetime.utcnow() + timedelta(seconds=seconds)
    )
    assert len(result["tokens"]) == 5


@pytest.mark.asyncio
async def test_list_tokens(
    user_app_client: AsyncClient, fixture: Fixture
) -> None:
    tokens = [
        {
            "id": 1,
            "site_id": None,
            "value": "c54e5ba6-d214-40dd-b601-01ebb1019c07",
            "expired": datetime.fromisoformat("2023-02-23T09:09:51.103703"),
            "created": datetime.fromisoformat("2023-02-22T03:14:15.926535"),
        },
        {
            "id": 2,
            "site_id": None,
            "value": "b67c449e-fcf6-4014-887d-909859f9fb70",
            "expired": datetime.fromisoformat("2023-02-23T11:28:54.382456"),
            "created": datetime.fromisoformat("2023-02-22T03:14:15.926535"),
        },
    ]
    await fixture.create("tokens", tokens)
    response = await user_app_client.get("/tokens")
    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert len(response.json()["items"]) == 2
