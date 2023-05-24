from datetime import (
    datetime,
    timedelta,
)
from typing import Any

from httpx import (
    AsyncClient,
    Response,
)
import pytest

from msm import __version__

from ..fixtures.app import AuthAsyncClient
from ..fixtures.db import Fixture


def duration_format(delta: timedelta, time_format: str) -> str:
    s = int(delta.total_seconds())
    match time_format:
        case "iso8601":
            return f"PT{s // 60 // 60}H{s // 60 % 60}M{s % 60}S"
        case "float":
            return str(s)
        case _:
            raise ValueError(f"Invalid time format {time_format}")


def site_details(**extra_details: Any) -> dict[str, Any]:
    """Return sample details for creating a site."""
    details = {
        "name": "LondonHQ",
        "name_unique": True,
        "url": "https://londoncalling.example.com",
        "accepted": True,
    }
    details.update(extra_details)
    return details


@pytest.mark.asyncio
class TestRootHandler:
    async def test_get(self, user_app_client: AsyncClient) -> None:
        response = await user_app_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"version": __version__}

    async def test_get_authenticated(
        self,
        authenticated_user_app_client: AuthAsyncClient,
    ) -> None:
        response = await authenticated_user_app_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"version": __version__}


@pytest.mark.asyncio
class TestSitesHandler:
    async def test_get(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        sites = await fixture.create(
            "site",
            [
                site_details(city="London"),
                site_details(name="BerlinHQ", city="Berlin"),
            ],
            commit=True,
        )
        for site in sites:
            site["stats"] = None
            del site["created"]
            del site["accepted"]

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
        paginated = await authenticated_user_app_client.get(
            "/sites?page=2&size=1"
        )
        assert paginated.status_code == 200
        assert paginated.json() == {
            "page": 2,
            "size": 1,
            "total": 2,
            "items": [sites[1]],
        }

    async def test_get_only_accepted(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        created_site, _ = await fixture.create(
            "site",
            [
                site_details(),
                site_details(name="BerlinHQ", accepted=False),
            ],
            commit=True,
        )
        created_site["stats"] = None
        del created_site["created"]
        del created_site["accepted"]

        page1 = await authenticated_user_app_client.get("/sites")
        assert page1.status_code == 200
        assert page1.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [created_site],
        }

    async def test_get_filter_timezone(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        [created_site, _] = await fixture.create(
            "site",
            [
                site_details(timezone="Europe/London"),
                site_details(name="BerlinHQ", timezone="Europe/Berlin"),
            ],
            commit=True,
        )
        created_site["stats"] = None
        del created_site["created"]
        del created_site["accepted"]
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

    async def test_get_with_stats(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        [site] = await fixture.create("site", [site_details()], commit=True)
        [site_data] = await fixture.create(
            "site_data",
            [
                {
                    "site_id": site["id"],
                    "allocated_machines": 10,
                    "deployed_machines": 20,
                    "ready_machines": 30,
                    "error_machines": 40,
                    "other_machines": 5,
                    "last_seen": datetime.utcnow(),
                }
            ],
            commit=True,
        )
        del site_data["id"]
        del site_data["site_id"]
        site_data["last_seen"] = site_data["last_seen"].isoformat()
        site_data["total_machines"] = 105
        site["stats"] = site_data
        del site["created"]
        del site["accepted"]

        page = await authenticated_user_app_client.get("/sites")
        assert page.status_code == 200
        assert page.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [site],
        }

    @pytest.mark.parametrize(
        "query_params, expected_result",
        [
            ("sort_by=city-asc", ["London", "Milan", "Paris", "Rome"]),
            (
                "sort_by=city,name,name_unique,country,region,street,timezone",
                ["London", "Milan", "Paris", "Rome"],
            ),
            ("sort_by=city-asc", ["London", "Milan", "Paris", "Rome"]),
            ("sort_by=city-desc", ["Rome", "Paris", "Milan", "London"]),
            (
                "sort_by=country,city-desc",
                ["Paris", "London", "Rome", "Milan"],
            ),
            ("sort_by=country,city-asc", ["Paris", "London", "Milan", "Rome"]),
            ("page=2&size=2&sort_by=country,city-asc", ["Milan", "Rome"]),
        ],
    )
    async def test_get_with_sorting(
        self,
        authenticated_user_app_client: AuthAsyncClient,
        fixture: Fixture,
        query_params: str,
        expected_result: list[str],
    ) -> None:
        def extract_cities(resp: Response) -> list[str]:
            return [site["city"] for site in resp.json()["items"]]

        await fixture.create(
            "site",
            [site_details(city="Milan", country="IT")],
            commit=True,
        )
        await fixture.create(
            "site",
            [site_details(city="Paris", country="FR")],
            commit=True,
        )
        await fixture.create(
            "site", [site_details(city="Rome", country="IT")], commit=True
        )
        await fixture.create(
            "site", [site_details(city="London", country="GB")], commit=True
        )

        response = await authenticated_user_app_client.get(
            "/sites", params=query_params
        )
        assert extract_cities(response) == expected_result

    @pytest.mark.parametrize(
        "query_params",
        ["sort_by=id-asc", "sort_by=city,city", "sort_by=doesnotexist"],
    )
    async def test_get_with_invalid_sorting(
        self,
        authenticated_user_app_client: AuthAsyncClient,
        fixture: Fixture,
        query_params: str,
    ) -> None:
        await fixture.create(
            "site", [site_details(city="Milan", country="IT")], commit=True
        )

        # not sortable
        response = await authenticated_user_app_client.get(
            "/sites", params=query_params
        )
        assert response.status_code == 400


@pytest.mark.asyncio
class TestPendingSitesHandler:
    async def test_get(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        _, pending_site = await fixture.create(
            "site",
            [
                site_details(),
                site_details(name="BerlinHQ", accepted=False),
            ],
            commit=True,
        )

        response = await authenticated_user_app_client.get("/requests")
        assert response.status_code == 200
        assert response.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [
                {
                    "id": pending_site["id"],
                    "name": pending_site["name"],
                    "url": pending_site["url"],
                    "created": pending_site["created"].isoformat(),
                },
            ],
        }

    async def test_post_accept(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        [pending_site] = await fixture.create(
            "site", [site_details(accepted=False)], commit=True
        )

        response = await authenticated_user_app_client.post(
            "/requests",
            json={"ids": [pending_site["id"]], "accept": True},
        )
        assert response.status_code == 204
        [created_site] = await fixture.get("site")
        assert created_site["accepted"]

    async def test_post_reject(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        [pending_site] = await fixture.create(
            "site", [site_details(accepted=False)], commit=True
        )

        response = await authenticated_user_app_client.post(
            "/requests",
            json={"ids": [pending_site["id"]], "accept": False},
        )
        assert response.status_code == 204
        assert await fixture.get("site") == []

    async def test_post_invalid_ids(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        [site] = await fixture.create("site", [site_details()], commit=True)
        # unknown IDs and IDs for non-pending sites are invalid
        ids = [site["id"], 10000]
        response = await authenticated_user_app_client.post(
            "/requests",
            json={"ids": ids, "accept": True},
        )
        assert response.status_code == 400
        assert response.json() == {
            "detail": {"message": "Unknown pending sites", "ids": ids}
        }


@pytest.mark.asyncio
class TestTokensHandler:
    @pytest.mark.parametrize("time_format", ["iso8601", "float"])
    async def test_token_time_format(
        self, time_format: str, authenticated_user_app_client: AuthAsyncClient
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

    async def test_tokens_get(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
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
            commit=True,
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
class TestLoginHandler:
    async def test_post(
        self, user_app_client: AsyncClient, fixture: Fixture
    ) -> None:
        phash = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
        userdata = {
            "id": 1,
            "email": "admin@example.com",
            "full_name": "Admin",
            "password": phash,
        }
        await fixture.create("user", userdata, commit=True)
        response = await user_app_client.post(
            "/login",
            json={"username": userdata["email"], "password": "admin"},
        )
        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"

    async def test_post_fails_with_wrong_password(
        self, user_app_client: AsyncClient, fixture: Fixture
    ) -> None:
        phash = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
        userdata = {
            "id": 1,
            "email": "admin@example.com",
            "full_name": "Admin",
            "password": phash,
        }
        await fixture.create("user", userdata, commit=True)

        fail_response = await user_app_client.post(
            "/login",
            json={"username": userdata["email"], "password": "incorrect_pass"},
        )
        assert fail_response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,url",
    [
        ("GET", "/sites"),
        ("GET", "/requests"),
        ("POST", "/requests"),
        ("GET", "/tokens"),
        ("POST", "/tokens"),
        ("GET", "/users/me"),
    ],
)
async def test_handler_auth_required(
    user_app_client: AsyncClient, method: str, url: str
) -> None:
    response = await user_app_client.request(method, url)
    assert (
        response.status_code == 401
    ), f"Auth should be required for {method} {url}"
