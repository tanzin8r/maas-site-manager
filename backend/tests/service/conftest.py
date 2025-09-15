from collections.abc import AsyncIterator, Iterator

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.service import (
    BootAssetItemService,
    BootAssetService,
    BootAssetVersionService,
    BootSourceSelectionService,
    BootSourceService,
    IndexService,
    ServiceCollection,
)
from msm.service.s3 import S3Service


@pytest.fixture
async def service_collection(
    db_connection: AsyncConnection,
    s3_env: None,
) -> AsyncIterator[ServiceCollection]:
    yield ServiceCollection(db_connection)


@pytest.fixture(autouse=True)
async def index_service(
    service_collection: ServiceCollection,
) -> AsyncIterator[IndexService]:
    await service_collection.index_service.ensure()
    yield service_collection.index_service


@pytest.fixture
def boot_asset_service(
    service_collection: ServiceCollection,
) -> Iterator[BootAssetService]:
    yield service_collection.boot_assets


@pytest.fixture
def boot_source_selection_service(
    service_collection: ServiceCollection,
) -> Iterator[BootSourceSelectionService]:
    yield service_collection.boot_source_selections


@pytest.fixture
def boot_source_service(
    service_collection: ServiceCollection,
) -> Iterator[BootSourceService]:
    yield service_collection.boot_sources


@pytest.fixture
def boot_asset_version_service(
    service_collection: ServiceCollection,
) -> Iterator[BootAssetVersionService]:
    yield service_collection.boot_asset_versions


@pytest.fixture
def boot_asset_item_service(
    service_collection: ServiceCollection,
) -> Iterator[BootAssetItemService]:
    yield service_collection.boot_asset_items


@pytest.fixture
def s3_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
    monkeypatch.setenv("MSM_S3_ENDPOINT", "http://test-endpoint.com")
    monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
    monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("MSM_S3_PATH", "test/path")


@pytest.fixture
def s3_service(
    service_collection: ServiceCollection,
) -> Iterator[S3Service]:
    yield service_collection.s3
