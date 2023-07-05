from datetime import (
    datetime,
    timedelta,
)
import random
from typing import Any

from httpx import (
    AsyncClient,
    Response,
)
import pytest

from msm import __version__
from msm.db.models import ConnectionStatus
from msm.settings import SETTINGS
from msm.user_api._jwt import get_password_hash

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


def random_sample_dict(
    dictionary: dict[str, Any], requires: dict[str, dict[str, Any]] = {}
) -> dict[str, Any]:
    """
    Generate a random subset of ${dictionary}.
    If any keys in ${requires} are present in the sample,
    the corresponding dict will also be included.
    """
    sample = dict(
        [
            (k, dictionary[k])
            for k in random.choices(
                list(dictionary.keys()),
                k=random.randint(1, len(dictionary)),
            )
        ]
    )
    for k, v in requires.items():
        if k in sample:
            sample |= v
    return sample


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
            site["connection_status"] = ConnectionStatus.UNKNOWN
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
        created_site["connection_status"] = ConnectionStatus.UNKNOWN
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
        created_site["connection_status"] = ConnectionStatus.UNKNOWN
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
        site["connection_status"] = ConnectionStatus.STABLE
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

    async def test_get_connection_status(
        self, authenticated_user_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        [site] = await fixture.create("site", [site_details()])
        await fixture.create(
            "site_data",
            [
                {
                    "site_id": site["id"],
                    "allocated_machines": 10,
                    "deployed_machines": 20,
                    "ready_machines": 30,
                    "error_machines": 40,
                    "other_machines": 5,
                    # Set last_seen to 1 second after the
                    # lost_connection_threshold setting in order to test
                    # that the connection is marked as lost
                    "last_seen": datetime.utcnow()
                    - timedelta(
                        seconds=SETTINGS.lost_connection_threshold_seconds + 1
                    ),
                },
            ],
            commit=True,
        )

        page = await authenticated_user_app_client.get("/sites")
        assert page.status_code == 200
        assert (
            page.json()["items"][0]["connection_status"]
            == ConnectionStatus.LOST
        )

    @pytest.mark.parametrize(
        "query_params, expected_result",
        [
            ("sort_by=city-asc", ["London", "Milan", "Paris", "Rome"]),
            (
                "sort_by=city,name,name_unique,country,region,street,"
                "timezone,connection_status",
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
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin",
            "password": phash,
            "is_admin": True,
        }
        await fixture.create("user", userdata, commit=True)
        response = await user_app_client.post(
            "/login",
            json={"email": userdata["email"], "password": "admin"},
        )
        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"

    async def test_post_fails_with_wrong_password(
        self, user_app_client: AsyncClient, fixture: Fixture
    ) -> None:
        phash = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
        userdata = {
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin",
            "password": phash,
            "is_admin": True,
        }
        await fixture.create("user", userdata, commit=True)

        fail_response = await user_app_client.post(
            "/login",
            json={"email": userdata["email"], "password": "incorrect_pass"},
        )
        assert fail_response.status_code == 401


@pytest.mark.asyncio
class TestUsersHandler:
    async def test_users_get(
        self, user_app_client: AsyncClient, fixture: Fixture
    ) -> None:
        phash1 = "$2b$12$F5sgrhRNtWAOehcoVO.XK.oSvupmcg8.0T2jCHOTg15M8N8LrpRwS"
        phash2 = "$2b$12$iEPLFcNocyeUDgu2ywDVGeFHyrksI89bzSvdAwvU1N4zYFtofme3S"
        users = await fixture.create(
            "user",
            [
                {
                    "email": "admin@example.com",
                    "username": "admin",
                    "full_name": "Admin",
                    "password": phash1,
                    "is_admin": True,
                },
                {
                    "email": "user@example.com",
                    "username": "user",
                    "full_name": "MAAS User",
                    "password": phash2,
                    "is_admin": False,
                },
            ],
            commit=True,
        )
        # the return data does not include passwords
        for user in users:
            user.pop("password")

        response = await user_app_client.post(
            "/login",
            json={"email": "admin@example.com", "password": "admin"},
        )
        assert response.status_code == 200

        user_list = await user_app_client.get(
            "/users",
            headers={
                "Authorization": " ".join(
                    [
                        response.json()["token_type"].capitalize(),
                        response.json()["access_token"],
                    ]
                )
            },
        )
        assert user_list.status_code == 200
        assert user_list.json()["total"] == len(users)
        assert user_list.json()["items"] == users

    @pytest.mark.parametrize(
        "query_params, expected_result",
        [
            (
                {"sort_by": "username-asc"},
                ["admin", "alphacen", "hatp13", "proxima", "trappist"],
            ),
            (
                {"sort_by": "username,full_name,email,is_admin"},
                ["admin", "alphacen", "hatp13", "proxima", "trappist"],
            ),
            (
                {"sort_by": "username-desc"},
                ["trappist", "proxima", "hatp13", "alphacen", "admin"],
            ),
            (
                {"sort_by": "full_name,email-desc"},
                ["admin", "hatp13", "proxima", "alphacen", "trappist"],
            ),
            (
                {"sort_by": "is_admin,full_name-desc"},
                ["alphacen", "proxima", "hatp13", "trappist", "admin"],
            ),
            (
                {"page": 2, "size": 2, "sort_by": "username,email-asc"},
                ["hatp13", "proxima"],
            ),
            (
                {"search_text": "@example"},
                ["admin", "hatp13", "alphacen"],
            ),
            ({"search_text": "Bob+Smith", "page": 1}, []),
            (
                {"search_text": "aur", "sort_by": "username-desc"},
                ["proxima", "alphacen"],
            ),
            (
                {"sort_by": "full_name-asc", "search_text": " b"},
                ["hatp13", "proxima"],
            ),
        ],
    )
    async def test_users_get_with_params(
        self,
        authenticated_admin_app_client: AuthAsyncClient,
        fixture: Fixture,
        query_params: str,
        expected_result: list[str],
    ) -> None:
        def extract_users(resp: Response) -> list[str]:
            return [user["username"] for user in resp.json()["items"]]

        async def create_user(
            username: str,
            password: str,
            email: str,
            full_name: str,
            is_admin: bool = False,
        ) -> None:
            await fixture.create(
                "user",
                {
                    "email": email,
                    "username": username,
                    "full_name": full_name,
                    "password": get_password_hash(password),
                    "confirm_password": get_password_hash(password),
                    "is_admin": is_admin,
                },
                commit=True,
            )

        await create_user(
            "proxima",
            "password1",
            "proxima@maas-site-manager.example.com",
            "Proxima Centauri b",
        )
        await create_user(
            "trappist",
            "password2",
            "trappist@maas-site-manager.example.com",
            "Trappist 1 e",
            True,
        )
        await create_user(
            "hatp13",
            "password3",
            "hatp13@example.com",
            "HAT-P-13 b",
        )
        await create_user(
            "alphacen",
            "password4",
            "alphacen@example.com",
            "Rigel Kentaurus",
        )

        response = await authenticated_admin_app_client.get(
            "/users", params=query_params
        )
        assert extract_users(response) == expected_result

    @pytest.mark.parametrize(
        "sort_by",
        [
            "id-asc",
            "username,username",
            "doesntexist",
        ],
    )
    async def test_users_get_with_invalid_params(
        self,
        authenticated_admin_app_client: AuthAsyncClient,
        fixture: Fixture,
        sort_by: str,
    ) -> None:
        await fixture.create(
            "user",
            [
                {
                    "email": "proxima@maas-site-manager.example.com",
                    "username": "proxima",
                    "full_name": "Proxima Centauri b",
                    "password": get_password_hash("password"),
                    "confirm_password": get_password_hash("password"),
                    "is_admin": False,
                }
            ],
            commit=True,
        )

        # not sortable
        response = await authenticated_admin_app_client.get(
            "/users", params={"sort_by": sort_by}
        )
        assert response.status_code == 400

    async def test_users_pagination(
        self, authenticated_admin_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        phash2 = "$2b$12$iEPLFcNocyeUDgu2ywDVGeFHyrksI89bzSvdAwvU1N4zYFtofme3S"
        users = await fixture.create(
            "user",
            {
                "email": "user@example.com",
                "username": "user",
                "full_name": "MAAS User",
                "password": phash2,
                "is_admin": False,
            },
            commit=True,
        )
        # the return data does not include passwords
        for user in users:
            user.pop("password")

        paginated = await authenticated_admin_app_client.get(
            "/users?page=2&size=1"
        )
        assert paginated.status_code == 200
        assert paginated.json() == {
            "page": 2,
            "size": 1,
            "total": 2,
            "items": users,
        }

    async def test_create_user(
        self, authenticated_admin_app_client: AuthAsyncClient
    ) -> None:
        user_details = {
            "full_name": "A MAAS User",
            "username": "newuser",
            "email": "newuser@example.com",
            "is_admin": False,
        }
        response = await authenticated_admin_app_client.post(
            "/users",
            json=user_details
            | {"password": "password", "confirm_password": "password"},
        )
        assert response.status_code == 200
        assert response.json() == user_details | {"id": 2}

    async def test_create_user_missing_fields(
        self, authenticated_admin_app_client: AuthAsyncClient
    ) -> None:
        response = await authenticated_admin_app_client.post(
            "/users",
            json={},
        )
        assert response.status_code == 422
        assert response.json()["detail"] == [
            {
                "loc": ["body", param],
                "msg": "field required",
                "type": "value_error.missing",
            }
            for param in [
                "full_name",
                "username",
                "email",
                "password",
                "confirm_password",
            ]
        ]

    async def test_create_user_password_unconfirmed(
        self, authenticated_admin_app_client: AuthAsyncClient
    ) -> None:
        user_details = {
            "full_name": "A MAAS User",
            "username": "newuser",
            "email": "user@example.com",
            "password": "password",
            "confirm_password": "",
        }
        response = await authenticated_admin_app_client.post(
            "/users",
            json=user_details,
        )
        assert response.status_code == 422
        assert response.json()

    async def test_create_user_email_taken(
        self, authenticated_admin_app_client: AuthAsyncClient
    ) -> None:
        user_details = {
            "full_name": "A New Admin",
            "username": "newAdmin",
            "email": "admin@example.com",
            "password": "password",
            "confirm_password": "password",
        }
        response = await authenticated_admin_app_client.post(
            "/users",
            json=user_details,
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Email or Username already in use."
        )

    async def test_create_user_username_taken(
        self, authenticated_admin_app_client: AuthAsyncClient
    ) -> None:
        user_details = {
            "full_name": "A New Admin",
            "username": "admin",
            "email": "newadmin@example.com",
            "password": "password",
            "confirm_password": "password",
        }
        response = await authenticated_admin_app_client.post(
            "/users",
            json=user_details,
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Email or Username already in use."
        )

    async def test_users_password_change(
        self, authenticated_user_app_client: AuthAsyncClient
    ) -> None:
        new_password = "new_admin_password"
        response = await authenticated_user_app_client.post(
            "/users/me/password",
            json={
                "current_password": "admin",
                "new_password": new_password,
                "confirm_password": new_password,
            },
        )
        assert response.status_code == 200

    async def test_users_password_too_short(
        self, authenticated_user_app_client: AuthAsyncClient
    ) -> None:
        short_pass = "new"
        response = await authenticated_user_app_client.post(
            "/users/me/password",
            json={
                "current_password": "admin",
                "new_password": short_pass,
                "confirm_password": short_pass,
            },
        )
        assert response.status_code == 422
        assert (
            response.json()["detail"][0]["msg"]
            == "ensure this value has at least 8 characters"
        )

    async def test_users_password_too_long(
        self, authenticated_user_app_client: AuthAsyncClient
    ) -> None:
        long_pass = "new" * 40

        response = await authenticated_user_app_client.post(
            "/users/me/password",
            json={
                "current_password": "admin",
                "new_password": long_pass,
                "confirm_password": long_pass,
            },
        )
        assert response.status_code == 422
        assert (
            response.json()["detail"][0]["msg"]
            == "ensure this value has at most 100 characters"
        )

    async def test_users_password_change_incorrect_pass(
        self,
        authenticated_user_app_client: AuthAsyncClient,
    ) -> None:
        new_password = "new_admin_password"
        response = await authenticated_user_app_client.post(
            "/users/me/password",
            json={
                "current_password": "wrong_password",
                "new_password": new_password,
                "confirm_password": new_password,
            },
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Incorrect password for user."
        )

    async def test_users_password_change_missing_parameters(
        self,
        authenticated_user_app_client: AuthAsyncClient,
    ) -> None:
        response = await authenticated_user_app_client.post(
            "/users/me/password",
            json={},
        )
        assert response.status_code == 422
        assert response.json()["detail"] == [
            {
                "loc": ["body", field],
                "msg": "field required",
                "type": "value_error.missing",
            }
            for field in [
                "current_password",
                "new_password",
                "confirm_password",
            ]
        ]

    async def test_users_patch_details(
        self, authenticated_admin_app_client: AuthAsyncClient
    ) -> None:
        old_details = {
            "id": 1,
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin",
            "password": "admin",
            "confirm_password": "",
            "is_admin": True,
        }
        new_details = random_sample_dict(
            {
                "username": "admin3",
                # "full_name": "New Admin",
                # "email": "admin3@example.com",
                # "password": "New Password",
                # "is_admin": True,
            },
            requires={"password": {"confirm_password": "New Password"}},
        )
        response = await authenticated_admin_app_client.patch(
            "/users/1", json=new_details
        )

        user_details = old_details | new_details
        user_details.pop("password")
        user_details.pop("confirm_password")
        assert response.status_code == 200
        assert response.json() == user_details

    async def test_users_patch_demote_admin(
        self, authenticated_admin_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        phash2 = "$2b$12$iEPLFcNocyeUDgu2ywDVGeFHyrksI89bzSvdAwvU1N4zYFtofme3S"
        user_details = {
            "email": "admin2@example.com",
            "username": "admin2",
            "full_name": "Another MAAS Admin",
            "password": phash2,
            "is_admin": True,
        }
        new_details = {"is_admin": False}
        await fixture.create(
            "user",
            [user_details],
            commit=True,
        )
        response = await authenticated_admin_app_client.patch(
            "/users/2", json=new_details
        )
        user_details |= new_details | {"id": 2}
        user_details.pop("password")
        assert response.status_code == 200
        assert response.json() == user_details

    async def test_users_patch_demote_self_admin(
        self, authenticated_admin_app_client: AuthAsyncClient
    ) -> None:
        response = await authenticated_admin_app_client.patch(
            "/users/1", json={"is_admin": False}
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]["message"]
            == "Admin users cannot demote themselves."
        )

    async def test_users_patch_missing_fields(
        self, authenticated_admin_app_client: AuthAsyncClient
    ) -> None:
        response = await authenticated_admin_app_client.patch(
            "/users/1", json={}
        )
        assert response.status_code == 422
        assert response.json()["detail"]["message"] == "Request body empty."

    async def test_users_patch_nonexistent_user(
        self, authenticated_admin_app_client: AuthAsyncClient
    ) -> None:
        response = await authenticated_admin_app_client.patch(
            "/users/10", json={"full_name": "ghost_in_the_test"}
        )
        assert response.status_code == 422
        assert response.json()["detail"]["message"] == "User does not exist."

    @pytest.mark.parametrize(
        "new_details",
        [{"email": "admin@example.com"}, {"username": "admin"}],
    )
    async def test_users_patch_duplicate_user(
        self,
        authenticated_admin_app_client: AuthAsyncClient,
        fixture: Fixture,
        new_details: dict[str, str],
    ) -> None:
        phash2 = "$2b$12$iEPLFcNocyeUDgu2ywDVGeFHyrksI89bzSvdAwvU1N4zYFtofme3S"
        user_details = {
            "email": "admin2@example.com",
            "username": "admin2",
            "full_name": "Another MAAS Admin",
            "password": phash2,
            "is_admin": True,
        }
        await fixture.create(
            "user",
            [user_details],
            commit=True,
        )
        response = await authenticated_admin_app_client.patch(
            "/users/2", json=new_details
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Email or Username already in use."
        )

    async def test_users_delete(
        self, authenticated_admin_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        phash2 = "$2b$12$iEPLFcNocyeUDgu2ywDVGeFHyrksI89bzSvdAwvU1N4zYFtofme3S"
        await fixture.create(
            "user",
            [
                {
                    "email": "user@example.com",
                    "username": "user",
                    "full_name": "MAAS User",
                    "is_admin": False,
                    "password": phash2,
                },
            ],
            commit=True,
        )

        response = await authenticated_admin_app_client.delete("/users/2")
        assert response.status_code == 204

        users_response = await authenticated_admin_app_client.get("/users")
        assert users_response.status_code == 200
        assert users_response.json() == {
            "items": [
                {
                    "id": 1,
                    "email": "admin@example.com",
                    "username": "admin",
                    "full_name": "Admin",
                    "is_admin": True,
                }
            ],
            "total": 1,
            "page": 1,
            "size": 20,
        }

    async def test_users_delete_self_fails(
        self, authenticated_admin_app_client: AuthAsyncClient, fixture: Fixture
    ) -> None:
        phash2 = "$2b$12$iEPLFcNocyeUDgu2ywDVGeFHyrksI89bzSvdAwvU1N4zYFtofme3S"
        await fixture.create(
            "user",
            [
                {
                    "email": "user@example.com",
                    "username": "user",
                    "full_name": "MAAS User",
                    "password": phash2,
                    "is_admin": False,
                },
            ],
            commit=True,
        )

        response = await authenticated_admin_app_client.delete("/users/1")
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Cannot delete the current user."
        )

    async def test_users_patch_me(
        self, authenticated_user_app_client: AuthAsyncClient
    ) -> None:
        old_details = {
            "id": 1,
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin",
            "is_admin": False,
        }
        new_details = random_sample_dict(
            {
                "username": "admin3",
                "full_name": "New Admin",
                "email": "admin3@example.com",
            },
        )
        response = await authenticated_user_app_client.patch(
            "/users/me", json=new_details
        )

        assert response.status_code == 200
        assert response.json() == old_details | new_details

    async def test_users_patch_me_missing_fields(
        self, authenticated_user_app_client: AuthAsyncClient
    ) -> None:
        response = await authenticated_user_app_client.patch(
            "/users/me", json={}
        )

        assert response.status_code == 422
        assert response.json()["detail"]["message"] == "Request body empty."

    @pytest.mark.parametrize(
        "new_details",
        [{"email": "admin2@example.com"}, {"username": "admin2"}],
    )
    async def test_users_patch_me_duplicate_user(
        self,
        authenticated_admin_app_client: AuthAsyncClient,
        fixture: Fixture,
        new_details: dict[str, str],
    ) -> None:
        phash2 = "$2b$12$iEPLFcNocyeUDgu2ywDVGeFHyrksI89bzSvdAwvU1N4zYFtofme3S"
        user_details = {
            "email": "admin2@example.com",
            "username": "admin2",
            "full_name": "Another MAAS Admin",
            "password": phash2,
            "is_admin": True,
        }
        await fixture.create(
            "user",
            [user_details],
            commit=True,
        )
        response = await authenticated_admin_app_client.patch(
            "/users/me", json=new_details
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Email or Username already in use."
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,url",
    [
        ("GET", "/requests"),
        ("POST", "/requests"),
        ("GET", "/sites"),
        ("GET", "/tokens"),
        ("POST", "/tokens"),
        ("GET", "/tokens/export"),
        ("GET", "/users"),
        ("POST", "/users"),
        ("GET", "/users/me"),
        ("PATCH", "/users/me"),
        ("POST", "/users/me/password"),
        ("PATCH", "/users/{id}"),
        ("DELETE", "/users/{id}"),
    ],
)
async def test_handler_auth_required(
    user_app_client: AsyncClient, method: str, url: str
) -> None:
    response = await user_app_client.request(method, url)
    assert (
        response.status_code == 401
    ), f"Auth should be required for {method} {url}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,url",
    [
        ("GET", "/users"),
        ("POST", "/users"),
        ("DELETE", "/users/{id}"),
        ("PATCH", "/users/{id}"),
    ],
)
async def test_handler_admin_required(
    authenticated_user_app_client: AuthAsyncClient, method: str, url: str
) -> None:
    response = await authenticated_user_app_client.request(method, url)
    assert (
        response.status_code == 403
    ), f"Admin should be required for {method} {url}"
