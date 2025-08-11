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
)


@pytest.fixture(autouse=True)
async def index_service(
    db_connection: AsyncConnection,
) -> AsyncIterator[IndexService]:
    srv = IndexService(db_connection)
    await srv.create()
    yield srv


@pytest.fixture
def boot_asset_service(
    db_connection: AsyncConnection,
) -> Iterator[BootAssetService]:
    yield BootAssetService(db_connection)


@pytest.fixture
def boot_source_selection_service(
    db_connection: AsyncConnection,
) -> Iterator[BootSourceSelectionService]:
    yield BootSourceSelectionService(db_connection)


@pytest.fixture
def boot_source_service(
    db_connection: AsyncConnection,
) -> Iterator[BootSourceService]:
    yield BootSourceService(db_connection)


@pytest.fixture
def boot_asset_version_service(
    db_connection: AsyncConnection,
) -> Iterator[BootAssetVersionService]:
    yield BootAssetVersionService(db_connection)


@pytest.fixture
def boot_asset_item_service(
    db_connection: AsyncConnection,
) -> Iterator[BootAssetItemService]:
    yield BootAssetItemService(db_connection)
