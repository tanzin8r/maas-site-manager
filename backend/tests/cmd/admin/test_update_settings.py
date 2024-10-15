from argparse import Namespace
from collections.abc import Iterator
from typing import (
    Any,
    cast,
)

import pytest

from msm.cmd import AsyncAction
from msm.cmd.admin import script
from tests.fixtures.factory import Factory


@pytest.fixture
def update_settings_action() -> Iterator[AsyncAction]:
    yield cast(AsyncAction, script._actions["update-settings"])


@pytest.mark.usefixtures("settings_environ", "db")
class CreateUpdateSettingsAction:

    @pytest.mark.parametrize(
        "setting,value",
        [
            ("service_url", "http://example:8080/"),
            ("token_lifetime_minutes", 300),
            ("token_rotation_interval_minutes", 200),
        ],
    )
    async def test_update_settings(
        self, factory: Factory, update_settings_action: AsyncAction, setting: str, value: Any,
    ) -> None:
        await update_settings_action.aexecute(
            Namespace(**{setting: value})
        )
        raw_settings = await factory.get("setting")
        settings = {setting["name"]: setting["value"] for setting in raw_settings}
        assert settings[setting] == value