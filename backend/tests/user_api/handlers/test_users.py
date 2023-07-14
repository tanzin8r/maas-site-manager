import random
from typing import Any

from httpx import Response
import pytest

from msm.user_api._auth import get_password_hash

from ...fixtures.client import Client
from ...fixtures.db import Fixture


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
class TestUsersGetHandler:
    async def test_get(self, app_client: Client, fixture: Fixture) -> None:
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
        )
        # the return data does not include passwords
        for user in users:
            user.pop("password")

        response = await app_client.post(
            "/login",
            json={"email": "admin@example.com", "password": "admin"},
        )
        assert response.status_code == 200

        user_list = await app_client.get(
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
    async def test_with_params(
        self,
        admin_client: Client,
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

        response = await admin_client.get("/users", params=query_params)
        assert extract_users(response) == expected_result

    @pytest.mark.parametrize(
        "sort_by",
        [
            "id-asc",
            "username,username",
            "doesntexist",
        ],
    )
    async def test_with_invalid_params(
        self,
        admin_client: Client,
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
        )

        # not sortable
        response = await admin_client.get(
            "/users", params={"sort_by": sort_by}
        )
        assert response.status_code == 400

    async def test_pagination(
        self, admin_client: Client, fixture: Fixture
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
        )
        # the return data does not include passwords
        for user in users:
            user.pop("password")

        paginated = await admin_client.get("/users?page=2&size=1")
        assert paginated.status_code == 200
        assert paginated.json() == {
            "page": 2,
            "size": 1,
            "total": 2,
            "items": users,
        }

    async def test_get_by_id(
        self, admin_client: Client, fixture: Fixture
    ) -> None:
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

        user_id = -1
        response = await admin_client.get(f"/users/{user_id}")
        assert response.status_code == 404
        assert response.json()["detail"]["message"] == "User does not exist."

        user_id = 2
        response = await admin_client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json() == {
            "id": 2,
            "full_name": "Proxima Centauri b",
            "username": "proxima",
            "email": "proxima@maas-site-manager.example.com",
            "is_admin": False,
        }


@pytest.mark.asyncio
class TestUsersPostHandler:
    async def test_post(self, admin_client: Client) -> None:
        user_details = {
            "full_name": "A MAAS User",
            "username": "newuser",
            "email": "newuser@example.com",
            "is_admin": False,
        }
        response = await admin_client.post(
            "/users",
            json=user_details
            | {"password": "password", "confirm_password": "password"},
        )
        assert response.status_code == 200
        assert response.json() == user_details | {"id": 2}

    async def test_missing_fields(self, admin_client: Client) -> None:
        response = await admin_client.post(
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

    async def test_password_unconfirmed(self, admin_client: Client) -> None:
        user_details = {
            "full_name": "A MAAS User",
            "username": "newuser",
            "email": "user@example.com",
            "password": "password",
            "confirm_password": "",
        }
        response = await admin_client.post(
            "/users",
            json=user_details,
        )
        assert response.status_code == 422
        assert response.json()

    async def test_email_taken(self, admin_client: Client) -> None:
        user_details = {
            "full_name": "A New Admin",
            "username": "newAdmin",
            "email": "admin@example.com",
            "password": "password",
            "confirm_password": "password",
        }
        response = await admin_client.post(
            "/users",
            json=user_details,
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Email or Username already in use."
        )

    async def test_username_taken(self, admin_client: Client) -> None:
        user_details = {
            "full_name": "A New Admin",
            "username": "admin",
            "email": "newadmin@example.com",
            "password": "password",
            "confirm_password": "password",
        }
        response = await admin_client.post(
            "/users",
            json=user_details,
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Email or Username already in use."
        )


@pytest.mark.asyncio
class TestUsersMePasswordPostHandler:
    async def test_password_change(self, user_client: Client) -> None:
        new_password = "new_admin_password"
        response = await user_client.post(
            "/users/me/password",
            json={
                "current_password": "admin",
                "new_password": new_password,
                "confirm_password": new_password,
            },
        )
        assert response.status_code == 200

    async def test_password_too_short(self, user_client: Client) -> None:
        short_pass = "new"
        response = await user_client.post(
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

    async def test_password_too_long(self, user_client: Client) -> None:
        long_pass = "new" * 40

        response = await user_client.post(
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

    async def test_password_change_incorrect_pass(
        self,
        user_client: Client,
    ) -> None:
        new_password = "new_admin_password"
        response = await user_client.post(
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

    async def test_password_change_missing_parameters(
        self,
        user_client: Client,
    ) -> None:
        response = await user_client.post(
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


@pytest.mark.asyncio
class TestUsersPatchHandler:
    async def test_patch(self, admin_client: Client) -> None:
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
            },
            requires={"password": {"confirm_password": "New Password"}},
        )
        response = await admin_client.patch("/users/1", json=new_details)

        user_details = old_details | new_details
        user_details.pop("password")
        user_details.pop("confirm_password")
        assert response.status_code == 200
        assert response.json() == user_details

    async def test_demote_admin(
        self, admin_client: Client, fixture: Fixture
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
        await fixture.create("user", [user_details])
        response = await admin_client.patch("/users/2", json=new_details)
        user_details |= new_details | {"id": 2}
        user_details.pop("password")
        assert response.status_code == 200
        assert response.json() == user_details

    async def test_demote_self_admin(self, admin_client: Client) -> None:
        response = await admin_client.patch(
            "/users/1", json={"is_admin": False}
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]["message"]
            == "Admin users cannot demote themselves."
        )

    async def test_missing_fields(self, admin_client: Client) -> None:
        response = await admin_client.patch("/users/1", json={})
        assert response.status_code == 422
        assert response.json()["detail"]["message"] == "Request body empty."

    async def test_nonexistent_user(self, admin_client: Client) -> None:
        response = await admin_client.patch(
            "/users/10", json={"full_name": "ghost_in_the_test"}
        )
        assert response.status_code == 404
        assert response.json()["detail"]["message"] == "User does not exist."

    @pytest.mark.parametrize(
        "new_details",
        [{"email": "admin@example.com"}, {"username": "admin"}],
    )
    async def test_duplicate_user(
        self,
        admin_client: Client,
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
        await fixture.create("user", [user_details])

        response = await admin_client.patch("/users/2", json=new_details)
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Email or Username already in use."
        )


@pytest.mark.asyncio
class TestUsersDeleteHandler:
    async def test_delete(
        self, admin_client: Client, fixture: Fixture
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
        )

        response = await admin_client.delete("/users/2")
        assert response.status_code == 204

        users_response = await admin_client.get("/users")
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

    async def test_delete_self_fails(
        self, admin_client: Client, fixture: Fixture
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
        )

        response = await admin_client.delete("/users/1")
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Cannot delete the current user."
        )


@pytest.mark.asyncio
class TestUsersMePatchHandler:
    async def test_patch(self, user_client: Client) -> None:
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
        response = await user_client.patch("/users/me", json=new_details)

        assert response.status_code == 200
        assert response.json() == old_details | new_details

    async def test_missing_fields(self, user_client: Client) -> None:
        response = await user_client.patch("/users/me", json={})

        assert response.status_code == 422
        assert response.json()["detail"]["message"] == "Request body empty."

    @pytest.mark.parametrize(
        "new_details",
        [{"email": "admin2@example.com"}, {"username": "admin2"}],
    )
    async def test_duplicate_user(
        self,
        admin_client: Client,
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
        await fixture.create("user", [user_details])
        response = await admin_client.patch("/users/me", json=new_details)
        assert response.status_code == 400
        assert (
            response.json()["detail"]["message"]
            == "Email or Username already in use."
        )
