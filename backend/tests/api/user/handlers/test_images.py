from datetime import MAXYEAR, UTC, datetime
from hashlib import sha256
import json
from pathlib import Path

from pydantic_core import ValidationError
import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import (
    ItemFileType,
)
from msm.service import IndexService
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestCustomImageUploadHandler:
    async def test_post(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mock_resource = mocker.patch(
            "msm.api.user.handlers.images.boto3.resource"
        )
        mock_upload = mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.upload"
        )
        mock_complete_upload = mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.complete_upload"
        )
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        monkeypatch.setenv("MSM_S3_PATH", "test/path")

        bs = await factory.make_BootSource()
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
            mock_resource.assert_called_with(
                "s3",
                use_ssl=False,
                verify=False,
                endpoint_url="http://test-endpoint",
                aws_access_key_id="test-access-key",
                aws_secret_access_key="test-secret-key",
            )
            mock_upload.assert_called_once()
            mock_complete_upload.assert_called_once()
            stored_assets = await factory.get("boot_asset")
            stored_versions = await factory.get("boot_asset_version")
            stored_items = await factory.get("boot_asset_item")
            assert len(stored_assets) == 1
            assert len(stored_versions) == 1
            assert len(stored_items) == 1
            expected_asset = {
                "id": 1,
                "boot_source_id": bs.id,
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
                "eol": datetime(MAXYEAR, 12, 31, 23, tzinfo=UTC),
                "esm_eol": datetime(MAXYEAR, 12, 31, 23, tzinfo=UTC),
                "signed": False,
            }
            expected_version = {
                "id": 1,
                "boot_asset_id": stored_assets[0]["id"],
                "version": datetime.now().strftime("%Y%m%d") + ".1",
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
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mock_resource = mocker.patch(
            "msm.api.user.handlers.images.boto3.resource"
        )
        mock_upload = mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.upload"
        )
        mock_complete_upload = mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.complete_upload"
        )
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        monkeypatch.setenv("MSM_S3_PATH", "test/path")

        bs = await factory.make_BootSource()
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
            mock_resource.assert_called_with(
                "s3",
                use_ssl=False,
                verify=False,
                endpoint_url="http://test-endpoint",
                aws_access_key_id="test-access-key",
                aws_secret_access_key="test-secret-key",
            )
            mock_upload.assert_called()
            mock_complete_upload.assert_called()
            stored_assets = await factory.get("boot_asset")
            stored_versions = await factory.get("boot_asset_version")
            stored_items = await factory.get("boot_asset_item")
            assert len(stored_assets) == 1
            assert len(stored_versions) == 2
            assert len(stored_items) == 2
            expected_asset = {
                "id": 1,
                "boot_source_id": bs.id,
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
                "eol": datetime(MAXYEAR, 12, 31, 23, tzinfo=UTC),
                "esm_eol": datetime(MAXYEAR, 12, 31, 23, tzinfo=UTC),
                "signed": False,
            }
            expected_first_version = {
                "id": 1,
                "boot_asset_id": stored_assets[0]["id"],
                "version": datetime.now().strftime("%Y%m%d") + ".1",
            }
            expected_second_version = {
                "id": 2,
                "boot_asset_id": stored_assets[0]["id"],
                "version": datetime.now().strftime("%Y%m%d") + ".2",
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
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mock_s3_target = mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget"
        )
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        monkeypatch.setenv("MSM_S3_PATH", "test/path")

        await factory.make_BootSource()
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
            mock_s3_target.assert_called_with(mocker.ANY, "1", mocker.ANY)

    async def test_post_wrong_file_size(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mocker.patch("msm.api.user.handlers.images.boto3.resource")
        mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.upload"
        )
        mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.complete_upload"
        )
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        monkeypatch.setenv("MSM_S3_PATH", "test/path")

        await factory.make_BootSource()
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
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mock_resource = mocker.patch(
            "msm.api.user.handlers.images.boto3.resource"
        )
        mock_upload = mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.upload"
        )
        mock_complete_upload = mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.complete_upload"
        )
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        monkeypatch.setenv("MSM_S3_PATH", "test/path")

        bs = await factory.make_BootSource()
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
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mock_resource = mocker.patch(
            "msm.api.user.handlers.images.boto3.resource"
        )
        mock_upload = mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.upload"
        )
        mock_complete_upload = mocker.patch(
            "msm.api.user.handlers.images.S3MultipartUploadTarget.complete_upload"
        )
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        monkeypatch.setenv("MSM_S3_PATH", "test/path")

        bs = await factory.make_BootSource()
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
    async def test_download(
        self,
        user_client: Client,
        factory: Factory,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mocker.patch("msm.api.user.handlers.images.boto3.resource")
        monkeypatch.setenv("MSM_S3_BUCKET", "test-bucket")
        monkeypatch.setenv("MSM_S3_ENDPOINT", "test-endpoint")
        monkeypatch.setenv("MSM_S3_ACCESS_KEY", "test-access-key")
        monkeypatch.setenv("MSM_S3_SECRET_KEY", "test-secret-key")
        file_path = "ubuntu/noble/boot-kernel"
        bs = await factory.make_BootSource()
        ba = await factory.make_BootAsset(bs.id)
        bv = await factory.make_BootAssetVersion(ba.id)
        bi = await factory.make_BootAssetItem(bv.id, path=file_path)

        resp = await user_client.get(f"/images/latest/stable/{file_path}")
        assert resp.status_code == 200

    async def test_download_not_found(
        self, user_client: Client, factory: Factory
    ) -> None:
        resp = await user_client.get(
            "/images/latest/stable/ubuntu/noble/unknown-file"
        )
        assert resp.status_code == 404

    async def test_invalid_track(
        self, user_client: Client, factory: Factory
    ) -> None:
        resp = await user_client.get(
            "/images/1.0/stable/ubuntu/noble/boot-kernel"
        )
        assert resp.status_code == 400

    async def test_invalid_risk(
        self, user_client: Client, factory: Factory
    ) -> None:
        resp = await user_client.get(
            "/images/latest/edge/ubuntu/noble/boot-kernel"
        )
        assert resp.status_code == 400

    async def test_download_index(
        self,
        user_client: Client,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        await factory.make_Setting(
            "service_url",
            value="https://maas.site.manager",
        )
        index_service = IndexService(db_connection)
        await index_service.create()
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
        db_connection: AsyncConnection,
    ) -> None:
        await factory.make_Setting(
            "service_url",
            value="https://maas.site.manager",
        )
        index_service = IndexService(db_connection)
        await index_service.create()
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
class TestGetAvailableImagesHandler:
    async def test_get_available_images(
        self, user_client: Client, factory: Factory
    ) -> None:
        low_prio_source = await factory.make_BootSource(
            priority=1,
            name="Low Prio Source",
        )
        high_prio_source = await factory.make_BootSource(
            priority=2,
            name="High Prio Source",
        )
        await factory.make_BootSourceSelection(
            low_prio_source.id,
            os="ubuntu",
            release="noble",
            available=["amd64", "arm64", "ppc64el"],
            selected=["amd64", "arm64"],
        )
        await factory.make_BootSourceSelection(
            high_prio_source.id,
            os="ubuntu",
            release="noble",
            available=["amd64", "arm64"],
            selected=["amd64"],
        )
        await factory.make_BootSourceSelection(
            high_prio_source.id,
            os="ubuntu",
            release="jammy",
            available=["amd64", "arm64"],
            selected=[],
        )
        await factory.make_BootSourceSelection(
            low_prio_source.id,
            os="windows",
            release="11",
            available=["amd64", "ppc64el"],
            selected=["amd64", "ppc64el"],
        )
        resp = await user_client.get("/available-images")
        assert resp.status_code == 200
        data = resp.json()
        expected = {
            "items": [
                {
                    "os": "ubuntu",
                    "release": "jammy",
                    "arch": "amd64",
                    "source_name": "High Prio Source",
                    "selected": False,
                },
                {
                    "os": "ubuntu",
                    "release": "jammy",
                    "arch": "arm64",
                    "source_name": "High Prio Source",
                    "selected": False,
                },
                {
                    "os": "ubuntu",
                    "release": "noble",
                    "arch": "amd64",
                    "source_name": "High Prio Source",
                    "selected": True,
                },
                {
                    "os": "ubuntu",
                    "release": "noble",
                    "arch": "arm64",
                    "source_name": "High Prio Source",
                    "selected": False,
                },
                {
                    "os": "windows",
                    "release": "11",
                    "arch": "amd64",
                    "source_name": "Low Prio Source",
                    "selected": True,
                },
                {
                    "os": "windows",
                    "release": "11",
                    "arch": "ppc64el",
                    "source_name": "Low Prio Source",
                    "selected": True,
                },
            ]
        }
        assert expected == data
