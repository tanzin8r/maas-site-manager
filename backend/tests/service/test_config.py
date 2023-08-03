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
