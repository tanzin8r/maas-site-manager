from datetime import timedelta
import json

import pytest

from msm.db.models import (
    BootAssetKind,
    BootAssetLabel,
)
from msm.time import now_utc
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestBootAssetsGetHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        boot_source = await factory.make_BootSource()
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
            eol=now_utc() + timedelta(days=3650),
            esm_eol=now_utc() + timedelta(days=7000),
        )
        assets = await user_client.get("/bootassets")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 1
        resp_body["items"][0]["id"] = boot_asset.id

        # dumping to JSON then loading back to a dict converts types like datetime
        # to string representations, which are returned by the API
        assert resp_body["items"] == [json.loads(boot_asset.model_dump_json())]

    async def test_get_with_sorting(
        self, user_client: Client, factory: Factory
    ) -> None:
        boot_source = await factory.make_BootSource()
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
            json.loads(boot_asset1.model_dump_json()),
            json.loads(boot_asset2.model_dump_json()),
        ]
        assets = await user_client.get("/bootassets?sort_by=release")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            json.loads(boot_asset2.model_dump_json()),
            json.loads(boot_asset1.model_dump_json()),
        ]

    async def test_get_with_page_and_size(
        self, user_client: Client, factory: Factory
    ) -> None:
        bs = await factory.make_BootSource()
        for i in range(4):
            await factory.make_BootAsset(bs.id, title=f"{i+1}")

        resp = await user_client.get("/bootassets?page=2&size=2&sort_by=title")
        assert resp.status_code == 200
        resp_body = resp.json()
        assert resp_body["page"] == 2
        assert resp_body["size"] == 2
        assert len(resp_body["items"]) == 2
        assert resp_body["items"][0]["title"] == "3"
        assert resp_body["items"][1]["title"] == "4"

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
class TestBootSourcesGetHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        boot_source = await factory.make_BootSource(
            priority=2,
            url="http://test.url",
            keyring="test_keyring",
            sync_interval=4200,
        )
        sources = await user_client.get("/bootasset-sources")
        assert sources.status_code == 200
        resp_body = sources.json()
        assert resp_body["page"] == 1
        assert resp_body["size"] == 20
        assert resp_body["total"] == 1
        assert resp_body["items"] == [boot_source.model_dump()]

    async def test_get_with_sorting(
        self, user_client: Client, factory: Factory
    ) -> None:
        boot_source1 = await factory.make_BootSource(url="a", keyring="b")
        boot_source2 = await factory.make_BootSource(url="b", keyring="a")
        assets = await user_client.get("/bootasset-sources?sort_by=url")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            json.loads(boot_source1.model_dump_json()),
            json.loads(boot_source2.model_dump_json()),
        ]
        assets = await user_client.get("/bootasset-sources?sort_by=keyring")
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            json.loads(boot_source2.model_dump_json()),
            json.loads(boot_source1.model_dump_json()),
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
class TestBootSourceSelectionsGetHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        boot_source = await factory.make_BootSource()
        boot_source2 = await factory.make_BootSource()
        selection = await factory.make_BootSourceSelection(
            boot_source.id,
            label=BootAssetLabel.CANDIDATE,
            os="test_os",
            release="test_release",
            arches=["test", "arches"],
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
        assert resp_body["items"] == [selection.model_dump()]

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
            json.loads(selection1.model_dump_json()),
            json.loads(selection2.model_dump_json()),
        ]
        assets = await user_client.get(
            f"/bootasset-sources/{boot_source.id}/selections?sort_by=release"
        )
        assert assets.status_code == 200
        resp_body = assets.json()
        assert resp_body["items"] == [
            json.loads(selection2.model_dump_json()),
            json.loads(selection1.model_dump_json()),
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
