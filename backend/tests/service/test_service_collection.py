import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import models
from msm.service import ServiceCollection
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestServiceCollection:
    async def test_delete_item_and_purge(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        source = await factory.make_BootSource()
        asset = await factory.make_BootAsset(source.id)
        ver = await factory.make_BootAssetVersion(asset.id)
        item = await factory.make_BootAssetItem(
            ver.id, ftype=models.ItemFileType.ARCHIVE_TAR_XZ
        )
        collection = ServiceCollection(db_connection)
        await collection.delete_item_and_purge(item.id)
        versions = await factory.get("boot_asset_version")
        assets = await factory.get("boot_asset")
        assert versions == []
        assert assets == []

    async def test_delete_item_and_purge_multi_item(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        source = await factory.make_BootSource()
        asset = await factory.make_BootAsset(source.id)
        ver = await factory.make_BootAssetVersion(asset.id)
        await factory.make_BootAssetItem(
            ver.id, ftype=models.ItemFileType.ARCHIVE_TAR_XZ
        )
        item2 = await factory.make_BootAssetItem(
            ver.id, ftype=models.ItemFileType.BOOT_DTB
        )
        collection = ServiceCollection(db_connection)
        await collection.delete_item_and_purge(item2.id)
        versions = await factory.get("boot_asset_version")
        assert len(versions) == 1
        assets = await factory.get("boot_asset")
        assert len(assets) == 1

    async def test_delete_item_and_purge_multi_version(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        source = await factory.make_BootSource()
        asset = await factory.make_BootAsset(source.id)
        ver1 = await factory.make_BootAssetVersion(asset.id, version="1")
        ver2 = await factory.make_BootAssetVersion(asset.id, version="2")
        await factory.make_BootAssetItem(
            ver1.id, ftype=models.ItemFileType.ARCHIVE_TAR_XZ
        )
        item2 = await factory.make_BootAssetItem(
            ver2.id, ftype=models.ItemFileType.BOOT_DTB
        )
        collection = ServiceCollection(db_connection)
        await collection.delete_item_and_purge(item2.id)
        versions = await factory.get("boot_asset_version")
        assert versions == [
            {"id": ver1.id, "version": ver1.version, "boot_asset_id": asset.id}
        ]
        assets = await factory.get("boot_asset")
        assert len(assets) == 1

    async def test_purge_source(
        self, factory: Factory, db_connection: AsyncConnection
    ) -> None:
        source = await factory.make_BootSource()
        asset = await factory.make_BootAsset(source.id)
        version = await factory.make_BootAssetVersion(asset.id)
        await factory.make_BootAssetItem(version.id)
        await factory.make_BootSourceSelection(source.id)
        collection = ServiceCollection(db_connection)
        await collection.purge_source(source.id)
        sources = await factory.get("boot_source")
        assets = await factory.get("boot_asset")
        versions = await factory.get("boot_asset_version")
        items = await factory.get("boot_asset_item")
        selections = await factory.get("boot_source_selection")
        assert sources == []
        assert assets == []
        assert versions == []
        assert items == []
        assert selections == []
