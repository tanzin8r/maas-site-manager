from hashlib import sha256
import json
from pathlib import Path
from typing import cast
from unittest.mock import ANY, call

import pytest
from pytest_mock import MockerFixture, MockType

from msm.apiserver.db.models import (
    BootAsset,
    BootAssetItem,
    BootSource,
    BootSourceSelection,
)
from msm.apiserver.service import S3Service
from msm.apiserver.service.images import END_OF_TIME
from msm.common.enums import ItemFileType
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.fixture(autouse=True)
def mock_now(mocker: MockerFixture, factory: Factory) -> MockType:
    return mocker.patch(
        "msm.apiserver.user.handlers.images.now_utc",
        return_value=factory.now,
    )


@pytest.fixture
def mock_s3_service(mocker: MockerFixture) -> MockType:
    mock_s3 = mocker.patch("msm.apiserver.service.S3Service", spec=S3Service)
    mock = mock_s3.return_value
    mock.create_multipart_upload.return_value = ("test-key", "test-upload-id")
    mock.upload_part.return_value = "test-etag"
    mock.complete_upload.return_value = None
    mock.abort_upload.return_value = None
    mock.delete_object.return_value = None
    mock.get_object.return_value = {"Body": [b"cadecafe"]}
    return cast(MockType, mock)


@pytest.mark.asyncio
class TestCustomImageUploadHandler:
    async def test_post(
        self,
        user_client: Client,
        factory: Factory,
        mock_s3_service: MockType,
        boot_source_custom: BootSource,
        tmp_path: Path,
    ) -> None:
        test_file_content = "This is a test file."
        data = {
            "os": "custom",
            "release": "noble",
            "arch": "amd64",
            "file_size": len(test_file_content),
            "title": "My Custom Image",
            "filename": "test.tgz",
        }
        test_file = tmp_path / "testfile"
        test_file.write_text(test_file_content)
        with test_file.open("rb") as f:
            file_data = {"file": f}
            resp = await user_client.post(
                "/images",
                data=data,
                files=file_data,
            )
            assert resp.status_code == 200
            mock_s3_service.create_multipart_upload.assert_called_once_with(
                "1"
            )
            mock_s3_service.upload_part.assert_called_once()
            mock_s3_service.complete_upload.assert_called_once()
            stored_assets = await factory.get("boot_asset")
            stored_versions = await factory.get("boot_asset_version")
            stored_items = await factory.get("boot_asset_item")
            assert len(stored_assets) == 1
            assert len(stored_versions) == 1
            assert len(stored_items) == 1
            expected_asset = {
                "id": 1,
                "boot_source_id": boot_source_custom.id,
                "kind": 0,
                "label": "stable",
                "os": "custom",
                "release": "noble",
                "arch": "amd64",
                "title": "My Custom Image",
                "codename": None,
                "subarch": None,
                "compatibility": None,
                "flavor": None,
                "base_image": "custom/noble",
                "bootloader_type": None,
                "eol": END_OF_TIME,
                "esm_eol": END_OF_TIME,
                "signed": False,
            }
            expected_version = {
                "id": 1,
                "boot_asset_id": stored_assets[0]["id"],
                "version": factory.now.strftime("%Y%m%d") + ".1",
                "last_seen": factory.now,
            }
            expected_item = {
                "id": resp.json()["id"],
                "boot_asset_version_id": stored_versions[0]["id"],
                "file_size": len(test_file_content),
                "sha256": sha256(test_file_content.encode()).hexdigest(),
                "ftype": ItemFileType.ROOT_TGZ,
                "bytes_synced": len(test_file_content),
                "path": f"noble/amd64/{stored_versions[0]['version']}/test.tgz",
                "source_package": None,
                "source_release": None,
                "source_version": None,
            }
            assert stored_assets[0] == expected_asset
            assert stored_versions[0] == expected_version
            assert stored_items[0] == expected_item

    async def test_post_duplicate_increments_revision(
        self,
        user_client: Client,
        factory: Factory,
        boot_source_custom: BootSource,
        mock_s3_service: MockType,
        tmp_path: Path,
    ) -> None:
        test_file_content = "This is a test file."
        data = {
            "os": "custom",
            "release": "noble",
            "arch": "amd64",
            "file_size": len(test_file_content),
            "title": "My Custom Image",
            "filename": "test.tgz",
        }
        test_file = tmp_path / "testfile"
        test_file.write_text(test_file_content)
        with test_file.open("rb") as f:
            file_data = {"file": f}
            resp = await user_client.post(
                "/images",
                data=data,
                files=file_data,
            )
            assert resp.status_code == 200
            first_item_id = resp.json()["id"]
            resp = await user_client.post(
                "/images",
                data=data,
                files=file_data,
            )
            assert resp.status_code == 200
            second_item_id = resp.json()["id"]
            mock_s3_service.create_multipart_upload.assert_has_calls(
                [call("1"), call("2")]
            )
            assert mock_s3_service.upload_part.call_count == 2
            assert mock_s3_service.complete_upload.call_count == 2
            stored_assets = await factory.get("boot_asset")
            stored_versions = await factory.get("boot_asset_version")
            stored_items = await factory.get("boot_asset_item")
            assert len(stored_assets) == 1
            assert len(stored_versions) == 2
            assert len(stored_items) == 2
            expected_asset = {
                "id": 1,
                "boot_source_id": boot_source_custom.id,
                "kind": 0,
                "label": "stable",
                "os": "custom",
                "release": "noble",
                "arch": "amd64",
                "title": "My Custom Image",
                "codename": None,
                "subarch": None,
                "compatibility": None,
                "flavor": None,
                "base_image": "custom/noble",
                "bootloader_type": None,
                "eol": END_OF_TIME,
                "esm_eol": END_OF_TIME,
                "signed": False,
            }
            expected_first_version = {
                "id": 1,
                "boot_asset_id": stored_assets[0]["id"],
                "version": factory.now.strftime("%Y%m%d") + ".1",
                "last_seen": factory.now,
            }
            expected_second_version = {
                "id": 2,
                "boot_asset_id": stored_assets[0]["id"],
                "version": factory.now.strftime("%Y%m%d") + ".2",
                "last_seen": factory.now,
            }
            expected_first_item = {
                "id": first_item_id,
                "boot_asset_version_id": stored_versions[0]["id"],
                "file_size": len(test_file_content),
                "sha256": sha256(test_file_content.encode()).hexdigest(),
                "ftype": ItemFileType.ROOT_TGZ,
                "bytes_synced": len(test_file_content),
                "path": f"noble/amd64/{stored_versions[0]['version']}/test.tgz",
                "source_package": None,
                "source_release": None,
                "source_version": None,
            }
            expected_second_item = {
                "id": second_item_id,
                "boot_asset_version_id": stored_versions[1]["id"],
                "file_size": len(test_file_content),
                "sha256": sha256(test_file_content.encode()).hexdigest(),
                "ftype": ItemFileType.ROOT_TGZ,
                "bytes_synced": len(test_file_content),
                "path": f"noble/amd64/{stored_versions[1]['version']}/test.tgz",
                "source_package": None,
                "source_release": None,
                "source_version": None,
            }
            assert stored_assets[0] == expected_asset
            assert stored_versions[0] == expected_first_version
            assert stored_versions[1] == expected_second_version
            assert stored_items[0] == expected_first_item
            assert stored_items[1] == expected_second_item

    async def test_post_wrong_file_size(
        self,
        user_client: Client,
        factory: Factory,
        boot_source_custom: BootSource,
        mock_s3_service: MockType,
        tmp_path: Path,
    ) -> None:
        test_file_content = "This is a test file."
        data = {
            "os": "custom",
            "release": "noble",
            "arch": "amd64",
            "file_size": len(test_file_content) + 1,
            "title": "My Custom Image",
            "filename": "test.tgz",
        }
        test_file = tmp_path / "testfile"
        test_file.write_text(test_file_content)
        with test_file.open("rb") as f:
            file_data = {"file": f}
            resp = await user_client.post(
                "/images",
                data=data,
                files=file_data,
            )
            assert resp.status_code == 400
            assert (
                json.loads(resp.text)["error"]["message"]
                == "The size of the uploaded file does not match the 'file_size' parameter in the request"
            )
            stored_assets = await factory.get("boot_asset")
            assert len(stored_assets) == 0
            stored_versions = await factory.get("boot_asset_version")
            assert len(stored_versions) == 0
            stored_images = await factory.get("boot_asset_item")
            assert len(stored_images) == 0

    async def test_post_bad_parameters(
        self,
        user_client: Client,
        factory: Factory,
        boot_source_custom: BootSource,
        mock_s3_service: MockType,
        tmp_path: Path,
    ) -> None:
        test_file_content = "This is a test file."
        data = {
            "os": "custom",
            "release": "noble",
            "arch": "amd64",
            "file_size": "this should have been an integer",
            "title": "My Custom Image",
            "filename": "test.tgz",
        }
        test_file = tmp_path / "testfile"
        test_file.write_text(test_file_content)
        with test_file.open("rb") as f:
            file_data = {"file": f}
            resp = await user_client.post(
                "/images",
                data=data,
                files=file_data,
            )
            assert resp.status_code == 400
            assert (
                json.loads(resp.text)["error"]["message"]
                == "Invalid type for file_size, expected <class 'int'>"
            )
            stored_assets = await factory.get("boot_asset")
            assert len(stored_assets) == 0
            stored_versions = await factory.get("boot_asset_version")
            assert len(stored_versions) == 0
            stored_images = await factory.get("boot_asset_item")
            assert len(stored_images) == 0

    async def test_post_bad_filetype(
        self,
        user_client: Client,
        factory: Factory,
        boot_source_custom: BootSource,
        mock_s3_service: MockType,
        tmp_path: Path,
    ) -> None:
        test_file_content = "This is a test file."
        data = {
            "os": "custom",
            "release": "noble",
            "arch": "amd64",
            "file_size": len(test_file_content),
            "title": "My Custom Image",
            "filename": "test.badext",
        }
        test_file = tmp_path / "testfile"
        test_file.write_text(test_file_content)
        with test_file.open("rb") as f:
            file_data = {"file": f}
            resp = await user_client.post(
                "/images",
                data=data,
                files=file_data,
            )
            assert resp.status_code == 400
            assert (
                json.loads(resp.text)["error"]["message"]
                == "Unsupported file type"
            )
            stored_assets = await factory.get("boot_asset")
            assert len(stored_assets) == 0
            stored_versions = await factory.get("boot_asset_version")
            assert len(stored_versions) == 0
            stored_images = await factory.get("boot_asset_item")
            assert len(stored_images) == 0

    async def test_post_ubuntu_os(
        self,
        user_client: Client,
        factory: Factory,
        boot_source_custom: BootSource,
        mock_s3_service: MockType,
        tmp_path: Path,
    ) -> None:
        test_file_content = "This is a test file."
        data = {
            "os": "ubuntu",
            "release": "noble",
            "arch": "amd64",
            "file_size": len(test_file_content),
            "title": "My Custom Image",
            "filename": "test.tgz",
        }
        test_file = tmp_path / "testfile"
        test_file.write_text(test_file_content)
        with test_file.open("rb") as f:
            file_data = {"file": f}
            resp = await user_client.post(
                "/images",
                data=data,
                files=file_data,
            )
            assert resp.status_code == 400
            assert (
                json.loads(resp.text)["error"]["message"]
                == "Invalid value for os: ubuntu"
            )
            stored_assets = await factory.get("boot_asset")
            assert len(stored_assets) == 0
            stored_versions = await factory.get("boot_asset_version")
            assert len(stored_versions) == 0
            stored_images = await factory.get("boot_asset_item")
            assert len(stored_images) == 0


@pytest.mark.asyncio
class TestCustomImageDeleteHandler:
    async def test_delete(
        self,
        user_client: Client,
        boot_source_custom: BootSource,
        factory: Factory,
        mocker: MockerFixture,
    ) -> None:
        mock_start_wf = mocker.patch(
            "msm.apiserver.middleware.S3Middleware.start_delete_workflow",
        )
        asset = await factory.make_BootAsset(
            boot_source_custom.id,
            os="custom",
            release="noble",
            arch="amd64",
            base_image="custom/noble",
        )
        version = await factory.make_BootAssetVersion(asset.id)
        item = await factory.make_BootAssetItem(version.id)
        resp = await user_client.post(
            "/images:remove", json={"asset_ids": [asset.id]}
        )
        assert resp.status_code == 204
        assets = await factory.get("boot_asset")
        versions = await factory.get("boot_asset_version")
        items = await factory.get("boot_asset_item")
        assert len(assets) == 0
        assert len(versions) == 0
        assert len(items) == 0
        mock_start_wf.assert_called_once_with(ANY, [item.id])

    async def test_delete_non_custom(
        self,
        user_client: Client,
        ubuntu_noble: BootAsset,
        items_ubuntu_noble_1: list[BootAssetItem],
        factory: Factory,
    ) -> None:
        resp = await user_client.post(
            "/images:remove", json={"asset_ids": [ubuntu_noble.id]}
        )
        assert resp.status_code == 403

    async def test_delete_not_found(
        self,
        user_client: Client,
    ) -> None:
        resp = await user_client.post(
            "/images:remove", json={"asset_ids": [999]}
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestGetSelectableImagesHandler:
    async def test_get_selectable_images(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
        boot_source_low: BootSource,
    ) -> None:
        await factory.make_BootSourceSelection(
            boot_source_low.id,
            os="ubuntu",
            release="noble",
            arch="amd64",
            selected=False,
        )
        await factory.make_BootSourceSelection(
            boot_source_low.id,
            os="ubuntu",
            release="noble",
            arch="arm64",
            selected=True,
        )
        noble_ppc_sel_low = await factory.make_BootSourceSelection(
            boot_source_low.id,
            os="ubuntu",
            release="noble",
            arch="ppc64el",
            selected=False,
        )
        noble_arm_sel_high = await factory.make_BootSourceSelection(
            boot_source.id,
            os="ubuntu",
            release="noble",
            arch="arm64",
            selected=False,
        )
        await factory.make_BootSourceSelection(
            boot_source.id,
            os="ubuntu",
            release="noble",
            arch="amd64",
            selected=True,
        )
        jammy_amd_sel_high = await factory.make_BootSourceSelection(
            boot_source.id,
            os="ubuntu",
            release="jammy",
            arch="amd64",
            selected=False,
        )
        jammy_arm_sel_high = await factory.make_BootSourceSelection(
            boot_source.id,
            os="ubuntu",
            release="jammy",
            arch="arm64",
            selected=False,
        )
        resp = await user_client.get("/selectable-images")
        assert resp.status_code == 200
        data = resp.json()
        expected = {
            "items": [
                {
                    "selection_id": jammy_amd_sel_high.id,
                    "os": "ubuntu",
                    "release": "jammy",
                    "arch": "amd64",
                    "boot_source_id": boot_source.id,
                    "boot_source_name": boot_source.name,
                    "boot_source_url": boot_source.url,
                },
                {
                    "selection_id": jammy_arm_sel_high.id,
                    "os": "ubuntu",
                    "release": "jammy",
                    "arch": "arm64",
                    "boot_source_id": boot_source.id,
                    "boot_source_name": boot_source.name,
                    "boot_source_url": boot_source.url,
                },
                {
                    "selection_id": noble_ppc_sel_low.id,
                    "os": "ubuntu",
                    "release": "noble",
                    "arch": "ppc64el",
                    "boot_source_id": boot_source_low.id,
                    "boot_source_name": boot_source_low.name,
                    "boot_source_url": boot_source_low.url,
                },
            ]
        }
        assert expected == data


@pytest.mark.asyncio
class TestGetSelectedImagesHandler:
    async def test_get_selected_images(
        self,
        user_client: Client,
        factory: Factory,
        boot_source_custom: BootSource,
        boot_source: BootSource,
        boot_source_low: BootSource,
        ubuntu_noble: BootAsset,
        items_ubuntu_noble_1: list[BootAssetItem],
        items_ubuntu_noble_2: list[BootAssetItem],
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        # create a custom image in the DB
        custom_asset = await factory.make_BootAsset(
            boot_source_custom.id,
            os="custom",
            release="plucky",
            title="My Custom Plucky Image",
            arch="amd64",
            base_image="ubuntu/plucky",
        )
        custom_ver = await factory.make_BootAssetVersion(custom_asset.id)
        custom_item = await factory.make_BootAssetItem(
            custom_ver.id,
            file_size=1000,
            bytes_synced=1000,
        )

        resp = await user_client.get("/selected-images")
        assert resp.status_code == 200
        data = resp.json()
        size = sum([item.file_size for item in items_ubuntu_noble_2])
        downloaded = sum([item.bytes_synced for item in items_ubuntu_noble_2])
        expected = {
            "items": [
                {
                    "selection_id": None,
                    "os": custom_asset.os,
                    "release": custom_asset.release,
                    "arch": custom_asset.arch,
                    "boot_source_id": boot_source_custom.id,
                    "boot_source_name": boot_source_custom.name,
                    "boot_source_url": boot_source_custom.url,
                    "size": custom_item.file_size,
                    "downloaded": custom_item.bytes_synced,
                    "custom_image_id": custom_asset.id,
                },
                {
                    "selection_id": sel_ubuntu_noble[1].id,
                    "os": ubuntu_noble.os,
                    "release": ubuntu_noble.release,
                    "arch": ubuntu_noble.arch,
                    "boot_source_id": boot_source.id,
                    "boot_source_name": boot_source.name,
                    "boot_source_url": boot_source.url,
                    "size": size,
                    "downloaded": downloaded,
                    "custom_image_id": None,
                },
            ]
        }
        assert data == expected


@pytest.mark.asyncio
class TestGetImageSourcesHandler:
    async def test_get_image_sources(
        self,
        user_client: Client,
        factory: Factory,
        boot_source: BootSource,
        boot_source_low: BootSource,
        ubuntu_noble: BootAsset,
        items_ubuntu_noble_1: list[BootAssetItem],
        items_ubuntu_noble_2: list[BootAssetItem],
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        alt_source = await factory.make_BootSource(
            url="alt.boot.source", name="Alternative Source"
        )
        alt_selection = await factory.make_BootSourceSelection(
            alt_source.id, os="ubuntu", release="noble", arch="amd64"
        )
        resp = await user_client.get(
            "/image-sources?os=ubuntu&release=noble&arch=amd64"
        )
        expected = [
            {
                "selection_id": sel_ubuntu_noble[1].id,
                "id": sel_ubuntu_noble[1].boot_source_id,
                "name": boot_source.name,
                "url": boot_source.url,
            },
            {
                "selection_id": alt_selection.id,
                "id": alt_source.id,
                "name": alt_source.name,
                "url": alt_source.url,
            },
        ]
        assert resp.json()["items"] == expected

    async def test_missing_params(
        self,
        user_client: Client,
    ) -> None:
        resp = await user_client.get("/image-sources")
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestPostSelectableImagesSelectHandler:
    async def test_post(
        self,
        user_client: Client,
        factory: Factory,
        ubuntu_noble: BootAsset,
        ubuntu_jammy: BootAsset,
        centos: BootAsset,
        sel_centos: BootSourceSelection,
        sel_ubuntu_noble: list[BootSourceSelection],
        mock_workflow_service: MockType,
    ) -> None:
        # don't use jammy selection fixutre since it is selected already
        jammy_sel = await factory.make_BootSourceSelection(
            ubuntu_jammy.boot_source_id,
            label=ubuntu_jammy.label,
            os=ubuntu_jammy.os,
            release=ubuntu_jammy.release,  # type: ignore
            arch=ubuntu_jammy.arch,
            selected=False,
        )
        data = {
            "selection_ids": [
                jammy_sel.id,
                sel_centos.id,
            ]
        }
        resp = await user_client.post("/selectable-images:select", json=data)
        assert resp.status_code == 201
        selections = await factory.get("boot_source_selection")
        assert len(selections) == 4
        selections_no_id = [
            {
                "os": sel["os"],
                "release": sel["release"],
                "arch": sel["arch"],
                "label": sel["label"],
                "arch": sel["arch"],
                "selected": sel["selected"],
            }
            for sel in selections
        ]
        expected_jammy_sel = {
            "os": ubuntu_jammy.os,
            "release": ubuntu_jammy.release,
            "arch": ubuntu_jammy.arch,
            "label": ubuntu_jammy.label,
            "selected": True,
        }
        expected_centos_sel = {
            "os": centos.os,
            "release": centos.release,
            "arch": centos.arch,
            "label": centos.label,
            "selected": True,
        }
        assert sel_ubuntu_noble[0].model_dump() in selections
        assert sel_ubuntu_noble[1].model_dump() in selections
        assert expected_jammy_sel in selections_no_id
        assert expected_centos_sel in selections_no_id
        expected_calls = [
            call(
                jammy_sel.boot_source_id,
            ),
            call(
                sel_centos.boot_source_id,
            ),
        ]
        assert (
            mock_workflow_service.trigger_sync.call_args_list == expected_calls
        )

    async def test_post_missing_ids(
        self,
        user_client: Client,
    ) -> None:
        resp = await user_client.post(
            "/selectable-images:select", json={"selection_ids": [999]}
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestPostSelectedImagesRemoveHandler:
    async def test_post(
        self,
        ubuntu_noble: BootAsset,
        ubuntu_jammy: BootAsset,
        items_ubuntu_noble_1: list[BootAssetItem],
        items_ubuntu_jammy_1: list[BootAssetItem],
        factory: Factory,
        user_client: Client,
        mocker: MockerFixture,
        mock_workflow_service: MockType,
    ) -> None:
        assert ubuntu_noble.release is not None
        assert ubuntu_jammy.release is not None
        noble_sel = await factory.make_BootSourceSelection(
            ubuntu_noble.boot_source_id,
            label=ubuntu_noble.label,
            os=ubuntu_noble.os,
            release=ubuntu_noble.release,
            arch=ubuntu_noble.arch,
            selected=True,
        )
        jammy_sel = await factory.make_BootSourceSelection(
            ubuntu_jammy.boot_source_id,
            label=ubuntu_jammy.label,
            os=ubuntu_jammy.os,
            release=ubuntu_jammy.release,
            arch=ubuntu_jammy.arch,
            selected=True,
        )
        mock_start_wf = mocker.patch(
            "msm.apiserver.middleware.S3Middleware.start_delete_workflow",
        )
        resp = await user_client.post(
            "/selected-images:remove",
            json={"selection_ids": [noble_sel.id, jammy_sel.id]},
        )
        assert resp.status_code == 204
        mock_start_wf.assert_called_once_with(
            ANY, [i.id for i in items_ubuntu_noble_1 + items_ubuntu_jammy_1]
        )
        expected_calls = [
            call(
                ubuntu_noble.boot_source_id,
            ),
        ]
        assert (
            mock_workflow_service.trigger_sync.call_args_list == expected_calls
        )
        selections = await factory.get("boot_source_selection")
        new_noble_selection = noble_sel.model_dump()
        new_noble_selection["selected"] = False
        new_jammy_selection = jammy_sel.model_dump()
        new_jammy_selection["selected"] = False
        assert new_noble_selection in selections
        assert new_jammy_selection in selections

    async def test_post_missing_ids(
        self,
        user_client: Client,
    ) -> None:
        resp = await user_client.post(
            "/selected-images:remove", json={"selection_ids": [999]}
        )
        assert resp.status_code == 404
