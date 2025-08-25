from collections.abc import Iterator
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import models
from msm.db.models import (
    BootAsset,
    BootAssetItem,
    BootAssetVersion,
    BootSource,
    BootSourceSelection,
)
from msm.service import ServiceCollection
from tests.fixtures.factory import Factory


@pytest.fixture
def collection(db_connection: AsyncConnection) -> Iterator[ServiceCollection]:
    yield ServiceCollection(db_connection)


@pytest.fixture
async def single_item(
    factory: Factory, ver_ubuntu_noble_1: BootAssetVersion
) -> BootAssetItem:
    return await factory.make_BootAssetItem(
        ver_ubuntu_noble_1.id, ftype=models.ItemFileType.ARCHIVE_TAR_XZ
    )


@pytest.fixture
async def multi_item(
    factory: Factory, ver_ubuntu_noble_1: BootAssetVersion
) -> list[BootAssetItem]:
    return [
        await factory.make_BootAssetItem(
            ver_ubuntu_noble_1.id, ftype=models.ItemFileType.ARCHIVE_TAR_XZ
        ),
        await factory.make_BootAssetItem(
            ver_ubuntu_noble_1.id, ftype=models.ItemFileType.BOOT_DTB
        ),
    ]


@pytest.fixture
async def multi_version(
    factory: Factory,
    ver_ubuntu_noble_1: BootAssetVersion,
    ver_ubuntu_noble_2: BootAssetVersion,
) -> list[BootAssetItem]:
    return [
        await factory.make_BootAssetItem(
            ver_ubuntu_noble_1.id, ftype=models.ItemFileType.ARCHIVE_TAR_XZ
        ),
        await factory.make_BootAssetItem(
            ver_ubuntu_noble_2.id, ftype=models.ItemFileType.BOOT_DTB
        ),
    ]


@pytest.mark.asyncio
class TestServiceCollection:
    async def test_delete_item_and_purge(
        self,
        factory: Factory,
        collection: ServiceCollection,
        single_item: BootAssetItem,
    ) -> None:
        await collection.delete_item_and_purge(single_item.id)
        versions = await factory.get("boot_asset_version")
        assets = await factory.get("boot_asset")
        assert versions == []
        assert assets == []

    async def test_delete_item_and_purge_multi_item(
        self,
        factory: Factory,
        collection: ServiceCollection,
        multi_item: list[BootAssetItem],
    ) -> None:
        await collection.delete_item_and_purge(multi_item[1].id)
        versions = await factory.get("boot_asset_version")
        assert len(versions) == 1
        assets = await factory.get("boot_asset")
        assert len(assets) == 1

    async def test_delete_item_and_purge_multi_version(
        self,
        factory: Factory,
        collection: ServiceCollection,
        ver_ubuntu_noble_1: BootAssetVersion,
        multi_version: list[BootAssetItem],
    ) -> None:
        await collection.delete_item_and_purge(multi_version[1].id)
        versions = await factory.get("boot_asset_version")
        assert versions == [
            {
                "id": ver_ubuntu_noble_1.id,
                "version": ver_ubuntu_noble_1.version,
                "boot_asset_id": multi_version[0].id,
                "last_seen": factory.now,
            }
        ]
        assets = await factory.get("boot_asset")
        assert len(assets) == 1

    async def test_purge_source(
        self,
        factory: Factory,
        collection: ServiceCollection,
        boot_source_custom: BootSource,
        boot_source: BootSource,
        sel_ubuntu_noble: BootSourceSelection,
        single_item: BootAssetItem,
    ) -> None:
        await collection.purge_source(boot_source.id)
        sources = await factory.get("boot_source")
        assets = await factory.get("boot_asset")
        versions = await factory.get("boot_asset_version")
        items = await factory.get("boot_asset_item")
        selections = await factory.get("boot_source_selection")
        assert sources[0]["id"] == boot_source_custom.id
        assert assets == []
        assert versions == []
        assert items == []
        assert selections == []

    async def test_purge_assets(
        self,
        ubuntu_noble: BootAsset,
        ubuntu_jammy: BootAsset,
        items_ubuntu_noble_1: list[BootAssetItem],
        items_ubuntu_noble_2: list[BootAssetItem],
        items_ubuntu_jammy_1: list[BootAssetItem],
        collection: ServiceCollection,
        factory: Factory,
        mocker: MockerFixture,
    ) -> None:
        mock_delete = MagicMock()
        mock_client = mocker.patch("msm.service.boto3.client")
        mock_client.return_value = mock_delete
        mock_refresh = mocker.patch.object(collection.index_service, "refresh")
        await collection.purge_assets(
            [ubuntu_noble.id, ubuntu_jammy.id],
            "test-s3-ep",
            "test-bucket",
            "test/path",
            "test-key",
            "test-secret-key",
        )
        mock_client.assert_called_once_with(
            "s3",
            use_ssl=False,
            verify=False,
            endpoint_url="test-s3-ep",
            aws_access_key_id="test-key",
            aws_secret_access_key="test-secret-key",
        )
        for item in items_ubuntu_noble_1:
            assert (
                call(Bucket="test-bucket", Key="test/path/" + str(item.id))
                in mock_delete.delete_object.call_args_list
            )
        for item in items_ubuntu_noble_2:
            assert (
                call(Bucket="test-bucket", Key="test/path/" + str(item.id))
                in mock_delete.delete_object.call_args_list
            )
        for item in items_ubuntu_jammy_1:
            assert (
                call(Bucket="test-bucket", Key="test/path/" + str(item.id))
                in mock_delete.delete_object.call_args_list
            )
        mock_refresh.assert_called_once()
        items = await factory.get("boot_asset_item")
        versions = await factory.get("boot_asset_version")
        assets = await factory.get("boot_asset")
        assert len(items) == 0
        assert len(versions) == 0
        assert len(assets) == 0
