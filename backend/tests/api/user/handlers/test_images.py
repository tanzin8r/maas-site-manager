from collections.abc import AsyncIterator
from hashlib import sha256
import json
from pathlib import Path

from pydantic_core import ValidationError
import pytest
from pytest_mock import MockerFixture, MockType
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import (
    BootAsset,
    BootAssetItem,
    BootSource,
    BootSourceSelection,
    ItemFileType,
)
from msm.service import IndexService
from msm.service.images import END_OF_TIME
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.fixture(autouse=True)
def s3_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
    monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
    monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
    monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("MSM_S3_PATH", "test/path")


@pytest.fixture(autouse=True)
def mock_now(mocker: MockerFixture, factory: Factory) -> MockType:
    return mocker.patch(
        "msm.api.user.handlers.images.now_utc",
        return_value=factory.now,
    )


@pytest.fixture
def s3_resource(mocker: MockerFixture) -> MockType:
    return mocker.patch("msm.api.user.handlers.images.boto3.resource")


@pytest.fixture
def s3_upload(mocker: MockerFixture) -> MockType:
    return mocker.patch(
        "msm.api.user.handlers.images.S3MultipartUploadTarget.upload"
    )


@pytest.fixture
def s3_upload_target(mocker: MockerFixture) -> MockType:
    return mocker.patch("msm.api.user.handlers.images.S3MultipartUploadTarget")


@pytest.fixture
def s3_complete_upload(mocker: MockerFixture) -> MockType:
    return mocker.patch(
        "msm.api.user.handlers.images.S3MultipartUploadTarget.complete_upload"
    )


@pytest.mark.asyncio
class TestCustomImageUploadHandler:
    async def test_post(
        self,
        user_client: Client,
        factory: Factory,
        boot_source_custom: BootSource,
        s3_resource: MockType,
        s3_upload: MockType,
        s3_complete_upload: MockType,
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
            assert resp.status_code == 200
            s3_resource.assert_called_with(
                "s3",
                use_ssl=False,
                verify=False,
                endpoint_url="http://test-endpoint",
                aws_access_key_id="test-access-key",
                aws_secret_access_key="test-secret-key",
            )
            s3_upload.assert_called_once()
            s3_complete_upload.assert_called_once()
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
                "os": "ubuntu",
                "release": "noble",
                "arch": "amd64",
                "title": "My Custom Image",
                "codename": None,
                "subarch": None,
                "compatibility": None,
                "flavor": None,
                "base_image": "ubuntu/noble",
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
                "path": "",
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
        s3_resource: MockType,
        s3_upload: MockType,
        s3_complete_upload: MockType,
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
            assert resp.status_code == 200
            first_item_id = resp.json()["id"]
            resp = await user_client.post(
                "/images",
                data=data,
                files=file_data,
            )
            assert resp.status_code == 200
            second_item_id = resp.json()["id"]
            s3_resource.assert_called_with(
                "s3",
                use_ssl=False,
                verify=False,
                endpoint_url="http://test-endpoint",
                aws_access_key_id="test-access-key",
                aws_secret_access_key="test-secret-key",
            )
            s3_upload.assert_called()
            s3_complete_upload.assert_called()
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
                "os": "ubuntu",
                "release": "noble",
                "arch": "amd64",
                "title": "My Custom Image",
                "codename": None,
                "subarch": None,
                "compatibility": None,
                "flavor": None,
                "base_image": "ubuntu/noble",
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
                "path": "",
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
                "path": "",
                "source_package": None,
                "source_release": None,
                "source_version": None,
            }
            assert stored_assets[0] == expected_asset
            assert stored_versions[0] == expected_first_version
            assert stored_versions[1] == expected_second_version
            assert stored_items[0] == expected_first_item
            assert stored_items[1] == expected_second_item

    async def test_post_filepath_is_correct(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        boot_source_custom: BootSource,
        s3_resource: MockType,
        s3_upload: MockType,
        s3_complete_upload: MockType,
        s3_upload_target: MockType,
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
            # all we care about is whether S3MultipartUploadTarget
            # was instantiated with the right filepath
            # mocking this object will result in a ValidationError
            # later down the line
            with pytest.raises(ValidationError):
                await user_client.post(
                    "/images",
                    data=data,
                    files=file_data,
                )
            s3_upload_target.assert_called_with(mocker.ANY, "1", mocker.ANY)

    async def test_post_wrong_file_size(
        self,
        user_client: Client,
        factory: Factory,
        boot_source_custom: BootSource,
        s3_resource: MockType,
        s3_upload: MockType,
        s3_complete_upload: MockType,
        tmp_path: Path,
    ) -> None:
        test_file_content = "This is a test file."
        data = {
            "os": "ubuntu",
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
        s3_resource: MockType,
        s3_upload: MockType,
        s3_complete_upload: MockType,
        tmp_path: Path,
    ) -> None:
        test_file_content = "This is a test file."
        data = {
            "os": "ubuntu",
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
        s3_resource: MockType,
        s3_upload: MockType,
        s3_complete_upload: MockType,
        tmp_path: Path,
    ) -> None:
        test_file_content = "This is a test file."
        data = {
            "os": "ubuntu",
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


@pytest.mark.asyncio
class TestBootAssetItemsDownloadHandler:
    @pytest.fixture
    async def index_service(
        self, db_connection: AsyncConnection
    ) -> AsyncIterator[IndexService]:
        index_service = IndexService(db_connection)
        await index_service.create()
        yield index_service

    async def test_download(
        self,
        user_client: Client,
        boot_source: BootSource,
        items_ubuntu_jammy_1: list[BootAssetItem],
        s3_resource: MockType,
    ) -> None:
        file_path = items_ubuntu_jammy_1[0].path
        resp = await user_client.get(
            f"/images/latest/stable/{boot_source.id}/{file_path}"
        )
        assert resp.status_code == 200

    async def test_download_not_found(
        self, user_client: Client, boot_source: BootSource
    ) -> None:
        resp = await user_client.get(
            f"/images/latest/stable/{boot_source.id}/ubuntu/noble/unknown-file"
        )
        assert resp.status_code == 404

    async def test_invalid_track(
        self, user_client: Client, boot_source: BootSource
    ) -> None:
        resp = await user_client.get(
            f"/images/1.0/stable/{boot_source.id}/ubuntu/noble/boot-kernel"
        )
        assert resp.status_code == 400

    async def test_invalid_risk(
        self, user_client: Client, boot_source: BootSource
    ) -> None:
        resp = await user_client.get(
            f"/images/latest/edge/{boot_source.id}/ubuntu/noble/boot-kernel"
        )
        assert resp.status_code == 400

    async def test_download_index(
        self,
        user_client: Client,
        factory: Factory,
        index_service: IndexService,
    ) -> None:
        await factory.make_Setting(
            "service_url",
            value="https://maas.site.manager",
        )
        resp = await user_client.get(
            "/images/latest/stable/streams/v1/index.json"
        )
        assert resp.status_code == 200
        index = resp.json()
        expected_index = {
            "format": "index:1.0",
            "index": {
                "manager.site.maas:stream:v1:download": {
                    "datatype": "image-ids",
                    "format": "products:1.0",
                    "path": "streams/v1/manager.site.maas:stream:v1:download.json",
                    "updated": index["updated"],
                    "products": [],
                }
            },
            "updated": index["updated"],
        }
        assert index == expected_index

    async def test_download_download_index(
        self,
        user_client: Client,
        factory: Factory,
        index_service: IndexService,
    ) -> None:
        await factory.make_Setting(
            "service_url",
            value="https://maas.site.manager",
        )
        resp = await user_client.get(
            "/images/latest/stable/streams/v1/manager.site.maas:stream:v1:download.json"
        )
        assert resp.status_code == 200
        dl_index = resp.json()
        expected_index = {
            "content_id": "manager.site.maas:stream:v1:download",
            "datatype": "image-ids",
            "format": "products:1.0",
            "products": {},
            "updated": dl_index["updated"],
        }
        assert dl_index == expected_index


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
            selected=True,
        )
        await factory.make_BootSourceSelection(
            boot_source_low.id,
            os="ubuntu",
            release="noble",
            arch="arm64",
            selected=True,
        )
        await factory.make_BootSourceSelection(
            boot_source_low.id,
            os="ubuntu",
            release="noble",
            arch="ppc64el",
            selected=False,
        )
        await factory.make_BootSourceSelection(
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
        await factory.make_BootSourceSelection(
            boot_source.id,
            os="ubuntu",
            release="jammy",
            arch="amd64",
            selected=False,
        )
        await factory.make_BootSourceSelection(
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
                    "os": "ubuntu",
                    "release": "jammy",
                    "arch": "amd64",
                    "boot_source_id": boot_source.id,
                    "boot_source_name": boot_source.name,
                    "boot_source_url": boot_source.url,
                },
                {
                    "os": "ubuntu",
                    "release": "jammy",
                    "arch": "arm64",
                    "boot_source_id": boot_source.id,
                    "boot_source_name": boot_source.name,
                    "boot_source_url": boot_source.url,
                },
                {
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
        boot_source: BootSource,
        boot_source_low: BootSource,
        ubuntu_noble: BootAsset,
        items_ubuntu_noble_1: list[BootAssetItem],
        items_ubuntu_noble_2: list[BootAssetItem],
        sel_ubuntu_noble: list[BootSourceSelection],
    ) -> None:
        resp = await user_client.get("/selected-images")
        assert resp.status_code == 200
        data = resp.json()
        size = sum([item.file_size for item in items_ubuntu_noble_2])
        downloaded = sum([item.bytes_synced for item in items_ubuntu_noble_2])
        expected = {
            "items": [
                {
                    "id": ubuntu_noble.id,
                    "os": ubuntu_noble.os,
                    "release": ubuntu_noble.release,
                    "arch": ubuntu_noble.arch,
                    "boot_source_id": boot_source.id,
                    "boot_source_name": boot_source.name,
                    "boot_source_url": boot_source.url,
                    "size": size,
                    "downloaded": downloaded,
                    "is_custom_image": False,
                }
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
        await factory.make_BootSourceSelection(
            alt_source.id, os="ubuntu", release="noble", arch="amd64"
        )
        resp = await user_client.get(
            "/image-sources?os=ubuntu&release=noble&arch=amd64"
        )
        expected = [
            {
                "id": sel_ubuntu_noble[0].boot_source_id,
                "name": boot_source.name,
                "url": boot_source.url,
            },
            {
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
    ) -> None:
        # don't use jammy selection fixutre since it is selected already
        await factory.make_BootSourceSelection(
            ubuntu_jammy.boot_source_id,
            label=ubuntu_jammy.label,
            os=ubuntu_jammy.os,
            release=ubuntu_jammy.release,  # type: ignore
            arch=ubuntu_jammy.arch,
            selected=False,
        )
        data = {
            "asset_ids": [
                ubuntu_jammy.id,
                centos.id,
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
        jammy_sel = {
            "os": ubuntu_jammy.os,
            "release": ubuntu_jammy.release,
            "arch": ubuntu_jammy.arch,
            "label": ubuntu_jammy.label,
            "selected": True,
        }
        centos_sel = {
            "os": centos.os,
            "release": centos.release,
            "arch": centos.arch,
            "label": centos.label,
            "selected": True,
        }
        assert sel_ubuntu_noble[0].model_dump() in selections
        assert sel_ubuntu_noble[1].model_dump() in selections
        assert jammy_sel in selections_no_id
        assert centos_sel in selections_no_id

    async def test_post_missing_ids(
        self,
        user_client: Client,
    ) -> None:
        resp = await user_client.post(
            "/selectable-images:select", json={"asset_ids": [999]}
        )
        assert resp.status_code == 404
