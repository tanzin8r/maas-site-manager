from collections.abc import Iterator
from typing import (
    cast,
)

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.cmd import AsyncAction
from msm.cmd.sampledata import script
from msm.cmd.sampledata.fixtures import DeleteFixturesAction, FixturesAction
from tests.fixtures.factory import Factory


@pytest.fixture
def create_sampledata_action() -> Iterator[AsyncAction]:
    yield cast(AsyncAction, script._actions["create-fixtures"])


@pytest.fixture
def purge_sampledata_action() -> Iterator[AsyncAction]:
    yield cast(AsyncAction, script._actions["purge-fixtures"])


@pytest.mark.usefixtures("settings_environ", "db")
class TestSampleData:
    async def test_create_data(
        self,
        create_sampledata_action: FixturesAction,
        purge_sampledata_action: DeleteFixturesAction,
        db_connection: AsyncConnection,
        factory: Factory,
    ) -> None:
        # call private methods as db has already been migrated by test setup
        config = await create_sampledata_action._get_config(db_connection)

        await create_sampledata_action._make_fixtures(db_connection, config)
        site = await factory.get("site")
        assert len(site) == 9
        user = await factory.get("user")
        assert len(user) == 2
        token = await factory.get("token")
        assert len(token) == 10
        boot_source_selection = await factory.get("boot_source_selection")
        assert len(boot_source_selection) == 2
        boot_source = await factory.get("boot_source")
        assert len(boot_source) == 2
        boot_asset = await factory.get("boot_asset")
        assert len(boot_asset) == 2
        boot_asset_version = await factory.get("boot_asset_version")
        assert len(boot_asset_version) == 2
        boot_asset_item = await factory.get("boot_asset_item")
        assert len(boot_asset_item) == 2

        await purge_sampledata_action._delete_fixtures(db_connection)
        site = await factory.get("site")
        assert len(site) == 0
        user = await factory.get("user")
        assert len(user) == 0
        token = await factory.get("token")
        assert len(token) == 0
        boot_source_selection = await factory.get("boot_source_selection")
        assert len(boot_source_selection) == 0
        boot_source = await factory.get("boot_source")
        assert len(boot_source) == 0
        boot_asset = await factory.get("boot_asset")
        assert len(boot_asset) == 0
        boot_asset_version = await factory.get("boot_asset_version")
        assert len(boot_asset_version) == 0
        boot_asset_item = await factory.get("boot_asset_item")
        assert len(boot_asset_item) == 0
