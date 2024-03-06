import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import Settings
from msm.service import _settings
from msm.service._settings import SettingsService
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestSettingsService:
    async def test_get(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        await factory.make_Setting(
            "service_url",
            value="https://sitemanager.example.com",
        )
        service = SettingsService(db_connection)
        settings = await service.get()
        assert settings == Settings(
            service_url="https://sitemanager.example.com"
        )

    async def test_get_no_extra_entries(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        await factory.make_Setting("some_setting", value=42)
        service = SettingsService(db_connection)
        settings = await service.get()
        assert settings == Settings()

    async def test_ensure_create_missing(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        service = SettingsService(db_connection)
        await service.ensure()
        settings = await factory.get("setting")
        assert {setting["name"] for setting in settings} == set(
            Settings.model_fields
        )

    async def test_ensure_sets_service_url(
        self,
        mocker: MockerFixture,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        mocker.patch.object(
            _settings, "gethostname"
        ).return_value = "sitemanager"
        service = SettingsService(db_connection)
        await service.ensure()
        settings = await factory.get("setting")
        assert settings == [
            {"name": "service_url", "value": "http://sitemanager:8000"}
        ]

    async def test_ensure_keep_existing(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        await factory.make_Setting(
            "service_url", value="http://sitemanager:8000"
        )
        service = SettingsService(db_connection)
        await service.ensure()
        settings = await factory.get("setting")
        assert settings == [
            {"name": "service_url", "value": "http://sitemanager:8000"}
        ]

    async def test_ensure_remove_extra(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        await factory.make_Setting("some_setting", value=42)
        await factory.make_Setting("another", value="test")
        service = SettingsService(db_connection)
        await service.ensure()
        settings = await factory.get("setting")
        assert {setting["name"] for setting in settings} == set(
            Settings.model_fields
        )
