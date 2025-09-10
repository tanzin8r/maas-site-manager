from typing import Any
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from msm.api.user.handlers.bootassets import purge_and_refresh
from msm.api.user.models.bootassets import (
    BootSourcesAssetsPutRequest,
    BootSourcesAssetsPutResponse,
    Product,
    ProductItem,
)
from msm.db.models import (
    BootAsset,
    BootAssetItem,
    BootAssetKind,
    BootAssetLabel,
    BootAssetVersion,
    BootSource,
    BootSourceSelection,
    ItemFileType,
)
from msm.jwt import TokenAudience, TokenPurpose
from msm.service.images import END_OF_TIME
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestBootSourcesGetHandler:
    async def test_get(
        self,
        user_client: Client,
        boot_source_custom: BootSource,
        boot_source: BootSource,
    ) -> None:
        sources = await user_client.get("/bootasset-sources")
        assert sources.status_code == 200
        resp_body = sources.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 2
        assert resp_body["items"] == [
            boot_source_custom.model_dump(mode="json"),
            boot_source.model_dump(mode="json"),
        ]

    async def test_get_by_id(
        self, user_client: Client, boot_source: BootSource
    ) -> None:
        resp = await user_client.get(f"/bootasset-sources/{boot_source.id}")
        assert resp.status_code == 200
        source = BootSource(**resp.json())
        assert source == boot_source

    async def test_get_by_id_not_found(self, user_client: Client) -> None:
        resp = await user_client.get("/bootasset-sources/999")
        assert resp.status_code == 404

    async def test_get_with_sorting(
        self,
        user_client: Client,
        boot_source_custom: BootSource,
        boot_source: BootSource,
    ) -> None:
        assets = await user_client.get("/bootasset-sources?sort_by=url")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            boot_source.model_dump(mode="json"),
            boot_source_custom.model_dump(mode="json"),
        ]
        assets = await user_client.get("/bootasset-sources?sort_by=name")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            boot_source_custom.model_dump(mode="json"),
            boot_source.model_dump(mode="json"),
        ]

    async def test_get_with_page_and_size(
        self,
        user_client: Client,
        boot_source: BootSource,
        boot_source_grub: BootSource,
        boot_source_low: BootSource,
    ) -> None:
        resp = await user_client.get(
            "/bootasset-sources?page=2&size=2&sort_by=priority"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 2
        assert resp_body["items"][1]["priority"] == boot_source.priority

    @pytest.mark.parametrize("sort_by", ["id", "kind,kind", "not_a_field"])
    async def test_invalid_sort_params(
        self, user_client: Client, sort_by: str
    ) -> None:
        resp = await user_client.get(f"/bootasset-sources?sort_by={sort_by}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, page: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-sources?page={page}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, size: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-sources?size={size}")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootSourcesPostHandler:
    async def test_post(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        boot_source_custom: BootSource,
    ) -> None:
        mock_now = mocker.patch(
            "msm.api.user.handlers.bootassets.now_utc",
            return_value=factory.now,
        )
        data = {
            "priority": 1,
            "url": "http://some.image.server",
            "keyring": "testkeyring",
            "sync_interval": 1000,
            "name": "Test Source",
        }
        resp = await user_client.post("/bootasset-sources", json=data)
        new_id = resp.json()["id"]
        assert resp.status_code == 200
        stored = await factory.get("boot_source")
        assert len(stored) == 2
        assert stored[1] == data | {"id": new_id, "last_sync": factory.now}

    @pytest.mark.parametrize(
        "field", ["priority", "url", "keyring", "sync_interval", "name"]
    )
    async def test_post_missing_details(
        self,
        user_client: Client,
        field: str,
    ) -> None:
        data = {
            "priority": 1,
            "url": "http://some.image.server",
            "keyring": "testkeyring",
            "sync_interval": 1000,
            "name": "Test Source",
        }
        data.pop(field)
        resp = await user_client.post("/bootasset-sources", json=data)
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootSourcesUpdateHandler:
    async def test_update(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
    ) -> None:
        orig_last_sync = boot_source.last_sync
        data = {
            "priority": 2,
            "url": "http://another.url",
            "keyring": "another-keyring",
            "sync_interval": 200,
            "name": "Another Name",
        }
        resp = await user_client.patch(
            f"/bootasset-sources/{boot_source.id}", json=data
        )
        assert resp.status_code == 200
        ret_obj = resp.json()
        assert all([ret_obj[k] == data[k] for k in data.keys()])

        sources = await factory.get("boot_source")
        assert len(sources) == 2
        assert all([sources[1][k] == data[k] for k in data.keys()])
        assert sources[1]["last_sync"] == orig_last_sync

    async def test_update_custom_source_fails(
        self,
        user_client: Client,
    ) -> None:
        resp = await user_client.patch(
            f"/bootasset-sources/1", json={"priority": 2}
        )
        assert resp.status_code == 422

    async def test_update_no_fields(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
    ) -> None:
        resp = await user_client.patch(
            f"/bootasset-sources/{boot_source.id}", json={}
        )
        assert resp.status_code == 422

    async def test_update_extra_fields(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
    ) -> None:
        data = {
            "priority": 2,
            "url": "http://another.url",
            "keyring": "another-keyring",
            "sync_interval": 200,
            "name": "Another Source",
            "something": "extra",
        }
        resp = await user_client.patch(
            f"/bootasset-sources/{boot_source.id}", json=data
        )
        assert resp.status_code == 422

    async def test_update_not_found(self, user_client: Client) -> None:
        resp = await user_client.patch(
            "/bootasset-sources/333", json={"priority": 2}
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestBootSourcesDeleteHandler:
    async def test_delete(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        boot_source: BootSource,
    ) -> None:
        mock_background = mocker.patch(
            "msm.api.user.handlers.bootassets.BackgroundTasks.add_task",
        )
        resp = await user_client.delete(f"/bootasset-sources/{boot_source.id}")
        assert resp.status_code == 200
        mock_background.assert_called_once_with(
            purge_and_refresh, mocker.ANY, boot_source.id
        )

    async def test_delete_not_found(self, user_client: Client) -> None:
        resp = await user_client.delete("/bootasset-sources/333")
        assert resp.status_code == 404

    async def test_cant_delete_custom_source(
        self, user_client: Client
    ) -> None:
        resp = await user_client.delete("/bootasset-sources/1")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootSourceSelectionsGetHandler:
    async def test_get(
        self,
        user_client: Client,
        sel_ubuntu_jammy: list[BootSourceSelection],
        sel_centos: BootSourceSelection,
    ) -> None:
        bs_id = sel_ubuntu_jammy[0].boot_source_id
        selections = await user_client.get(
            f"/bootasset-sources/{bs_id}/selections"
        )
        assert selections.status_code == 200
        resp_body = selections.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 2
        assert resp_body["items"] == [
            sel.model_dump(mode="json") for sel in sel_ubuntu_jammy
        ]

    async def test_get_with_sorting(
        self,
        user_client: Client,
        sel_ubuntu_jammy: list[BootSourceSelection],
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        bs_id = sel_ubuntu_jammy[0].boot_source_id
        assets = await user_client.get(
            f"/bootasset-sources/{bs_id}/selections?sort_by=release"
        )
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            sel_ubuntu_jammy[0].model_dump(mode="json"),
            sel_ubuntu_jammy[1].model_dump(mode="json"),
            sel_ubuntu_noble[0].model_dump(mode="json"),
            sel_ubuntu_noble[1].model_dump(mode="json"),
        ]
        assets = await user_client.get(
            f"/bootasset-sources/{bs_id}/selections?sort_by=arch"
        )
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            sel_ubuntu_jammy[1].model_dump(mode="json"),
            sel_ubuntu_noble[1].model_dump(mode="json"),
            sel_ubuntu_noble[0].model_dump(mode="json"),
            sel_ubuntu_jammy[0].model_dump(mode="json"),
        ]

    async def test_get_with_page_and_size(
        self,
        user_client: Client,
        sel_ubuntu_jammy: list[BootSourceSelection],
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        bs_id = sel_ubuntu_jammy[0].boot_source_id

        resp = await user_client.get(
            f"/bootasset-sources/{bs_id}/selections?page=2&size=1&sort_by=release"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 1
        assert len(resp_body["items"]) == 1
        assert resp_body["items"][0]["release"] == sel_ubuntu_jammy[1].release

    @pytest.mark.parametrize("sort_by", ["id", "kind,kind", "not_a_field"])
    async def test_invalid_sort_params(
        self, user_client: Client, sort_by: str
    ) -> None:
        resp = await user_client.get(
            f"/bootasset-sources/1/selections?sort_by={sort_by}"
        )
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, page: int
    ) -> None:
        resp = await user_client.get(
            f"/bootasset-sources/1/selections?page={page}"
        )
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, size: int
    ) -> None:
        resp = await user_client.get(
            f"/bootasset-sources/1/selections?size={size}"
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootSourceAvailSelectionsPutHandler:
    async def test_put_add_and_update_selections(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        # update the existing noble selections
        up_sel_1 = {
            "os": sel_ubuntu_noble[0].os,
            "release": sel_ubuntu_noble[0].release,
            "label": sel_ubuntu_noble[0].label,
            "arch": "amd64",
        }
        up_sel_2 = {
            "os": sel_ubuntu_noble[0].os,
            "release": sel_ubuntu_noble[0].release,
            "label": sel_ubuntu_noble[0].label,
            "arch": "arm64",
        }
        new_sel = {
            "os": "centos",
            "release": "stream9",
            "label": "candidate",
            "arch": "amd64",
        }
        put_data = {"available": [up_sel_1, up_sel_2, new_sel]}
        resp = await user_client.put(
            f"/bootasset-sources/{boot_source.id}/available-selections",
            json=put_data,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "stale" in data
        # The original selection should be updated, and a new one added
        stored = await factory.get("boot_source_selection")
        stored = [
            {
                "os": sel["os"],
                "arch": sel["arch"],
                "release": sel["release"],
                "label": sel["label"],
            }
            for sel in stored
        ]
        assert len(stored) == 3
        assert up_sel_1 in stored
        assert up_sel_2 in stored
        assert new_sel in stored

    async def test_put_removes_stale_selections(
        self,
        user_client: Client,
        boot_source: BootSource,
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        # Remove all selections (should mark existing as stale)
        put_data: dict[str, Any] = {"available": []}
        resp = await user_client.put(
            f"/bootasset-sources/{boot_source.id}/available-selections",
            json=put_data,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["stale"], list)
        assert all(
            s["id"] in (sel.id for sel in sel_ubuntu_noble)
            for s in data["stale"]
        )

    async def test_put_boot_source_not_found(
        self,
        user_client: Client,
    ) -> None:
        put_data: dict[str, Any] = {"available": []}
        resp = await user_client.put(
            "/bootasset-sources/9999/available-selections", json=put_data
        )
        assert resp.status_code == 404

    async def test_put_invalid_payload(
        self,
        user_client: Client,
        boot_source: BootSource,
    ) -> None:
        # Missing 'available' field
        resp = await user_client.put(
            f"/bootasset-sources/{boot_source.id}/available-selections",
            json={},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootAssetItemsPatchHandler:
    async def test_patch(
        self,
        user_client: Client,
        factory: Factory,
        items_ubuntu_noble_2: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_2[0]
        data = {
            "ftype": ItemFileType.ROOT_TGZ,
            "source_package": "testpackage2",
            "source_version": "testversion2",
            "source_release": "testrelease2",
        }
        resp = await user_client.patch(
            f"/bootasset-items/{item.id}", json=data
        )
        assert resp.status_code == 200
        stored = await factory.get("boot_asset_item")
        assert len(stored) == len(items_ubuntu_noble_2)
        assert stored[0] == data | {
            "id": item.id,
            "boot_asset_version_id": item.boot_asset_version_id,
            "file_size": item.file_size,
            "bytes_synced": item.bytes_synced,
            "sha256": item.sha256,
            "path": item.path,
        }

    async def test_patch_no_values(
        self,
        user_client: Client,
        factory: Factory,
        items_ubuntu_noble_2: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_2[0]
        resp = await user_client.patch(
            f"/bootasset-items/{item.id}",
        )
        assert resp.status_code == 422
        stored = await factory.get("boot_asset_item")
        assert len(stored) == 3
        assert stored[0] == item.model_dump()

    async def test_patch_extra_params(
        self,
        user_client: Client,
        factory: Factory,
        items_ubuntu_noble_2: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_2[0]
        data = {
            "ftype": ItemFileType.BOOT_DTB,
            "sha256": "testsha2",
            "path": "testpath2",
            "file_size": 2,
            "source_package": "testpackage2",
            "source_version": "testversion2",
            "source_release": "testrelease2",
        }
        resp = await user_client.patch(
            f"/bootasset-items/{item.id}", json=data
        )
        assert resp.status_code == 422
        stored = await factory.get("boot_asset_item")
        assert len(stored) == 3
        assert stored[0] == item.model_dump()

    async def test_patch_bad_item_id(
        self,
        user_client: Client,
        factory: Factory,
        items_ubuntu_noble_2: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_2[0]
        data = {
            "ftype": ItemFileType.BOOT_DTB,
            "source_package": "testpackage2",
            "source_version": "testversion2",
            "source_release": "testrelease2",
        }
        resp = await user_client.patch(f"/bootasset-items/{9999}", json=data)
        assert resp.status_code == 404
        stored = await factory.get("boot_asset_item")
        assert len(stored) == 3
        assert stored[0] == item.model_dump()

    async def test_users_cannot_change_bytes_synced(
        self,
        user_client: Client,
        factory: Factory,
        items_ubuntu_noble_2: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_2[0]
        data = {"bytes_synced": 2}
        resp = await user_client.patch(
            f"/bootasset-items/{item.id}", json=data
        )
        assert resp.status_code == 403
        stored = await factory.get("boot_asset_item")
        assert stored[0]["bytes_synced"] == item.bytes_synced

    async def test_workers_can_change_bytes_synced(
        self,
        app_client: Client,
        factory: Factory,
        items_ubuntu_noble_2: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_2[0]
        auth_id = uuid4()
        await factory.make_Token(
            auth_id=auth_id,
            audience=TokenAudience.WORKER,
            purpose=TokenPurpose.ACCESS,
        )
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.WORKER,
            token_purpose=TokenPurpose.ACCESS,
        )
        data = {"bytes_synced": 1}
        resp = await app_client.patch(
            f"/api/v1/bootasset-items/{item.id}", json=data
        )
        assert resp.status_code == 200
        stored = await factory.get("boot_asset_item")
        assert len(stored) == 3
        assert stored[0]["bytes_synced"] == data["bytes_synced"]


@pytest.mark.asyncio
class TestPutBootSourceAssetsEndpoint:
    @pytest.fixture
    def version_oracular_new(self) -> tuple[str, list[ProductItem]]:
        return "20250401", [
            ProductItem(
                ftype=ItemFileType.BOOT_KERNEL,
                sha256="abc123",
                path="oracular/amd64/20250401/ga-24.10/generic/boot-kernel",
                file_size=12345,
            ),
            ProductItem(
                ftype=ItemFileType.BOOT_INITRD,
                sha256="abc123",
                path="oracular/amd64/20250401/ga-24.10/generic/boot-initrd",
                file_size=12345,
            ),
            ProductItem(
                ftype=ItemFileType.SQUASHFS_IMAGE,
                sha256="abc123",
                path="oracular/amd64/20250401/squashfs",
                file_size=12345,
            ),
        ]

    @pytest.fixture
    def version_noble_existing(
        self,
        ver_ubuntu_noble_1: BootAssetVersion,
        items_ubuntu_noble_1: list[BootAssetItem],
    ) -> tuple[str, list[ProductItem]]:
        items = [
            ProductItem(
                ftype=i.ftype,
                sha256=i.sha256,
                path=i.path,
                file_size=i.file_size,
            )
            for i in items_ubuntu_noble_1
        ]
        return ver_ubuntu_noble_1.version, items

    @pytest.fixture
    def version_noble_new(self) -> tuple[str, list[ProductItem]]:
        return "20250802", [
            ProductItem(
                ftype=ItemFileType.BOOT_KERNEL,
                sha256="cadecafe",
                path="noble/amd64/20250802/ga-24.04/generic/boot-kernel",
                file_size=456789,
            ),
            ProductItem(
                ftype=ItemFileType.BOOT_INITRD,
                sha256="cadecafe",
                path="noble/amd64/20250802/ga-24.04/generic/boot-initrd",
                file_size=456789,
            ),
            ProductItem(
                ftype=ItemFileType.SQUASHFS_IMAGE,
                sha256="cadecafe",
                path="noble/amd64/20250802/squashfs",
                file_size=456789,
            ),
        ]

    @pytest.fixture
    def product_noble(self, ubuntu_noble: BootAsset) -> Product:
        return Product(
            kind=ubuntu_noble.kind,
            label=ubuntu_noble.label,
            os=ubuntu_noble.os,
            release=ubuntu_noble.release,
            title=ubuntu_noble.title,
            arch=ubuntu_noble.arch,
            subarch=ubuntu_noble.subarch,
            flavor=ubuntu_noble.flavor,
            codename=ubuntu_noble.codename,
            compatibility=[
                "ga-23.10",
                "ga-24.04",
            ],
            eol=END_OF_TIME,
            esm_eol=END_OF_TIME,
            signed=True,
            versions={},
        )

    @pytest.fixture
    def product_oracular(
        self, version_oracular_new: tuple[str, list[ProductItem]]
    ) -> Product:
        return Product(
            kind=BootAssetKind.OS,
            label=BootAssetLabel.CANDIDATE,
            os="ubuntu",
            release="oracular",
            title="Ubuntu Oracular",
            arch="amd64",
            subarch="ga-24.10",
            flavor="generic",
            codename="Oracular Oriole",
            compatibility=[
                "ga-24.04",
                "ga-24.10",
            ],
            eol=END_OF_TIME,
            esm_eol=END_OF_TIME,
            signed=True,
            versions={version_oracular_new[0]: version_oracular_new[1]},
        )

    async def test_new_asset_success(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
        product_oracular: Product,
    ) -> None:
        put_request = BootSourcesAssetsPutRequest(products=[product_oracular])
        resp = await user_client.put(
            f"/bootasset-sources/{boot_source.id}/assets",
            json=put_request.model_dump(mode="json"),
        )
        assert resp.status_code == 200
        data = BootSourcesAssetsPutResponse.model_validate(resp.json())
        assert len(data.to_download) == 3

        items = await factory.get("boot_asset_item")
        assert len(items) == 3
        versions = await factory.get("boot_asset_version")
        assert len(versions) == 1
        [oracular] = await factory.get("boot_asset")
        assert oracular["release"] == product_oracular.release

    async def test_idempotent(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
        product_noble: Product,
        version_noble_existing: tuple[str, list[ProductItem]],
    ) -> None:
        product_noble.versions = {
            version_noble_existing[0]: version_noble_existing[1]
        }
        put_request = BootSourcesAssetsPutRequest(products=[product_noble])
        resp = await user_client.put(
            f"/bootasset-sources/{boot_source.id}/assets",
            json=put_request.model_dump(mode="json"),
        )
        assert resp.status_code == 200
        data = BootSourcesAssetsPutResponse.model_validate(resp.json())
        assert len(data.to_download) == 0

    async def test_new_version(
        self,
        user_client: Client,
        boot_source: BootSource,
        product_noble: Product,
        version_noble_new: tuple[str, list[ProductItem]],
    ) -> None:
        product_noble.versions = {version_noble_new[0]: version_noble_new[1]}
        put_request = BootSourcesAssetsPutRequest(products=[product_noble])
        resp = await user_client.put(
            f"/bootasset-sources/{boot_source.id}/assets",
            json=put_request.model_dump(mode="json"),
        )
        assert resp.status_code == 200
        data = BootSourcesAssetsPutResponse.model_validate(resp.json())
        assert len(data.to_download) == 3

    async def test_put_boot_source_assets_not_found(
        self,
        user_client: Client,
        product_noble: Product,
    ) -> None:
        put_request = BootSourcesAssetsPutRequest(products=[product_noble])
        resp = await user_client.put(
            "/v1/bootasset-sources/999999/assets",
            json=put_request.model_dump(mode="json"),
        )
        assert resp.status_code == 404

    async def test_put_boot_source_assets_validation_error(
        self,
        user_client: Client,
        boot_source: BootSource,
    ) -> None:
        # Send invalid payload (missing products)
        resp = await user_client.put(
            f"/bootasset-sources/{boot_source.id}/assets",
            json={},
        )
        assert resp.status_code == 422
