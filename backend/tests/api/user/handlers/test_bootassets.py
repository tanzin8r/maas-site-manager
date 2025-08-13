from datetime import datetime, timedelta
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
from msm.time import now_utc
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestBootAssetsGetHandler:
    async def test_get(
        self,
        user_client: Client,
        boot_source: BootSource,
        ubuntu_noble: BootAsset,
    ) -> None:
        assets = await user_client.get("/bootassets")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 1
        resp_body["items"][0]["id"] = ubuntu_noble.id
        assert resp_body["items"] == [
            ubuntu_noble.model_dump(mode="json")
            | {"source_name": boot_source.name}
        ]

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
        user_client: Client,
        ubuntu_jammy: BootAsset,
        grub: BootAsset,
        filter_param: str,
    ) -> None:
        url = f"/bootassets?{filter_param}={ubuntu_jammy.model_dump(mode="json")[filter_param]}"
        resp = await user_client.get(url)
        assert resp.status_code == 200
        resp_body = resp.json()
        assert len(resp_body["items"]) == 1
        assert resp_body["items"][0]["id"] == ubuntu_jammy.id

    async def test_get_with_sorting(
        self,
        user_client: Client,
        ubuntu_jammy: BootAsset,
        centos: BootAsset,
    ) -> None:
        assets = await user_client.get("/bootassets?sort_by=os")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert [item["id"] for item in resp_body["items"]] == [
            centos.id,
            ubuntu_jammy.id,
        ]
        assets = await user_client.get("/bootassets?sort_by=title")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert [item["id"] for item in resp_body["items"]] == [
            ubuntu_jammy.id,
            centos.id,
        ]

    async def test_get_with_page_and_size(
        self,
        user_client: Client,
        centos: BootAsset,
        ubuntu_jammy: BootAsset,
        ubuntu_noble: BootAsset,
    ) -> None:
        resp = await user_client.get("/bootassets?page=2&size=2&sort_by=os")
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 1
        assert resp_body["items"][0]["release"] == "jammy"

    @pytest.mark.parametrize("sort_by", ["id", "kind,kind", "not_a_field"])
    async def test_invalid_sort_params(
        self, user_client: Client, sort_by: str
    ) -> None:
        resp = await user_client.get(f"/bootassets?sort_by={sort_by}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, page: int
    ) -> None:
        resp = await user_client.get(f"/bootassets?page={page}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, size: int
    ) -> None:
        resp = await user_client.get(f"/bootassets?size={size}")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootAssetsPostHandler:
    async def test_post(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
    ) -> None:
        data = {
            "boot_source_id": boot_source.id,
            "kind": BootAssetKind.BOOTLOADER,
            "label": BootAssetLabel.CANDIDATE,
            "os": "ubuntu",
            "release": "noble",
            "codename": "Noble Numbat",
            "title": "My Custom Image",
            "arch": "amd64",
            "subarch": "generic",
            "compatibility": ["generic"],
            "flavor": "generic",
            "base_image": "ubuntu",
            "bootloader_type": "uefi",
            "eol": (now_utc() + timedelta(days=365)).isoformat(),
            "esm_eol": (now_utc() + timedelta(days=3650)).isoformat(),
            "signed": True,
        }
        resp = await user_client.post("/bootassets", json=data)
        new_id = resp.json()["id"]
        assert resp.status_code == 200
        stored = await factory.get("boot_asset")
        assert len(stored) == 1
        data["eol"] = datetime.fromisoformat(data["eol"])  # type: ignore
        data["esm_eol"] = datetime.fromisoformat(data["esm_eol"])  # type: ignore
        assert stored[0] == data | {"id": new_id}

    async def test_post_missing_details(
        self,
        user_client: Client,
        boot_source: BootSource,
    ) -> None:
        data = {
            "boot_source_id": boot_source.id,
            "kind": BootAssetKind.BOOTLOADER,
            "label": BootAssetLabel.CANDIDATE,
        }
        resp = await user_client.post("/bootassets", json=data)
        assert resp.status_code == 422

    async def test_post_missing_boot_source(self, user_client: Client) -> None:
        data = {
            "boot_source_id": 999,
            "kind": BootAssetKind.BOOTLOADER,
            "label": BootAssetLabel.CANDIDATE,
            "os": "ubuntu",
            "release": "noble",
            "codename": "Noble Numbat",
            "title": "My Custom Image",
            "arch": "amd64",
            "subarch": "generic",
            "compatibility": ["generic"],
            "flavor": "generic",
            "base_image": "ubuntu",
            "eol": (now_utc() + timedelta(days=365)).isoformat(),
            "esm_eol": (now_utc() + timedelta(days=3650)).isoformat(),
        }
        resp = await user_client.post("/bootassets", json=data)
        assert resp.status_code == 404

    async def test_post_conflict(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
    ) -> None:
        await factory.make_BootAsset(
            boot_source.id,
            kind=BootAssetKind.OS,
            label=BootAssetLabel.CANDIDATE,
            os="ubuntu",
            release="noble",
            codename="Noble Numbat",
            title="Ubuntu Noble",
            arch="amd64",
            subarch="generic",
            compatibility=["generic", "hwe-p"],
            flavor="generic",
            eol=now_utc() + timedelta(days=365),
            esm_eol=now_utc() + timedelta(days=3650),
        )
        data = {
            "boot_source_id": boot_source.id,
            "kind": BootAssetKind.BOOTLOADER,
            "label": BootAssetLabel.STABLE,
            "os": "ubuntu",
            "release": "noble",
            "codename": "NobleNumbat",
            "title": "Another Noble Image",
            "arch": "amd64",
            "subarch": "generic",
            "compatibility": ["generic"],
            "flavor": "highbank",
            "base_image": "ubuntu",
            "eol": (now_utc() + timedelta(days=366)).isoformat(),
            "esm_eol": (now_utc() + timedelta(days=3660)).isoformat(),
        }
        resp = await user_client.post("/bootassets", json=data)
        assert resp.status_code == 409


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
        sel_ubuntu_jammy: BootSourceSelection,
        sel_centos: BootSourceSelection,
    ) -> None:
        bs_id = sel_ubuntu_jammy.boot_source_id
        selections = await user_client.get(
            f"/bootasset-sources/{bs_id}/selections"
        )
        assert selections.status_code == 200
        resp_body = selections.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 1
        assert resp_body["items"] == [sel_ubuntu_jammy.model_dump(mode="json")]

    async def test_get_with_sorting(
        self,
        user_client: Client,
        sel_ubuntu_jammy: BootSourceSelection,
        sel_ubuntu_noble: BootSourceSelection,
    ) -> None:
        bs_id = sel_ubuntu_jammy.boot_source_id
        assets = await user_client.get(
            f"/bootasset-sources/{bs_id}/selections?sort_by=release"
        )
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            sel_ubuntu_jammy.model_dump(mode="json"),
            sel_ubuntu_noble.model_dump(mode="json"),
        ]
        assets = await user_client.get(
            f"/bootasset-sources/{bs_id}/selections?sort_by=available"
        )
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            sel_ubuntu_noble.model_dump(mode="json"),
            sel_ubuntu_jammy.model_dump(mode="json"),
        ]

    async def test_get_with_page_and_size(
        self,
        user_client: Client,
        sel_ubuntu_jammy: BootSourceSelection,
        sel_ubuntu_noble: BootSourceSelection,
    ) -> None:
        bs_id = sel_ubuntu_jammy.boot_source_id

        resp = await user_client.get(
            f"/bootasset-sources/{bs_id}/selections?page=2&size=1&sort_by=release"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 1
        assert len(resp_body["items"]) == 1
        assert resp_body["items"][0]["release"] == sel_ubuntu_noble.release

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
        sel_ubuntu_noble: BootSourceSelection,
    ) -> None:
        # update the existing one
        up_sel = {
            "os": sel_ubuntu_noble.os,
            "release": sel_ubuntu_noble.release,
            "label": sel_ubuntu_noble.label,
            "arches": ["amd64", "arm64"],
        }
        new_sel = {
            "os": "centos",
            "release": "stream9",
            "label": "candidate",
            "arches": ["amd64"],
        }
        put_data = {"available": [up_sel, new_sel]}
        resp = await user_client.put(
            f"/bootasset-sources/{boot_source.id}/available-selections",
            json=put_data,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "stale" in data
        # The original selection should be updated, and a new one added
        stored = await factory.get("boot_source_selection")
        assert len(stored) == 2
        assert stored[0]["os"] == up_sel["os"]
        assert stored[0]["available"] == up_sel["arches"]
        assert stored[1]["os"] == new_sel["os"]
        assert stored[1]["available"] == new_sel["arches"]

    async def test_put_removes_stale_selections(
        self,
        user_client: Client,
        boot_source: BootSource,
        sel_ubuntu_noble: BootSourceSelection,
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
        assert any(s["id"] == sel_ubuntu_noble.id for s in data["stale"])

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
class TestBootAssetVersionsGetHandler:
    async def test_get(
        self,
        user_client: Client,
        ver_ubuntu_noble_1: BootAssetVersion,
        ver_ubuntu_noble_2: BootAssetVersion,
    ) -> None:
        resp = await user_client.get(f"/bootasset-versions")
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 2
        assert resp_body["items"] == [
            ver_ubuntu_noble_1.model_dump(mode="json"),
            ver_ubuntu_noble_2.model_dump(mode="json"),
        ]

    @pytest.mark.parametrize(
        "filter_param",
        [
            ("boot_asset_id"),
            ("version"),
        ],
    )
    async def test_get_with_filters(
        self,
        user_client: Client,
        ver_ubuntu_noble_1: BootAssetVersion,
        ver_ubuntu_jammy_1: BootAssetVersion,
        filter_param: str,
    ) -> None:
        resp = await user_client.get(
            f"/bootasset-versions?{filter_param}={ver_ubuntu_noble_1.model_dump()[filter_param]}"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert len(resp_body["items"]) == 1
        assert resp_body["items"][0] == ver_ubuntu_noble_1.model_dump(
            mode="json"
        )

    async def test_get_with_sorting(
        self,
        user_client: Client,
        ver_ubuntu_noble_2: BootAssetVersion,
        ver_ubuntu_noble_2_reloaded: BootAssetVersion,
    ) -> None:
        resp = await user_client.get(f"/bootasset-versions?sort_by=version")
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["items"] == [
            ver_ubuntu_noble_2.model_dump(mode="json"),
            ver_ubuntu_noble_2_reloaded.model_dump(mode="json"),
        ]

        resp = await user_client.get(
            f"/bootasset-versions?sort_by=version-desc"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["items"] == [
            ver_ubuntu_noble_2_reloaded.model_dump(mode="json"),
            ver_ubuntu_noble_2.model_dump(mode="json"),
        ]

    async def test_get_with_page_and_size(
        self,
        user_client: Client,
        ver_ubuntu_noble_1: BootAssetVersion,
        ver_ubuntu_noble_2: BootAssetVersion,
        ver_ubuntu_noble_2_reloaded: BootAssetVersion,
    ) -> None:
        resp = await user_client.get(
            f"/bootasset-versions?page=2&size=2&sort_by=version"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 1
        assert (
            resp_body["items"][0]["version"]
            == ver_ubuntu_noble_2_reloaded.version
        )

    @pytest.mark.parametrize(
        "sort_by", ["id", "version,version", "not_a_field"]
    )
    async def test_invalid_sort_params(
        self, user_client: Client, sort_by: str
    ) -> None:
        resp = await user_client.get(f"/bootasset-versions?sort_by={sort_by}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, page: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-versions?page={page}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, size: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-versions?size={size}")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootAssetVersionsPostHandler:
    async def test_post(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        ubuntu_noble: BootAsset,
    ) -> None:
        mock_now = mocker.patch(
            "msm.api.user.handlers.bootassets.now_utc",
            return_value=factory.now,
        )
        data = {
            "version": "20250302.1",
        }
        resp = await user_client.post(
            f"/bootassets/{ubuntu_noble.id}/versions", json=data
        )
        new_id = resp.json()["id"]
        assert resp.status_code == 200
        stored = await factory.get("boot_asset_version")
        assert len(stored) == 1
        assert stored[0] == data | {
            "id": new_id,
            "boot_asset_id": ubuntu_noble.id,
            "last_seen": factory.now,
        }

    async def test_post_missing_details(
        self,
        user_client: Client,
        ubuntu_noble: BootAsset,
    ) -> None:
        resp = await user_client.post(
            f"/bootassets/{ubuntu_noble.id}/versions",
        )
        assert resp.status_code == 422

    async def test_post_missing_boot_source(self, user_client: Client) -> None:
        data = {
            "version": "20250302.1",
        }
        resp = await user_client.post(f"/bootassets/{999}/versions", json=data)
        assert resp.status_code == 404

    async def test_post_conflict(
        self,
        user_client: Client,
        ubuntu_noble: BootAsset,
        ver_ubuntu_noble_1: BootAssetVersion,
    ) -> None:
        resp = await user_client.post(
            f"bootassets/{ubuntu_noble.id}/versions",
            json={"version": ver_ubuntu_noble_1.version},
        )
        assert resp.status_code == 409


@pytest.mark.asyncio
class TestBootAssetItemsGetHandler:
    async def test_get(
        self, user_client: Client, items_ubuntu_noble_1: list[BootAssetItem]
    ) -> None:
        resp = await user_client.get("/bootasset-items")
        assert resp.status_code == 200
        resp_data = resp.json()
        assert len(resp_data["items"]) == 3
        assert resp_data["items"] == [
            i.model_dump() for i in items_ubuntu_noble_1
        ]

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
        user_client: Client,
        items_ubuntu_noble_1: list[BootAssetItem],
        filter_param: str,
    ) -> None:
        bi = items_ubuntu_noble_1[0]
        resp = await user_client.get(
            "/bootasset-items",
            params=f"{filter_param}={bi.model_dump(mode="json")[filter_param]}",
        )

        assert resp.status_code == 200
        resp_data = resp.json()
        assert len(resp_data["items"]) >= 1
        assert resp_data["items"][0] == bi.model_dump(mode="json")

    @pytest.mark.parametrize(
        "sort_param,first",
        [
            ("ftype", 2),
            ("sha256", 1),
            ("path", 2),
            ("file_size", 2),
            ("source_package", 0),
            ("source_version", 0),
            ("source_release", 0),
            ("bytes_synced", 2),
        ],
    )
    async def test_get_with_sorting(
        self,
        user_client: Client,
        items_ubuntu_noble_1: list[BootAssetItem],
        sort_param: str,
        first: int,
    ) -> None:
        resp = await user_client.get(
            f"/bootasset-items?sort_by={sort_param}-desc"
        )

        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["items"][0] == items_ubuntu_noble_1[first].model_dump(
            mode="json"
        )

    async def test_get_with_page_and_size(
        self,
        user_client: Client,
        items_ubuntu_noble_1: list[BootAssetItem],
    ) -> None:
        resp = await user_client.get(
            "/bootasset-items?page=2&size=2&sort_by=path"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 1
        assert resp_body["items"][0]["path"] == items_ubuntu_noble_1[2].path

    @pytest.mark.parametrize("sort_by", ["id", "kind,kind", "not_a_field"])
    async def test_invalid_sort_params(
        self, user_client: Client, sort_by: str
    ) -> None:
        resp = await user_client.get(f"/bootasset-items?sort_by={sort_by}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, page: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-items?page={page}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, size: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-items?size={size}")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootAssetItemsPostHandler:
    async def test_post(
        self,
        user_client: Client,
        factory: Factory,
        ver_ubuntu_noble_1: BootAssetVersion,
    ) -> None:
        data = {
            "ftype": ItemFileType.ARCHIVE_TAR_XZ,
            "sha256": "testblaksjdflkj",
            "path": "/item",
            "file_size": 2321345623,
            "source_package": "ubukernel",
            "source_version": "23.4.1",
            "source_release": "noble",
        }
        resp = await user_client.post(
            f"/bootasset-versions/{ver_ubuntu_noble_1.id}/items", json=data
        )
        assert resp.status_code == 200
        new_id = resp.json()["id"]
        stored = await factory.get("boot_asset_item")
        assert len(stored) == 1
        assert stored[0] == data | {
            "id": new_id,
            "boot_asset_version_id": ver_ubuntu_noble_1.id,
            "bytes_synced": 0,
        }

    async def test_post_missing_details(
        self,
        user_client: Client,
        ver_ubuntu_noble_1: BootAssetVersion,
    ) -> None:
        data = {
            "sha256": "testblaksjdflkj",
            "path": "/item",
            "file_size": 2321345623,
            "source_package": "ubukernel",
            "source_version": "23.4.1",
            "source_release": "noble",
        }
        resp = await user_client.post(
            f"/bootasset-versions/{ver_ubuntu_noble_1.id}/items", json=data
        )
        assert resp.status_code == 422

    async def test_post_missing_boot_asset_version(
        self, user_client: Client
    ) -> None:
        data = {
            "ftype": ItemFileType.ARCHIVE_TAR_XZ,
            "sha256": "testblaksjdflkj",
            "path": "/item",
            "file_size": 2321345623,
            "source_package": "ubukernel",
            "source_version": "23.4.1",
            "source_release": "noble",
        }
        resp = await user_client.post(
            f"/bootasset-versions/{999}/items", json=data
        )
        assert resp.status_code == 404

    async def test_post_conflict(
        self,
        user_client: Client,
        ver_ubuntu_noble_1: BootAssetVersion,
        items_ubuntu_noble_1: list[BootAssetItem],
    ) -> None:
        item = items_ubuntu_noble_1[0]
        data = {
            "ftype": item.ftype,
            "sha256": "testblaksjdflkj",
            "path": item.path,
            "file_size": 2321345623,
            "source_package": "ubukernel",
            "source_version": "23.4.1",
            "source_release": "noble",
        }
        resp = await user_client.post(
            f"/bootasset-versions/{ver_ubuntu_noble_1.id}/items", json=data
        )
        assert resp.status_code == 409


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
class TestBootAssetItemsDeleteHandler:
    @pytest.fixture(autouse=True)
    def s3_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        monkeypatch.setenv("MSM_S3_PATH", "test/path")

    async def test_delete(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        items_ubuntu_noble_2: list[BootAssetItem],
    ) -> None:
        mock_resource = mocker.patch(
            "msm.api.user.handlers.bootassets.boto3.resource"
        )
        mock_delete = mocker.patch(
            "msm.api.user.handlers.bootassets.run_in_threadpool"
        )
        bi = items_ubuntu_noble_2[0]
        resp = await user_client.delete(f"/bootasset-items/{bi.id}")
        assert resp.status_code == 200
        stored = await factory.get("boot_asset_item")
        assert len(stored) == len(items_ubuntu_noble_2) - 1
        mock_resource.assert_called_with(
            "s3",
            use_ssl=False,
            verify=False,
            endpoint_url="test-endpoint",
            aws_access_key_id="test-access-key",
            aws_secret_access_key="test-secret-key",
        )
        mock_delete.assert_called_with(
            mocker.ANY, Bucket="test-bucket", Key=str(bi.id)
        )

    async def test_delete_doesnt_exist(
        self,
        user_client: Client,
    ) -> None:
        resp = await user_client.delete(f"/bootasset-items/999")
        assert resp.status_code == 404

    async def test_delete_purges(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        ubuntu_noble: BootAsset,
        ver_ubuntu_noble_2: BootAssetVersion,
        items_ubuntu_noble_2: list[BootAssetItem],
    ) -> None:
        mock_resource = mocker.patch(
            "msm.api.user.handlers.bootassets.boto3.resource"
        )
        mock_delete = mocker.patch(
            "msm.api.user.handlers.bootassets.run_in_threadpool"
        )

        while items_ubuntu_noble_2:
            bi = items_ubuntu_noble_2.pop()
            resp = await user_client.delete(f"/bootasset-items/{bi.id}")
            assert resp.status_code == 200
            items = await factory.get("boot_asset_item")
            assert len(items) == len(items_ubuntu_noble_2)

            # cascade only after all items were removed
            versions = await factory.get("boot_asset_version")
            assert len(versions) == (1 if items_ubuntu_noble_2 else 0)
            assets = await factory.get("boot_asset")
            assert len(assets) == (1 if items_ubuntu_noble_2 else 0)

            mock_resource.assert_called_with(
                "s3",
                use_ssl=False,
                verify=False,
                endpoint_url="test-endpoint",
                aws_access_key_id="test-access-key",
                aws_secret_access_key="test-secret-key",
            )
            mock_resource.reset_mock()
            mock_delete.assert_called_with(
                mocker.ANY, Bucket="test-bucket", Key=str(bi.id)
            )
            mock_delete.reset_mock()


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
