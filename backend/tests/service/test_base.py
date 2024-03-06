from collections.abc import Iterator
from operator import itemgetter

from pydantic import BaseModel
import pytest
from sqlalchemy import (
    Column,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.tables import METADATA
from msm.service._base import DBBackedModelService
from tests.fixtures.factory import Factory

SampleTable = Table(
    "sample_table",
    METADATA,
    Column("name", Text, primary_key=True),
    Column("value", JSONB, nullable=False),
)


class SampleModel(BaseModel):
    key1: str = "default"
    key2: int = 42


class SampleService(DBBackedModelService[SampleModel]):
    db_table = SampleTable


@pytest.fixture
def service(db_connection: AsyncConnection) -> Iterator[SampleService]:
    yield SampleService(db_connection)


@pytest.mark.asyncio
class TestDBBackedModelService:
    async def test_ensure_insert_defaults(
        self, factory: Factory, service: SampleService
    ) -> None:
        await service.ensure()
        res = await factory.get("sample_table")
        assert sorted(res, key=itemgetter("name")) == [
            {"name": "key1", "value": "default"},
            {"name": "key2", "value": 42},
        ]

    async def test_ensure_defaults_only_missing_keys(
        self, factory: Factory, service: SampleService
    ) -> None:
        # add a value for a known key
        await factory.create(
            "sample_table",
            {"name": "key2", "value": 100},
        )
        await service.ensure()
        res = await factory.get("sample_table")
        assert sorted(res, key=itemgetter("name")) == [
            {"name": "key1", "value": "default"},
            {"name": "key2", "value": 100},
        ]

    async def test_ensure_only_known_keys(
        self, factory: Factory, service: SampleService
    ) -> None:
        # add an unknown key
        await factory.create(
            "sample_table",
            {"name": "otherkey", "value": "somevalue"},
        )
        await service.ensure()
        res = await factory.get("sample_table")
        assert sorted(res, key=itemgetter("name")) == [
            {"name": "key1", "value": "default"},
            {"name": "key2", "value": 42},
        ]

    async def test_get(self, factory: Factory, service: SampleService) -> None:
        await factory.create(
            "sample_table",
            [
                {"name": "key1", "value": "a value"},
                {"name": "key2", "value": 42},
            ],
        )
        instance = await service.get()
        assert instance.key1 == "a value"
        assert instance.key2 == 42

    async def test_update(
        self, factory: Factory, service: SampleService
    ) -> None:
        await factory.create(
            "sample_table",
            [
                {"name": "key1", "value": "a value"},
                {"name": "key2", "value": 42},
            ],
        )
        await service.update({"key2": 100})
        instance = await service.get()
        assert instance.key1 == "a value"
        assert instance.key2 == 100

    async def test_update_ignore_unknown_keys(
        self, service: SampleService
    ) -> None:
        await service.ensure()
        await service.update({"otherkey": 1.4})
        instance = await service.get()
        assert instance.key1 == "default"
        assert instance.key2 == 42
