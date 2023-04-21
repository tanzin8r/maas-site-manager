from datetime import (
    datetime,
    timedelta,
)

from httpx import AsyncClient
import pytest

from ..fixtures.app import AuthAsyncClient
from ..fixtures.db import Fixture


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
async def test_root_as_auth(
    authenticated_user_app_client: AuthAsyncClient,
) -> None:
    response = await authenticated_user_app_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"version": "0.0.1"}


@pytest.mark.asyncio
async def test_list_sites(
    authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
) -> None:
    site1 = {
        "name": "LondonHQ",
        "city": "London",
        "country": "gb",
        "latitude": "51.509865",
        "longitude": "-0.118092",
        "note": "the first site",
        "region": "Blue Fin Bldg",
        "street": "110 Southwark St",
        "timezone": "Europe/London",
        "url": "https://londoncalling.example.com",
    }
    site2 = site1.copy()
    site2.update(
        {
            "name": "BerlinHQ",
            "timezone": "Europe/Berlin",
            "city": "Berlin",
            "country": "de",
        }
    )
    sites = await fixture.create("site", [site1, site2])
    for site in sites:
        site["stats"] = None
    page1 = await authenticated_user_app_client.get("/sites")
    assert page1.status_code == 200
    assert page1.json() == {
        "page": 1,
        "size": 20,
        "total": 2,
        "items": sites,
    }
    filtered = await authenticated_user_app_client.get(
        "/sites?city=onDo"
    )  # vs London
    assert filtered.status_code == 200
    assert filtered.json() == {
        "page": 1,
        "size": 20,
        "total": 1,
        "items": [sites[0]],
    }
    paginated = await authenticated_user_app_client.get("/sites?page=2&size=1")
    assert paginated.status_code == 200
    assert paginated.json() == {
        "page": 2,
        "size": 1,
        "total": 2,
        "items": [sites[1]],
    }


@pytest.mark.asyncio
async def test_list_sites_filter_timezone(
    authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
) -> None:
    site1 = {
        "name": "LondonHQ",
        "city": "London",
        "country": "gb",
        "latitude": "51.509865",
        "longitude": "-0.118092",
        "note": "the first site",
        "region": "Blue Fin Bldg",
        "street": "110 Southwark St",
        "timezone": "Europe/London",
        "url": "https://londoncalling.example.com",
    }
    site2 = site1.copy()
    site2.update(
        {
            "name": "BerlinHQ",
            "timezone": "Europe/Berlin",
            "city": "Berlin",
            "country": "de",
        }
    )
    [created_site, _] = await fixture.create("site", [site1, site2])
    created_site["stats"] = None
    page1 = await authenticated_user_app_client.get(
        "/sites?timezone=Europe/London"
    )
    assert page1.status_code == 200
    assert page1.json() == {
        "page": 1,
        "size": 20,
        "total": 1,
        "items": [created_site],
    }


@pytest.mark.asyncio
async def test_list_sites_with_stats(
    authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
) -> None:
    [site] = await fixture.create(
        "site",
        [
            {
                "name": "LondonHQ",
                "city": "London",
                "country": "gb",
                "latitude": "51.509865",
                "longitude": "-0.118092",
                "note": "the first site",
                "region": "Blue Fin Bldg",
                "street": "110 Southwark St",
                "timezone": "Europe/London",
                "url": "https://londoncalling.example.com",
            }
        ],
    )
    [site_data] = await fixture.create(
        "site_data",
        [
            {
                "site_id": site["id"],
                "allocated_machines": 10,
                "deployed_machines": 20,
                "ready_machines": 30,
                "error_machines": 40,
                "last_seen": datetime.utcnow(),
            }
        ],
    )
    del site_data["id"]
    del site_data["site_id"]
    site_data["last_seen"] = site_data["last_seen"].isoformat()
    site["stats"] = site_data

    page = await authenticated_user_app_client.get("/sites")
    assert page.status_code == 200
    assert page.json() == {
        "page": 1,
        "size": 20,
        "total": 1,
        "items": [site],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("time_format", ["ISO 8601", "Float"])
async def test_token_time_format(
    time_format: str, authenticated_user_app_client: AuthAsyncClient
) -> None:
    seconds = 100
    expiry = timedelta(seconds=seconds)
    formatted_expiry = duration_format(expiry, time_format)

    response = await authenticated_user_app_client.post(
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


@pytest.mark.asyncio
async def test_login_fails_with_wrong_password(
    user_app_client: AsyncClient, fixture: Fixture
) -> None:
    phash = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
    userdata = {
        "id": 1,
        "email": "admin@example.com",
        "full_name": "Admin",
        "password": phash,
    }
    await fixture.create("user", userdata)

    fail_response = await user_app_client.post(
        "/login",
        data={"username": userdata["email"], "password": "incorrect_pass"},
    )
    assert fail_response.status_code == 401, "Expected authentication error."

    fail_response = await user_app_client.post(
        "/login", data={"username": userdata["email"], "password": "admin"}
    )
    assert fail_response.status_code == 200, "Expected user login."


@pytest.mark.asyncio
async def test_sites_fails_without_login(
    user_app_client: AsyncClient, fixture: Fixture
) -> None:
    site = [
        {
            "name": "LondonHQ",
            "city": "London",
            "country": "gb",
            "latitude": "51.509865",
            "longitude": "-0.118092",
            "note": "the first site",
            "region": "Blue Fin Bldg",
            "street": "110 Southwark St",
            "timezone": "Europe/London",
            "url": "https://londoncalling.example.com",
        }
    ]
    await fixture.create("site", site)
    page1 = await user_app_client.get("/sites")
    assert page1.status_code == 401, "Expected authentication error."


@pytest.mark.asyncio
async def test_token_fails_without_login(user_app_client: AsyncClient) -> None:
    seconds = 100

    response = await user_app_client.post(
        "/tokens", json={"count": 5, "duration": seconds}
    )
    assert response.status_code == 401, "Expected authentication error."
