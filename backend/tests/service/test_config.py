import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import Config
from msm.service._config import ConfigService

from ..fixtures.factory import Factory


@pytest.mark.asyncio
class TestConfigService:
    async def test_get(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        await factory.make_Config("token_secret_key", value="secret")
        service = ConfigService(db_connection)
        config = await service.get()
        assert config == Config(token_secret_key="secret")

    async def test_get_no_extra_entries(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        await factory.make_Config("some_config", value=42)
        service = ConfigService(db_connection)
        config = await service.get()
        assert config == Config()

    async def test_ensure_create_missing(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        service = ConfigService(db_connection)
        await service.ensure()
        configs = await factory.get("config")
        assert {config["name"] for config in configs} == set(
            Config.model_fields
        )

    async def test_ensure_keep_existing(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        await factory.make_Config("token_secret_key", value="secret")
        service = ConfigService(db_connection)
        await service.ensure()
        configs = await factory.get("config")
        assert configs == [{"name": "token_secret_key", "value": "secret"}]

    async def test_ensure_remove_extra(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        await factory.make_Config("some_config", value=42)
        await factory.make_Config("another", value="test")
        service = ConfigService(db_connection)
        await service.ensure()
        configs = await factory.get("config")
        assert {config["name"] for config in configs} == set(
            Config.model_fields
        )
