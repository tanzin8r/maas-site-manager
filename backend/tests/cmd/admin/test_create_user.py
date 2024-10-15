from argparse import Namespace
from collections.abc import Iterator
from typing import (
    cast,
)

import pytest

from msm.cmd import AsyncAction
from msm.cmd.admin import script
from msm.password import verify_password
from tests.fixtures.factory import Factory


@pytest.fixture
def create_user_action() -> Iterator[AsyncAction]:
    yield cast(AsyncAction, script._actions["create-user"])


@pytest.mark.usefixtures("settings_environ", "db")
class TestCreateUserAction:
    async def test_create_user(
        self, factory: Factory, create_user_action: AsyncAction
    ) -> None:
        await create_user_action.aexecute(
            Namespace(
                username="admin",
                email="admin@example.net",
                full_name="An Administrator",
                password="secret",
                admin=True,
            )
        )
        [user] = await factory.get("user")
        assert user["username"] == "admin"
        assert user["email"] == "admin@example.net"
        assert user["full_name"] == "An Administrator"
        assert user["is_admin"]
        assert verify_password("secret", user["password"])

    @pytest.mark.parametrize(
        "attr,value",
        [
            ("username", "admin"),
            ("email", "admin@example.net"),
        ],
    )
    async def test_create_user_exists(
        self,
        capsys: pytest.CaptureFixture[str],
        factory: Factory,
        create_user_action: AsyncAction,
        attr: str,
        value: str,
    ) -> None:
        await factory.make_User(**{attr: value})  # type: ignore[arg-type]
        await factory.conn.commit()
        with pytest.raises(SystemExit) as error:
            await create_user_action.aexecute(
                Namespace(
                    username="admin",
                    email="admin@example.net",
                    full_name="An Administrator",
                    password="secret",
                    admin=True,
                )
            )
        assert error.value.code == 1
        _, err = capsys.readouterr()
        assert err == "User with specified username/email already exists.\n"
