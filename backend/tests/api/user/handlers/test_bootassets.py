from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from msm.api.user.handlers.bootassets import purge_and_refresh
from msm.db.models import (
    BootAssetKind,
    BootAssetLabel,
    BootSource,
    BootSourceSelection,
    ItemFileType,
)
from msm.jwt import TokenAudience, TokenPurpose
from msm.time import now_utc
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestBootAssetsGetHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        boot_source = await factory.make_BootSource(name="Test Source")
        boot_asset = await factory.make_BootAsset(
            boot_source_id=boot_source.id,
            kind=BootAssetKind.BOOTLOADER,
            label=BootAssetLabel.CANDIDATE,
            os="test_os",
            release="test_release",
            codename="test_codename",
            title="test title",
            arch="test_arch",
            subarch="test_subarch",
            compatibility=["test", "compatibility"],
            flavor="test_flavor",
            base_image="test_base_image",
            bootloader_type="test_bootloader",
            eol=now_utc() + timedelta(days=3650),
            esm_eol=now_utc() + timedelta(days=7000),
            signed=True,
        )
        assets = await user_client.get("/bootassets")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 1
        resp_body["items"][0]["id"] = boot_asset.id
        assert resp_body["items"] == [
            boot_asset.model_dump(mode="json") | {"source_name": "Test Source"}
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
        self, user_client: Client, factory: Factory, filter_param: str
    ) -> None:
        bs = await factory.make_BootSource(name="Test Source 1")
        bs2 = await factory.make_BootSource(name="Test Source 2")
        ba1 = await factory.make_BootAsset(
            bs.id,
            kind=BootAssetKind.OS,
            label=BootAssetLabel.STABLE,
            os="ubuntu",
            arch="amd64",
            release="plucky",
        )
        ba2 = await factory.make_BootAsset(
            bs2.id,
            kind=BootAssetKind.BOOTLOADER,
            label=BootAssetLabel.CANDIDATE,
            os="centos",
            arch="arm",
            release="uhh",
        )
        url = f"/bootassets?{filter_param}={ba1.model_dump(mode="json")[filter_param]}"
        resp = await user_client.get(url)
        assert resp.status_code == 200
        resp_body = resp.json()
        assert len(resp_body["items"]) == 1
        assert resp_body["items"][0] == ba1.model_dump(mode="json") | {
            "source_name": "Test Source 1"
        }

    async def test_get_with_sorting(
        self, user_client: Client, factory: Factory
    ) -> None:
        boot_source = await factory.make_BootSource(name="Test Source")
        boot_asset1 = await factory.make_BootAsset(
            boot_source_id=boot_source.id, os="a", release="b"
        )
        boot_asset2 = await factory.make_BootAsset(
            boot_source_id=boot_source.id, os="b", release="a"
        )
        assets = await user_client.get("/bootassets?sort_by=os")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            boot_asset1.model_dump(mode="json")
            | {"source_name": "Test Source"},
            boot_asset2.model_dump(mode="json")
            | {"source_name": "Test Source"},
        ]
        assets = await user_client.get("/bootassets?sort_by=release")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            boot_asset2.model_dump(mode="json")
            | {"source_name": "Test Source"},
            boot_asset1.model_dump(mode="json")
            | {"source_name": "Test Source"},
        ]

    async def test_get_with_page_and_size(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        for i in range(4):
            await factory.make_BootAsset(bs.id, os=f"{i+1}")

        resp = await user_client.get("/bootassets?page=2&size=2&sort_by=os")
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 2
        assert resp_body["items"][0]["os"] == "3"
        assert resp_body["items"][1]["os"] == "4"

    @pytest.mark.parametrize("sort_by", ["id", "kind,kind", "not_a_field"])
    async def test_invalid_sort_params(
        self, user_client: Client, factory: Factory, sort_by: str
    ) -> None:
        resp = await user_client.get(f"/bootassets?sort_by={sort_by}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, factory: Factory, page: int
    ) -> None:
        resp = await user_client.get(f"/bootassets?page={page}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, factory: Factory, size: int
    ) -> None:
        resp = await user_client.get(f"/bootassets?size={size}")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootAssetsPostHandler:
    async def test_post(self, user_client: Client, factory: Factory) -> None:
        boot_source = await factory.make_BootSource()
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
        self, user_client: Client, factory: Factory
    ) -> None:
        boot_source = await factory.make_BootSource()
        data = {
            "boot_source_id": boot_source.id,
            "kind": BootAssetKind.BOOTLOADER,
            "label": BootAssetLabel.CANDIDATE,
        }
        resp = await user_client.post("/bootassets", json=data)
        assert resp.status_code == 422

    async def test_post_missing_boot_source(
        self, user_client: Client, factory: Factory
    ) -> None:
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
    ) -> None:
        bs = await factory.make_BootSource()
        await factory.make_BootAsset(
            bs.id,
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
            "boot_source_id": bs.id,
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
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        boot_source = await factory.make_BootSource(
            priority=2,
            url="http://test.url",
            keyring="test_keyring",
            sync_interval=4200,
            name="Test Source",
        )
        sources = await user_client.get("/bootasset-sources")
        assert sources.status_code == 200
        resp_body = sources.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 1
        assert resp_body["items"] == [boot_source.model_dump(mode="json")]

    async def test_get_by_id(
        self, user_client: Client, factory: Factory
    ) -> None:
        boot_source = await factory.make_BootSource(
            priority=2,
            url="http://test.url",
            keyring="test_keyring",
            sync_interval=4200,
            name="Test Source",
        )
        resp = await user_client.get(f"/bootasset-sources/{boot_source.id}")
        assert resp.status_code == 200
        source = BootSource(**resp.json())
        assert source == boot_source

    async def test_get_by_id_not_found(
        self, user_client: Client, factory: Factory
    ) -> None:
        resp = await user_client.get("/bootasset-sources/999")
        assert resp.status_code == 404

    async def test_get_with_sorting(
        self, user_client: Client, factory: Factory
    ) -> None:
        boot_source1 = await factory.make_BootSource(url="a", keyring="b")
        boot_source2 = await factory.make_BootSource(url="b", keyring="a")
        assets = await user_client.get("/bootasset-sources?sort_by=url")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            boot_source1.model_dump(mode="json"),
            boot_source2.model_dump(mode="json"),
        ]
        assets = await user_client.get("/bootasset-sources?sort_by=keyring")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            boot_source2.model_dump(mode="json"),
            boot_source1.model_dump(mode="json"),
        ]

    async def test_get_with_page_and_size(
        self, user_client: Client, factory: Factory
    ) -> None:
        for i in range(4):
            await factory.make_BootSource(priority=i + 1)

        resp = await user_client.get(
            "/bootasset-sources?page=2&size=2&sort_by=priority"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 2
        assert resp_body["items"][0]["priority"] == 3
        assert resp_body["items"][1]["priority"] == 4

    @pytest.mark.parametrize("sort_by", ["id", "kind,kind", "not_a_field"])
    async def test_invalid_sort_params(
        self, user_client: Client, factory: Factory, sort_by: str
    ) -> None:
        resp = await user_client.get(f"/bootasset-sources?sort_by={sort_by}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, factory: Factory, page: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-sources?page={page}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, factory: Factory, size: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-sources?size={size}")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootSourcesPostHandler:
    async def test_post(
        self,
        user_client: Client,
        factory: Factory,
        index_view: None,
        mocker: MockerFixture,
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
        assert len(stored) == 1
        assert stored[0] == data | {"id": new_id, "last_sync": factory.now}

    @pytest.mark.parametrize(
        "field", ["priority", "url", "keyring", "sync_interval", "name"]
    )
    async def test_post_missing_details(
        self,
        user_client: Client,
        factory: Factory,
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
        self, user_client: Client, factory: Factory, index_view: None
    ) -> None:
        # need to create custom boot source and edit second one
        await factory.make_BootSource()
        bs = await factory.make_BootSource(
            priority=1,
            url="http://test.url",
            keyring="test-keyring",
            sync_interval=100,
            name="Test Source",
        )
        data = {
            "priority": 2,
            "url": "http://another.url",
            "keyring": "another-keyring",
            "sync_interval": 200,
            "name": "Another Name",
        }
        resp = await user_client.patch(
            f"/bootasset-sources/{bs.id}", json=data
        )
        assert resp.status_code == 200
        assert (
            resp.json() == {"id": bs.id, "last_sync": factory.now_json} | data
        )
        sources = await factory.get("boot_source")
        assert len(sources) == 2
        assert sources[1] == {"id": bs.id, "last_sync": factory.now} | data

    async def test_update_custom_source_fails(
        self, user_client: Client, factory: Factory
    ) -> None:
        await factory.make_BootSource()
        resp = await user_client.patch(
            f"/bootasset-sources/1", json={"priority": 2}
        )
        assert resp.status_code == 422

    async def test_update_no_fields(
        self, user_client: Client, factory: Factory
    ) -> None:
        await factory.make_BootSource()
        bs = await factory.make_BootSource(
            priority=1,
            url="http://test.url",
            keyring="test-keyring",
            sync_interval=100,
            name="Test Source",
        )
        resp = await user_client.patch(f"/bootasset-sources/{bs.id}", json={})
        assert resp.status_code == 422

    async def test_update_extra_fields(
        self, user_client: Client, factory: Factory
    ) -> None:
        await factory.make_BootSource()
        bs = await factory.make_BootSource(
            priority=1,
            url="http://test.url",
            keyring="test-keyring",
            sync_interval=100,
            name="Test Source",
        )
        data = {
            "priority": 2,
            "url": "http://another.url",
            "keyring": "another-keyring",
            "sync_interval": 200,
            "name": "Another Source",
            "something": "extra",
        }
        resp = await user_client.patch(
            f"/bootasset-sources/{bs.id}", json=data
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
        index_view: None,
        mocker: MockerFixture,
    ) -> None:
        mock_background = mocker.patch(
            "msm.api.user.handlers.bootassets.BackgroundTasks.add_task",
        )
        # need to create custom boot source and delete second one
        await factory.make_BootSource()
        bs = await factory.make_BootSource()
        resp = await user_client.delete(f"/bootasset-sources/{bs.id}")
        assert resp.status_code == 200
        mock_background.assert_called_once_with(
            purge_and_refresh, mocker.ANY, bs.id
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
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        boot_source = await factory.make_BootSource()
        boot_source2 = await factory.make_BootSource()
        selection = await factory.make_BootSourceSelection(
            boot_source.id,
            label=BootAssetLabel.CANDIDATE,
            os="test_os",
            release="test_release",
            available=["test", "arches"],
            selected=["test", "arches"],
        )
        await factory.make_BootSourceSelection(boot_source2.id)
        selections = await user_client.get(
            f"/bootasset-sources/{boot_source.id}/selections"
        )
        assert selections.status_code == 200
        resp_body = selections.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 1
        assert resp_body["items"] == [selection.model_dump(mode="json")]

    async def test_get_with_sorting(
        self, user_client: Client, factory: Factory
    ) -> None:
        boot_source = await factory.make_BootSource()
        selection1 = await factory.make_BootSourceSelection(
            boot_source.id, os="a", release="b"
        )
        selection2 = await factory.make_BootSourceSelection(
            boot_source.id, os="b", release="a"
        )
        assets = await user_client.get(
            f"/bootasset-sources/{boot_source.id}/selections?sort_by=os"
        )
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            selection1.model_dump(mode="json"),
            selection2.model_dump(mode="json"),
        ]
        assets = await user_client.get(
            f"/bootasset-sources/{boot_source.id}/selections?sort_by=release"
        )
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            selection2.model_dump(mode="json"),
            selection1.model_dump(mode="json"),
        ]

    async def test_get_with_page_and_size(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        for i in range(4):
            await factory.make_BootSourceSelection(bs.id, release=f"{i+1}")

        resp = await user_client.get(
            f"/bootasset-sources/{bs.id}/selections?page=2&size=2&sort_by=release"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 2
        assert resp_body["items"][0]["release"] == "3"
        assert resp_body["items"][1]["release"] == "4"

    @pytest.mark.parametrize("sort_by", ["id", "kind,kind", "not_a_field"])
    async def test_invalid_sort_params(
        self, user_client: Client, factory: Factory, sort_by: str
    ) -> None:
        resp = await user_client.get(
            f"/bootasset-sources/1/selections?sort_by={sort_by}"
        )
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, factory: Factory, page: int
    ) -> None:
        resp = await user_client.get(
            f"/bootasset-sources/1/selections?page={page}"
        )
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, factory: Factory, size: int
    ) -> None:
        resp = await user_client.get(
            f"/bootasset-sources/1/selections?size={size}"
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootSourceAvailSelectionsPutHandler:
    @pytest.fixture
    async def boot_source(self, factory: Factory) -> BootSource:
        return await factory.make_BootSource()

    @pytest.fixture
    async def selection(
        self, factory: Factory, boot_source: BootSource
    ) -> BootSourceSelection:
        return await factory.make_BootSourceSelection(
            boot_source.id,
            label=BootAssetLabel.STABLE,
            os="ubuntu",
            release="noble",
            available=["amd64"],
            selected=["amd64"],
        )

    async def test_put_add_and_update_selections(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
        selection: BootSourceSelection,
        index_view: None,
    ) -> None:
        # Add a new selection and update the existing one
        up_sel = {
            "os": selection.os,
            "release": selection.release,
            "label": selection.label,
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
        selection: BootSourceSelection,
        index_view: None,
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
        assert any(s["id"] == selection.id for s in data["stale"])

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
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        bs = await factory.make_BootSource()
        boot_asset1 = await factory.make_BootAsset(bs.id)
        boot_asset2 = await factory.make_BootAsset(bs.id, os="os")
        v1 = await factory.make_BootAssetVersion(boot_asset1.id, version="1")
        v2 = await factory.make_BootAssetVersion(boot_asset2.id, version="2")
        resp = await user_client.get(f"/bootasset-versions")
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 2
        assert resp_body["items"] == [
            v1.model_dump(mode="json"),
            v2.model_dump(mode="json"),
        ]

    @pytest.mark.parametrize(
        "filter_param",
        [
            ("boot_asset_id"),
            ("version"),
        ],
    )
    async def test_get_with_filters(
        self, user_client: Client, factory: Factory, filter_param: str
    ) -> None:
        bs = await factory.make_BootSource()
        boot_asset1 = await factory.make_BootAsset(bs.id)
        boot_asset2 = await factory.make_BootAsset(bs.id, os="os")
        v1 = await factory.make_BootAssetVersion(boot_asset1.id, version="1")
        await factory.make_BootAssetVersion(boot_asset2.id, version="2")
        resp = await user_client.get(
            f"/bootasset-versions?{filter_param}={v1.model_dump()[filter_param]}"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert len(resp_body["items"]) == 1
        assert resp_body["items"][0] == v1.model_dump(mode="json")

    async def test_get_with_sorting(
        self, user_client: Client, factory: Factory
    ) -> None:
        boot_source = await factory.make_BootSource()
        ba = await factory.make_BootAsset(boot_source.id)
        v1 = await factory.make_BootAssetVersion(ba.id, version=("20221212"))
        v2 = await factory.make_BootAssetVersion(ba.id, version=("20211212"))

        resp = await user_client.get(f"/bootasset-versions?sort_by=version")
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["items"] == [
            v2.model_dump(mode="json"),
            v1.model_dump(mode="json"),
        ]

        resp = await user_client.get(
            f"/bootasset-versions?sort_by=version-desc"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["items"] == [
            v1.model_dump(mode="json"),
            v2.model_dump(mode="json"),
        ]

    async def test_get_with_page_and_size(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        for i in range(4):
            await factory.make_BootAssetVersion(ba.id, version=f"{i+1}")

        resp = await user_client.get(
            f"/bootasset-versions?page=2&size=2&sort_by=version"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 2
        assert resp_body["items"][0]["version"] == "3"
        assert resp_body["items"][1]["version"] == "4"

    @pytest.mark.parametrize(
        "sort_by", ["id", "version,version", "not_a_field"]
    )
    async def test_invalid_sort_params(
        self, user_client: Client, factory: Factory, sort_by: str
    ) -> None:
        resp = await user_client.get(f"/bootasset-versions?sort_by={sort_by}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, factory: Factory, page: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-versions?page={page}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, factory: Factory, size: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-versions?size={size}")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootAssetVersionsPostHandler:
    async def test_post(
        self, user_client: Client, factory: Factory, mocker: MockerFixture
    ) -> None:
        mock_now = mocker.patch(
            "msm.api.user.handlers.bootassets.now_utc",
            return_value=factory.now,
        )
        bs = await factory.make_BootSource()
        boot_asset = await factory.make_BootAsset(bs.id)
        data = {
            "version": "20250302.1",
        }
        resp = await user_client.post(
            f"/bootassets/{boot_asset.id}/versions", json=data
        )
        new_id = resp.json()["id"]
        assert resp.status_code == 200
        stored = await factory.get("boot_asset_version")
        assert len(stored) == 1
        assert stored[0] == data | {
            "id": new_id,
            "boot_asset_id": boot_asset.id,
            "last_seen": factory.now,
        }

    async def test_post_missing_details(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        boot_asset = await factory.make_BootAsset(bs.id)
        resp = await user_client.post(
            f"/bootassets/{boot_asset.id}/versions",
        )
        assert resp.status_code == 422

    async def test_post_missing_boot_source(
        self, user_client: Client, factory: Factory
    ) -> None:
        data = {
            "version": "20250302.1",
        }
        resp = await user_client.post(f"/bootassets/{999}/versions", json=data)
        assert resp.status_code == 404

    async def test_post_conflict(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        await factory.make_BootAssetVersion(ba.id, version="x")
        resp = await user_client.post(
            f"bootassets/{ba.id}/versions", json={"version": "x"}
        )
        assert resp.status_code == 409


@pytest.mark.asyncio
class TestBootAssetItemsGetHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        bi = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="sha256",
            path="test/path",
            file_size=1,
            bytes_synced=1,
            source_package="source_package",
            source_version="source_version",
            source_release="source_release",
        )
        resp = await user_client.get("/bootasset-items")
        assert resp.status_code == 200
        resp_data = resp.json()
        assert len(resp_data["items"]) == 1
        assert resp_data["items"] == [bi.model_dump()]

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
        self, user_client: Client, factory: Factory, filter_param: str
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        bv2 = await factory.make_BootAssetVersion(ba.id, version="x")
        bi = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="sha256",
            path="test/path",
            file_size=1,
            bytes_synced=1,
            source_package="source_package",
            source_version="source_version",
            source_release="source_release",
        )
        await factory.make_BootAssetItem(
            bv2.id,
            ftype=ItemFileType.BOOT_INITRD,
            sha256="3",
            path="somethingelse",
            file_size=2,
            bytes_synced=2,
            source_package="ee",
            source_version="aa",
            source_release="oo",
        )
        resp = await user_client.get(
            "/bootasset-items",
            params=f"{filter_param}={bi.model_dump(mode="json")[filter_param]}",
        )

        assert resp.status_code == 200
        resp_data = resp.json()
        assert len(resp_data["items"]) == 1
        assert resp_data["items"] == [bi.model_dump(mode="json")]

    @pytest.mark.parametrize(
        "sort_param",
        [
            ("ftype"),
            ("sha256"),
            ("path"),
            ("file_size"),
            ("source_package"),
            ("source_version"),
            ("source_release"),
            ("bytes_synced"),
        ],
    )
    async def test_get_with_sorting(
        self, user_client: Client, factory: Factory, sort_param: str
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        bi1 = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="a",
            path="a",
            file_size=1,
            bytes_synced=1,
            source_package="a",
            source_version="a",
            source_release="a",
        )
        bi2 = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.BOOT_INITRD,
            sha256="b",
            path="b",
            file_size=2,
            bytes_synced=2,
            source_package="b",
            source_version="b",
            source_release="b",
        )

        resp = await user_client.get(f"/bootasset-items?sort_by={sort_param}")

        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["items"] == [
            bi1.model_dump(mode="json"),
            bi2.model_dump(mode="json"),
        ]

    async def test_get_with_page_and_size(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        await factory.make_BootAssetItem(
            bv.id, ftype=ItemFileType.ARCHIVE_TAR_XZ, path="1"
        )
        await factory.make_BootAssetItem(
            bv.id, ftype=ItemFileType.BOOT_DTB, path="2"
        )
        await factory.make_BootAssetItem(
            bv.id, ftype=ItemFileType.BOOT_INITRD, path="3"
        )
        await factory.make_BootAssetItem(
            bv.id, ftype=ItemFileType.BOOT_KERNEL, path="4"
        )

        resp = await user_client.get(
            "/bootasset-items?page=2&size=2&sort_by=path"
        )
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 2
        assert resp_body["items"][0]["path"] == "3"
        assert resp_body["items"][1]["path"] == "4"

    @pytest.mark.parametrize("sort_by", ["id", "kind,kind", "not_a_field"])
    async def test_invalid_sort_params(
        self, user_client: Client, factory: Factory, sort_by: str
    ) -> None:
        resp = await user_client.get(f"/bootasset-items?sort_by={sort_by}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("page", [-1, 0])
    async def test_invalid_page_params(
        self, user_client: Client, factory: Factory, page: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-items?page={page}")
        assert resp.status_code == 422

    @pytest.mark.parametrize("size", [0, -1, 101])
    async def test_invalid_size_params(
        self, user_client: Client, factory: Factory, size: int
    ) -> None:
        resp = await user_client.get(f"/bootasset-items?size={size}")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestBootAssetItemsPostHandler:
    async def test_post(
        self, user_client: Client, factory: Factory, index_view: None
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        boot_asset_version = await factory.make_BootAssetVersion(ba.id)
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
            f"/bootasset-versions/{boot_asset_version.id}/items", json=data
        )
        assert resp.status_code == 200
        new_id = resp.json()["id"]
        stored = await factory.get("boot_asset_item")
        assert len(stored) == 1
        assert stored[0] == data | {
            "id": new_id,
            "boot_asset_version_id": boot_asset_version.id,
            "bytes_synced": 0,
        }

    async def test_post_missing_details(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        boot_asset_version = await factory.make_BootAssetVersion(ba.id)
        data = {
            "sha256": "testblaksjdflkj",
            "path": "/item",
            "file_size": 2321345623,
            "source_package": "ubukernel",
            "source_version": "23.4.1",
            "source_release": "noble",
        }
        resp = await user_client.post(
            f"/bootasset-versions/{boot_asset_version.id}/items", json=data
        )
        assert resp.status_code == 422

    async def test_post_missing_boot_asset_version(
        self, user_client: Client, factory: Factory
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
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        await factory.make_BootAssetItem(
            bv.id, ftype=ItemFileType.ARCHIVE_TAR_XZ, path="/item"
        )
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
            f"/bootasset-versions/{bv.id}/items", json=data
        )
        assert resp.status_code == 409


@pytest.mark.asyncio
class TestBootAssetItemsPatchHandler:
    async def test_patch(
        self, user_client: Client, factory: Factory, index_view: None
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        item = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="testsha1",
            path="testpath1",
            file_size=1,
            bytes_synced=1,
            source_package="testpackage1",
            source_version="testversion1",
            source_release="testrelease1",
        )
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
        assert len(stored) == 1
        assert stored[0] == data | {
            "id": item.id,
            "boot_asset_version_id": bv.id,
            "file_size": 1,
            "bytes_synced": 1,
            "sha256": "testsha1",
            "path": "testpath1",
        }

    async def test_patch_no_values(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        item = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="testsha1",
            path="testpath1",
            file_size=1,
            bytes_synced=1,
            source_package="testpackage1",
            source_version="testversion1",
            source_release="testrelease1",
        )
        resp = await user_client.patch(
            f"/bootasset-items/{item.id}",
        )
        assert resp.status_code == 422
        stored = await factory.get("boot_asset_item")
        assert len(stored) == 1
        assert stored[0] == item.model_dump()

    async def test_patch_extra_params(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        item = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="testsha1",
            path="testpath1",
            file_size=1,
            bytes_synced=1,
            source_package="testpackage1",
            source_version="testversion1",
            source_release="testrelease1",
        )
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
        assert len(stored) == 1
        assert stored[0] == item.model_dump()

    async def test_patch_bad_item_id(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        item = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="testsha1",
            path="testpath1",
            file_size=1,
            bytes_synced=1,
            source_package="testpackage1",
            source_version="testversion1",
            source_release="testrelease1",
        )
        data = {
            "ftype": ItemFileType.BOOT_DTB,
            "source_package": "testpackage2",
            "source_version": "testversion2",
            "source_release": "testrelease2",
        }
        resp = await user_client.patch(
            f"/bootasset-items/{item.id + 1}", json=data
        )
        assert resp.status_code == 404
        stored = await factory.get("boot_asset_item")
        assert len(stored) == 1
        assert stored[0] == item.model_dump()

    async def test_users_cannot_change_bytes_synced(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        item = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="testsha1",
            path="testpath1",
            file_size=1,
            bytes_synced=1,
            source_package="testpackage1",
            source_version="testversion1",
            source_release="testrelease1",
        )
        data = {"bytes_synced": 2}
        resp = await user_client.patch(
            f"/bootasset-items/{item.id}", json=data
        )
        assert resp.status_code == 403
        stored = await factory.get("boot_asset_item")
        assert stored[0]["bytes_synced"] == 1

    async def test_workers_can_change_bytes_synced(
        self, app_client: Client, factory: Factory, index_view: None
    ) -> None:
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        item = await factory.make_BootAssetItem(
            bv.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="testsha1",
            path="testpath1",
            file_size=1,
            bytes_synced=0,
            source_package="testpackage1",
            source_version="testversion1",
            source_release="testrelease1",
        )
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
        assert len(stored) == 1
        assert stored[0] == data | {
            "id": item.id,
            "boot_asset_version_id": bv.id,
            "ftype": ItemFileType.ARCHIVE_TAR_XZ,
            "sha256": "testsha1",
            "path": "testpath1",
            "file_size": 1,
            "source_package": "testpackage1",
            "source_version": "testversion1",
            "source_release": "testrelease1",
        }


@pytest.mark.asyncio
class TestBootAssetItemsDeleteHandler:
    async def test_delete(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        index_view: None,
    ) -> None:
        mock_resource = mocker.patch(
            "msm.api.user.handlers.bootassets.boto3.resource"
        )
        mock_delete = mocker.patch(
            "msm.api.user.handlers.bootassets.run_in_threadpool"
        )
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        bi = await factory.make_BootAssetItem(bv.id)
        resp = await user_client.delete(f"/bootasset-items/{bi.id}")
        assert resp.status_code == 200
        stored = await factory.get("boot_asset_item")
        assert len(stored) == 0
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
        self, user_client: Client, factory: Factory
    ) -> None:
        resp = await user_client.delete(f"/bootasset-items/999")
        assert resp.status_code == 404

    async def test_delete_purges(
        self,
        user_client: Client,
        factory: Factory,
        index_view: None,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_resource = mocker.patch(
            "msm.api.user.handlers.bootassets.boto3.resource"
        )
        mock_delete = mocker.patch(
            "msm.api.user.handlers.bootassets.run_in_threadpool"
        )
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        bi = await factory.make_BootAssetItem(bv.id)
        resp = await user_client.delete(f"/bootasset-items/{bi.id}")
        assert resp.status_code == 200
        items = await factory.get("boot_asset_item")
        assert len(items) == 0
        versions = await factory.get("boot_asset_version")
        assert len(versions) == 0
        assets = await factory.get("boot_asset")
        assert len(assets) == 0
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
