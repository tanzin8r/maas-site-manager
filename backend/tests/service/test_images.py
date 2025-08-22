from datetime import datetime, timedelta
import json

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import (
    BootAsset,
    BootAssetCreate,
    BootAssetItem,
    BootAssetItemCreate,
    BootAssetItemUpdate,
    BootAssetKind,
    BootAssetLabel,
    BootAssetUpdate,
    BootAssetVersion,
    BootAssetVersionCreate,
    BootSource,
    BootSourceCreate,
    BootSourceSelection,
    BootSourceSelectionCreate,
    BootSourceSelectionUpdate,
    BootSourceUpdate,
    IndexType,
    ItemFileType,
)
from msm.service import (
    BootAssetItemService,
    BootAssetService,
    BootAssetVersionService,
    BootSourceSelectionService,
    BootSourceService,
    IndexNotFound,
    IndexService,
)
from msm.time import now_utc
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestBootAssetService:
    async def test_get(
        self,
        boot_asset_service: BootAssetService,
        ubuntu_noble: BootAsset,
    ) -> None:
        count, [rba] = await boot_asset_service.get([])
        assert count == 1
        assert ubuntu_noble == rba

    @pytest.mark.parametrize(
        "filter_param",
        [
            ("boot_source_id"),
            ("kind"),
            ("label"),
            ("os"),
            ("arch"),
            ("release"),
        ],
    )
    async def test_get_with_filters(
        self,
        boot_asset_service: BootAssetService,
        ubuntu_noble: BootAsset,
        filter_param: str,
    ) -> None:
        filters = {filter_param: [ubuntu_noble.model_dump()[filter_param]]}
        count, [rba] = await boot_asset_service.get(
            sort_params=[], offset=0, limit=None, **filters
        )
        assert count == 1
        assert rba == ubuntu_noble

    @pytest.mark.parametrize(
        "id,exists",
        [
            (1, True),
            (-1, False),
        ],
    )
    async def test_get_by_id(
        self,
        boot_asset_service: BootAssetService,
        ubuntu_noble: BootAsset,
        id: int,
        exists: bool,
    ) -> None:
        assert await boot_asset_service.get_by_id(id) == (
            ubuntu_noble if exists else None
        )

    async def test_create(
        self,
        factory: Factory,
        boot_source: BootSource,
        boot_asset_service: BootAssetService,
    ) -> None:
        new_boot_asset = BootAssetCreate(
            boot_source_id=boot_source.id,
            kind=BootAssetKind.BOOTLOADER,
            label=BootAssetLabel.CANDIDATE,
            os="test OS",
            release="test release",
            codename="test codename",
            title="test title",
            arch="test arch",
            subarch="test subarch",
            compatibility=["test", "compatibility"],
            flavor="test flavor",
            base_image="test base image",
            bootloader_type="test bootloader type",
            eol=now_utc() + timedelta(days=3650),
            esm_eol=now_utc() + timedelta(days=5000),
            signed=True,
        )
        boot_asset = await boot_asset_service.create(new_boot_asset)
        expected_boot_asset = BootAsset(
            id=boot_asset.id, **new_boot_asset.model_dump()
        )
        assert boot_asset == expected_boot_asset
        assets = await factory.get("boot_asset")
        assert len(assets) == 1
        assert assets[0] == expected_boot_asset.model_dump()

    async def test_delete(
        self,
        factory: Factory,
        boot_asset_service: BootAssetService,
        ubuntu_noble: BootAsset,
    ) -> None:
        await boot_asset_service.delete(ubuntu_noble.id)
        assets = await factory.get("boot_asset")
        assert len(assets) == 0

    async def test_update(
        self,
        factory: Factory,
        boot_asset_service: BootAssetService,
        ubuntu_noble: BootAsset,
    ) -> None:
        asset_updates = BootAssetUpdate(
            kind=BootAssetKind.OS,
            label=BootAssetLabel.STABLE,
            os="ubuntu",
            release="noble",
            codename="Numbat",
            title="new title",
            arch="amd64",
            subarch="subarch",
            compatibility=["test"],
            flavor="flavor",
            base_image="ubuntu/noble",
            bootloader_type="pxe",
            eol=now_utc(),
            esm_eol=now_utc(),
            signed=False,
        )

        await boot_asset_service.update(ubuntu_noble.id, asset_updates)
        assets = await factory.get("boot_asset")
        assert len(assets) == 1
        assert assets[0] == asset_updates.model_dump() | {
            "id": ubuntu_noble.id,
            "boot_source_id": ubuntu_noble.boot_source_id,
        }

    async def test_delete_by_source_id(
        self,
        factory: Factory,
        boot_asset_service: BootAssetService,
        boot_source: BootSource,
        ubuntu_noble: BootAsset,
    ) -> None:
        await boot_asset_service.delete_by_source_id(boot_source.id)
        assets = await factory.get("boot_asset")
        assert len(assets) == 0

    async def test_get_many_by_id(
        self,
        boot_asset_service: BootAssetService,
        ubuntu_noble: BootAsset,
        ubuntu_jammy: BootAsset,
        centos: BootAsset,
    ) -> None:
        _, assets = await boot_asset_service.get_many_by_id(
            [ubuntu_noble.id, ubuntu_jammy.id]
        )
        assert ubuntu_noble in assets
        assert ubuntu_jammy in assets
        assert centos not in assets

    async def test_get_many_by_id_with_filters(
        self,
        boot_asset_service: BootAssetService,
        ubuntu_noble: BootAsset,
        grub: BootAsset,
    ) -> None:
        count, assets = await boot_asset_service.get_many_by_id(
            [ubuntu_noble.id, grub.id], kind=[BootAssetKind.OS]
        )
        assert count == 1
        assert next(iter(assets)) == ubuntu_noble
        count, assets = await boot_asset_service.get_many_by_id(
            [ubuntu_noble.id, grub.id], kind=[BootAssetKind.BOOTLOADER]
        )
        assert count == 1
        assert next(iter(assets)) == grub


@pytest.mark.asyncio
class TestBootSourceSelectionService:
    async def test_get(
        self,
        boot_source_selection_service: BootSourceSelectionService,
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        (
            count,
            [sel1, sel2],
        ) = await boot_source_selection_service.get(
            [],
            boot_source_id=[sel_ubuntu_noble[0].boot_source_id],
        )
        assert count == 2
        assert sel_ubuntu_noble[0] == sel1
        assert sel_ubuntu_noble[1] == sel2

    @pytest.mark.parametrize(
        "filter_param",
        [
            ("boot_source_id"),
            ("os"),
            ("arch"),
            ("release"),
        ],
    )
    async def test_get_with_filters(
        self,
        boot_source_selection_service: BootSourceSelectionService,
        ubuntu_noble: BootAsset,
        centos: BootAsset,
        factory: Factory,
        filter_param: str,
    ) -> None:
        noble_sel = await factory.make_BootSourceSelection(
            ubuntu_noble.boot_source_id,
            os="ubuntu",
            release="noble",
            arch="amd64",
        )
        await factory.make_BootSourceSelection(
            centos.boot_source_id,
            os="centos",
            release="centos70",
            arch="arm64",
        )
        filters = {filter_param: [ubuntu_noble.model_dump()[filter_param]]}
        count, [sel] = await boot_source_selection_service.get(
            [],
            0,
            None,
            **filters,
        )
        assert count == 1
        assert sel == noble_sel

    async def test_create(
        self,
        factory: Factory,
        boot_source_selection_service: BootSourceSelectionService,
        boot_source: BootSource,
    ) -> None:
        new_boot_src_selection = BootSourceSelectionCreate(
            boot_source_id=boot_source.id,
            label=BootAssetLabel.CANDIDATE,
            os="test os",
            release="test release",
            arch="testarch",
            selected=True,
        )
        boot_src_selection = await boot_source_selection_service.create(
            new_boot_src_selection
        )
        expected_boot_src_selection = BootSourceSelection(
            id=boot_src_selection.id,
            **new_boot_src_selection.model_dump(),
        )
        selections = await factory.get("boot_source_selection")
        assert len(selections) == 1
        assert selections[0] == expected_boot_src_selection.model_dump()

    async def test_update(
        self,
        factory: Factory,
        boot_source_selection_service: BootSourceSelectionService,
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        new_boot_src_selection = BootSourceSelectionUpdate(
            label=BootAssetLabel.STABLE,
            os="new os",
        )
        await boot_source_selection_service.update(
            sel_ubuntu_noble[0].boot_source_id,
            sel_ubuntu_noble[0].id,
            new_boot_src_selection,
        )
        selections = await factory.get("boot_source_selection")
        assert len(selections) == 2
        assert selections[0]["os"] == "new os"

    async def test_delete(
        self,
        factory: Factory,
        boot_source_selection_service: BootSourceSelectionService,
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        await boot_source_selection_service.delete(
            sel_ubuntu_noble[0].boot_source_id, sel_ubuntu_noble[0].id
        )
        selections = await factory.get("boot_source_selection")
        assert len(selections) == 1
        assert selections[0] == sel_ubuntu_noble[1].model_dump()

    async def test_delete_by_source_id(
        self,
        factory: Factory,
        boot_source_selection_service: BootSourceSelectionService,
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        await boot_source_selection_service.delete_by_source_id(
            sel_ubuntu_noble[0].boot_source_id
        )
        selections = await factory.get("boot_source_selection")
        assert len(selections) == 0


@pytest.mark.asyncio
class TestBootSourceService:
    async def test_get(
        self,
        boot_source_service: BootSourceService,
        boot_source_custom: BootSource,
    ) -> None:
        count, [rbs] = await boot_source_service.get([])
        assert count == 1
        assert rbs == boot_source_custom

    @pytest.mark.parametrize(
        "id,exists",
        [
            (1, True),
            (-1, False),
        ],
    )
    async def test_get_by_id(
        self,
        boot_source_service: BootSourceService,
        boot_source_custom: BootSource,
        id: int,
        exists: bool,
    ) -> None:
        assert await boot_source_service.get_by_id(id) == (
            boot_source_custom if exists else None
        )

    async def test_create(
        self,
        factory: Factory,
        boot_source_service: BootSourceService,
        boot_source_custom: BootSource,
    ) -> None:
        new_boot_source = BootSourceCreate(
            priority=1,
            url="http://some.image.server",
            keyring="test keyring",
            sync_interval=3600,
            name="Test Boot Source",
            last_sync=factory.now,
        )
        boot_source = await boot_source_service.create(new_boot_source)
        expected_boot_source = BootSource(
            id=boot_source.id, **new_boot_source.model_dump()
        )
        sources = await factory.get("boot_source")
        assert len(sources) == 2
        assert sources[1] == expected_boot_source.model_dump()

    async def test_update(
        self,
        factory: Factory,
        boot_source_service: BootSourceService,
        boot_source: BootSource,
    ) -> None:
        new_boot_source = BootSourceUpdate(
            priority=2,
            url="http://another.image.server",
            name="Another Boot Source",
        )
        await boot_source_service.update(boot_source.id, new_boot_source)
        sources = await factory.get("boot_source")
        assert len(sources) == 2
        assert sources[1]["url"] == new_boot_source.url

    async def test_delete(
        self,
        factory: Factory,
        boot_source_service: BootSourceService,
        boot_source: BootSource,
    ) -> None:
        await boot_source_service.delete(boot_source.id)
        sources = await factory.get("boot_source")
        assert len(sources) == 1


class TestBootAssetVersionService:
    async def test_get(
        self,
        factory: Factory,
        boot_asset_version_service: BootAssetVersionService,
        ver_ubuntu_jammy_1: BootAssetVersion,
    ) -> None:
        count, [rbav] = await boot_asset_version_service.get([])
        assert count == 1
        assert rbav == ver_ubuntu_jammy_1

    async def test_get_latest_version(
        self,
        factory: Factory,
        boot_asset_version_service: BootAssetVersionService,
        ver_ubuntu_noble_1: BootAssetVersion,
        ver_ubuntu_noble_2: BootAssetVersion,
    ) -> None:
        version = await boot_asset_version_service.get_latest_version(
            ver_ubuntu_noble_1.boot_asset_id
        )
        assert version is not None
        assert version == ver_ubuntu_noble_2

    @pytest.mark.parametrize(
        "filter_param",
        [("boot_asset_id"), ("version")],
    )
    async def test_get_with_filters(
        self,
        factory: Factory,
        boot_asset_version_service: BootAssetVersionService,
        ver_ubuntu_jammy_1: BootAssetVersion,
        ver_ubuntu_noble_1: BootAssetVersion,
        filter_param: str,
    ) -> None:
        count, [rbav] = await boot_asset_version_service.get(
            [],
            0,
            None,
            **{filter_param: [ver_ubuntu_jammy_1.model_dump()[filter_param]]},
        )
        assert count == 1
        assert rbav == ver_ubuntu_jammy_1

    async def test_create(
        self,
        factory: Factory,
        boot_asset_version_service: BootAssetVersionService,
        ubuntu_jammy: BootAsset,
    ) -> None:
        new_boot_asset_version = BootAssetVersionCreate(
            boot_asset_id=ubuntu_jammy.id,
            version="20250227.1",
            last_seen=factory.now,
        )
        boot_asset_version = await boot_asset_version_service.create(
            new_boot_asset_version
        )
        expected_boot_asset_version = BootAssetVersion(
            id=boot_asset_version.id,
            **new_boot_asset_version.model_dump(),
        )
        versions = await factory.get("boot_asset_version")
        assert len(versions) == 1
        assert versions[0] == expected_boot_asset_version.model_dump()

    async def test_delete(
        self,
        factory: Factory,
        boot_asset_version_service: BootAssetVersionService,
        ver_ubuntu_jammy_1: BootAssetVersion,
    ) -> None:
        await boot_asset_version_service.delete(ver_ubuntu_jammy_1.id)
        versions = await factory.get("boot_asset_version")
        assert len(versions) == 0

    async def test_delete_by_asset_id(
        self,
        factory: Factory,
        boot_asset_version_service: BootAssetVersionService,
        ubuntu_jammy: BootAsset,
    ) -> None:
        await boot_asset_version_service.delete_by_asset_id(ubuntu_jammy.id)
        versions = await factory.get("boot_asset_version")
        assert len(versions) == 0

    async def test_upsert(
        self,
        factory: Factory,
        boot_asset_version_service: BootAssetVersionService,
        ubuntu_jammy: BootAsset,
    ) -> None:
        now = factory.now

        # First upsert should insert
        new_version = BootAssetVersionCreate(
            boot_asset_id=ubuntu_jammy.id,
            version="20250227.1",
            last_seen=now,
        )
        upserted = await boot_asset_version_service.upsert(new_version)
        expected = BootAssetVersion(
            id=upserted.id,
            boot_asset_id=ubuntu_jammy.id,
            version="20250227.1",
            last_seen=now,
        )
        assert upserted == expected

        # Second upsert should update
        updated_time = now.replace(year=now.year + 1)
        updated_version = BootAssetVersionCreate(
            boot_asset_id=ubuntu_jammy.id,
            version="20250227.1",
            last_seen=updated_time,
        )
        upserted2 = await boot_asset_version_service.upsert(updated_version)
        expected2 = BootAssetVersion(
            id=upserted.id,
            boot_asset_id=ubuntu_jammy.id,
            version="20250227.1",
            last_seen=updated_time,
        )
        assert upserted2 == expected2

        # There should only be one version in the DB
        versions = await factory.get("boot_asset_version")
        assert len(versions) == 1


class TestBootAssetItemService:
    async def test_get(
        self,
        boot_asset_item_service: BootAssetItemService,
        items_ubuntu_noble_1: list[BootAssetItem],
    ) -> None:
        count, items = await boot_asset_item_service.get([])
        assert count == 3
        got = list(items)
        assert got == items_ubuntu_noble_1

    @pytest.mark.parametrize(
        "filter_param",
        [
            ("boot_asset_version_id"),
            ("ftype"),
            ("sha256"),
            ("path"),
            ("file_size"),
        ],
    )
    async def test_get_with_filters(
        self,
        boot_asset_item_service: BootAssetItemService,
        items_ubuntu_noble_1: list[BootAssetItem],
        filter_param: str,
    ) -> None:
        item = items_ubuntu_noble_1[0]
        filters = {filter_param: [item.model_dump()[filter_param]]}
        count, items = await boot_asset_item_service.get(
            [], 0, None, **filters
        )
        assert count >= 1
        assert next(iter(items)) == item

    @pytest.mark.parametrize(
        "exists",
        [
            (True),
            (False),
        ],
    )
    async def test_get_by_id(
        self,
        boot_asset_item_service: BootAssetItemService,
        items_ubuntu_noble_1: list[BootAssetItem],
        exists: bool,
    ) -> None:
        details = items_ubuntu_noble_1[0].model_dump()
        id = details["id"] if exists else -1

        assert await boot_asset_item_service.get_by_id(id) == (
            BootAssetItem(**details) if exists else None
        )

    @pytest.mark.parametrize(
        "exists",
        [
            (True),
            (False),
        ],
    )
    async def test_get_by_path(
        self,
        boot_asset_item_service: BootAssetItemService,
        ubuntu_noble: BootAsset,
        items_ubuntu_noble_1: list[BootAssetItem],
        exists: bool,
    ) -> None:
        details = items_ubuntu_noble_1[0].model_dump()
        boot_source_id = ubuntu_noble.boot_source_id
        path = details["path"] if exists else "asdf/asdf"

        assert await boot_asset_item_service.get_by_path(
            boot_source_id, path
        ) == (BootAssetItem(**details) if exists else None)

    async def test_create(
        self,
        factory: Factory,
        boot_asset_item_service: BootAssetItemService,
        ver_ubuntu_noble_1: BootAssetVersion,
    ) -> None:
        new_boot_asset_item = BootAssetItemCreate(
            boot_asset_version_id=ver_ubuntu_noble_1.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="2349asldkfj2309854jhs",
            path="/test",
            file_size=23425323,
            source_package="ubukernel",
            source_version="23.2",
            source_release="Noble",
        )
        boot_asset_item = await boot_asset_item_service.create(
            new_boot_asset_item
        )
        expected_boot_asset_item = BootAssetItem(
            id=boot_asset_item.id,
            bytes_synced=0,
            **new_boot_asset_item.model_dump(),
        )
        items = await factory.get("boot_asset_item")
        assert len(items) == 1
        assert items[0] == expected_boot_asset_item.model_dump()

    async def test_create_temporary(
        self,
        factory: Factory,
        boot_asset_item_service: BootAssetItemService,
        ver_ubuntu_noble_1: BootAssetVersion,
    ) -> None:
        boot_asset_item = await boot_asset_item_service.create_temporary(
            ver_ubuntu_noble_1.id
        )
        items = await factory.get("boot_asset_item")
        assert len(items) == 1
        assert items[0] == {
            "id": boot_asset_item.id,
            "boot_asset_version_id": ver_ubuntu_noble_1.id,
            "ftype": ItemFileType.ROOT_TGZ,
            "sha256": "",
            "path": "",
            "file_size": 0,
            "source_package": None,
            "source_version": None,
            "source_release": None,
            "bytes_synced": 0,
        }

    async def test_update(
        self,
        factory: Factory,
        boot_asset_item_service: BootAssetItemService,
        items_ubuntu_noble_1: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_1[0]
        updates = BootAssetItemUpdate(
            ftype=ItemFileType.BOOT_INITRD,
            sha256="asdflkj234lkjsdlfkj23",
            path="/another-test",
            file_size=33425323,
            source_package="kern",
            source_version="34.3",
            source_release="Jammy",
            bytes_synced=23425322,
        )
        await boot_asset_item_service.update(item.id, updates)
        items = await factory.get("boot_asset_item")
        assert len(items) == len(items_ubuntu_noble_1)
        updates_dict = updates.model_dump()
        updates_dict.pop("boot_asset_version_id")
        expected_item = BootAssetItem(
            id=item.id,
            boot_asset_version_id=item.boot_asset_version_id,
            **updates_dict,
        )
        assert items[0] == expected_item.model_dump()

    async def test_delete(
        self,
        factory: Factory,
        boot_asset_item_service: BootAssetItemService,
        items_ubuntu_noble_1: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_1[0]
        await boot_asset_item_service.delete(item.id)
        items = await factory.get("boot_asset_item")
        assert len(items) == len(items_ubuntu_noble_1) - 1

    async def test_update_bytes_synced(
        self,
        factory: Factory,
        boot_asset_item_service: BootAssetItemService,
        items_ubuntu_noble_1: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_1[0]

        await boot_asset_item_service.update_bytes_synced(item.id, 23425323)
        items = await factory.get("boot_asset_item")
        assert items[0]["bytes_synced"] == 23425323

    async def test_delete_by_version_id(
        self,
        factory: Factory,
        boot_asset_item_service: BootAssetItemService,
        items_ubuntu_noble_1: list[BootAssetItem],
    ) -> None:
        id = items_ubuntu_noble_1[0].boot_asset_version_id
        assert id is not None
        await boot_asset_item_service.delete_by_version_id(id)
        items = await factory.get("boot_asset_item")
        assert len(items) == 0


class TestImagesIndexService:
    async def test_create(
        self,
        index_service: IndexService,
        items_ubuntu_jammy_1: list[BootAssetItem],
        items_ubuntu_noble_1: list[BootAssetItem],
        items_ubuntu_noble_2: list[BootAssetItem],
        items_grub: list[BootAssetItem],
        db_connection: AsyncConnection,
    ) -> None:
        await index_service.refresh()
        index = await db_connection.execute(
            text("SELECT * FROM images_index;")
        )
        expected = {
            "ubuntu/noble": {"amd64": 3, "arm64": 0},
            "ubuntu/jammy": {"amd64": 3, "arm64": 0},
            "grub-efi-signed/None": {"amd64": 0, "arm64": 2},
        }
        found_entries = {
            "ubuntu/noble": {"amd64": 0, "arm64": 0},
            "ubuntu/jammy": {"amd64": 0, "arm64": 0},
            "grub-efi-signed/None": {"amd64": 0, "arm64": 0},
        }
        for item in [x._asdict() for x in index.all()]:
            found_entries[f'{item["os"]}/{item["release"]}'][item["arch"]] += 1
        assert expected == found_entries

    async def test_get_index(
        self,
        index_service: IndexService,
        items_ubuntu_jammy_1: list[BootAssetItem],
        items_ubuntu_noble_1: list[BootAssetItem],
        items_grub: list[BootAssetItem],
    ) -> None:
        await index_service.refresh()
        index = await index_service.get(IndexType.INDEX, "maas.site.manager")

        expected_index = {
            "format": "index:1.0",
            "updated": index["updated"],
            "index": {
                "manager.site.maas:stream:v1:download": {
                    "updated": index["updated"],
                    "datatype": "image-ids",
                    "format": "products:1.0",
                    "path": "streams/v1/manager.site.maas:stream:v1:download.json",
                    "products": [
                        "manager.site.maas.stream:grub-efi-signed:uefi:arm64",
                        "manager.site.maas.stream:ubuntu:jammy:amd64:ga-22.04-generic",
                        "manager.site.maas.stream:ubuntu:noble:amd64:hwe-24.04-generic",
                    ],
                },
            },
        }
        assert index == expected_index

    async def test_get_download_index(
        self,
        mocker: MockerFixture,
        index_service: IndexService,
        items_ubuntu_jammy_1: list[BootAssetItem],
        items_ubuntu_noble_1: list[BootAssetItem],
        items_grub: list[BootAssetItem],
    ) -> None:
        mock_now = mocker.patch(
            "msm.service.images.now_utc",
            return_value=datetime.fromtimestamp(0.0),
        )

        await index_service.refresh()

        index = await index_service.get(
            IndexType.DOWNLOAD, "maas.site.manager"
        )
        expected_index = """
            {
                "content_id": "manager.site.maas:stream:v1:download",
                "datatype": "image-ids",
                "format": "products:1.0",
                "products": {
                    "manager.site.maas.stream:ubuntu:jammy:amd64:ga-22.04-generic": {
                        "arch": "amd64",
                        "kflavor": "generic",
                        "label": "stable",
                        "os": "ubuntu",
                        "release": "jammy",
                        "release_title": "22.04 LTS",
                        "subarch": "ga-22.04",
                        "support_eol": "2027-04-21",
                        "support_esm_eol": "2032-04-21",
                        "versions": {
                            "20250601": {
                                "items": {
                                    "boot-initrd": {
                                        "ftype": "boot-initrd",
                                        "path": "2/20250601/ga-22.04/boot-initrd",
                                        "sha256": "abc456",
                                        "size": 465
                                    },
                                    "squashfs": {
                                        "ftype": "squashfs",
                                        "path": "2/20250601/squashfs",
                                        "sha256": "12345555",
                                        "size": 12345555
                                    },
                                    "boot-kernel": {
                                        "ftype": "boot-kernel",
                                        "path": "2/20250601/ga-22.04/boot-kernel",
                                        "sha256": "abc123",
                                        "size": 123
                                    }
                                }
                            }
                        }
                    },
                    "manager.site.maas.stream:grub-efi-signed:uefi:arm64": {
                        "arch": "arm64",
                        "label": "candidate",
                        "os": "grub-efi-signed",
                        "bootloader-type": "uefi",
                        "versions": {
                            "20250401": {
                                "items": {
                                    "grub2-signed": {
                                        "ftype": "archive.tar.xz",
                                        "path": "3/20250401/grub2-signed.tar.xz",
                                        "sha256": "deadbeef",
                                        "size": 8888,
                                        "src_package": "grub2-signed",
                                        "src_release": "focal",
                                        "src_version": "1.167.2+2.04-1ubuntu44.2"
                                    },
                                    "shim-signed": {
                                        "ftype": "archive.tar.xz",
                                        "path": "3/20250401/shim-signed.tar.xz",
                                        "sha256": "deadbeef2",
                                        "size": 7777,
                                        "src_package": "shim-signed",
                                        "src_release": "focal",
                                        "src_version": "1.167.2+2.04-1ubuntu44.2"
                                    }
                                }
                            }
                        }
                    },
                    "manager.site.maas.stream:ubuntu:noble:amd64:hwe-24.04-generic": {
                        "arch": "amd64",
                        "kflavor": "generic",
                        "label": "stable",
                        "os": "ubuntu",
                        "release": "noble",
                        "release_title": "24.04 LTS",
                        "subarch": "hwe-24.04",
                        "support_eol": "2029-05-31",
                        "support_esm_eol": "2034-04-25",
                        "versions": {
                            "20250701": {
                                "items": {
                                    "squashfs": {
                                        "ftype": "squashfs",
                                        "path": "2/20250701/squashfs",
                                        "sha256": "12345555",
                                        "size": 12345555
                                    },
                                    "boot-kernel": {
                                        "ftype": "boot-kernel",
                                        "path": "2/20250701/hwe-24.04/boot-kernel",
                                        "sha256": "abc123",
                                        "size": 123
                                    },
                                    "boot-initrd": {
                                        "ftype": "boot-initrd",
                                        "path": "2/20250701/hwe-24.04/boot-initrd",
                                        "sha256": "abc456",
                                        "size": 465
                                    }
                                }
                            }
                        }
                    }
                },
                "updated": "Thu, 01 Jan 1970 00:00:00 "
            }
            """

        expected_index_json = json.loads(expected_index)
        expected_index_json["updated"] = index["updated"]
        assert index == expected_index_json

    async def test_incomplete_set_not_included(
        self,
        index_service: IndexService,
        items_ubuntu_jammy_1: list[BootAssetItem],
        items_ubuntu_noble_2: list[BootAssetItem],
        items_grub: list[BootAssetItem],
    ) -> None:
        await index_service.refresh()
        index = await index_service.get(
            IndexType.INDEX, fqdn="maas.site.manager"
        )
        dl_index = await index_service.get(
            IndexType.DOWNLOAD, fqdn="maas.site.manager"
        )

        # items_ubuntu_noble_2 has incomplete items
        n_products = len(
            index["index"]["manager.site.maas:stream:v1:download"]["products"]
        )
        assert n_products == 2
        assert len(dl_index["products"]) == 2

    async def test_drop(
        self,
        index_service: IndexService,
    ) -> None:
        await index_service.create()
        await index_service.drop()
        with pytest.raises(IndexNotFound):
            await index_service.get(IndexType.DOWNLOAD, "maas.site.manager")
