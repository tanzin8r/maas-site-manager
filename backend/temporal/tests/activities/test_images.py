from dataclasses import asdict
from datetime import UTC, datetime
import json
import typing
from unittest.mock import PropertyMock

from activities.images import (  # type: ignore
    BootAsset,
    BootAssetItem,
    BootAssetKind,
    BootAssetLabel,
    BootAssetVersion,
    CreateIndexJsonParams,
    DownloadAssetParams,
    GetOrCreateAssetParams,
    GetOrCreateItemParams,
    GetOrCreateVersionParams,
    ImageManagementActivity,
    S3Params,
    S3ResourceManager,
    UpdateBytesSyncedParams,
)
from httpx import AsyncClient, Response
import pytest
from pytest_mock import MockerFixture
from temporalio.testing import ActivityEnvironment


class AsyncIterator:
    """
    Class for mocking async iterators, namely httpx Request.aiter_bytes()
    """

    def __init__(self, seq: list[typing.Any]) -> None:
        self.iter = iter(seq)

    def __aiter__(self) -> "AsyncIterator":
        return self

    async def __anext__(self) -> typing.Any:
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


@pytest.fixture
async def im_act(mocker: MockerFixture) -> ImageManagementActivity:
    mock_response = mocker.create_autospec(Response)
    mock_response.aiter_bytes.return_value = AsyncIterator([b"abc", b"def"])

    mock_client = mocker.create_autospec(AsyncClient)
    mock_client.stream.return_value.__aenter__.return_value = mock_response
    mocker.patch.object(
        ImageManagementActivity, "_create_client", return_value=mock_client
    )
    return ImageManagementActivity()


class TestDownloadUpstreamActivities:
    async def test_update_bytes_synced(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        act_env = ActivityEnvironment()
        params = UpdateBytesSyncedParams(
            msm_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            bytes_synced=10,
        )
        await act_env.run(im_act.update_bytes_synced, params)
        im_act.client.patch.assert_called_with(
            params.msm_url,
            headers={"Authorization": f"bearer {params.msm_jwt}"},
            json={"bytes_synced": params.bytes_synced},
        )

    async def test_download_asset(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        mocker.patch.object(S3ResourceManager, "_create_multipart_upload")
        mocker.patch.object(S3ResourceManager, "upload_part")
        mocker.patch.object(S3ResourceManager, "complete_upload")
        mocker.patch.object(S3ResourceManager, "abort_upload")
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="test-key",
            secret_key="test-secret-key",
            bucket="test-bucket",
            path="test/path",
        )
        item_id = 1
        s3_manager = S3ResourceManager(s3_params, item_id)
        mocker.patch.object(s3_manager, "bytes_sent", 6)
        mocker.patch.object(
            im_act, "_create_s3_manager", return_value=s3_manager
        )
        act_env = ActivityEnvironment()
        params = DownloadAssetParams(
            ss_url="http://test.ss.url",
            boot_asset_item_id=item_id,
            s3_params=s3_params,
        )

        result = await act_env.run(im_act.download_asset, params)
        # len of total bytes mocked in AsyncIterator from im_act fixture
        assert result == 6
        s3_manager._create_multipart_upload.assert_called_once()
        s3_manager.upload_part.assert_called_once_with(b"abcdef")
        s3_manager.complete_upload.assert_called_once()
        s3_manager.abort_upload.assert_not_called()

    async def test_download_asset_is_aborted(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        mocker.patch.object(S3ResourceManager, "_create_multipart_upload")
        mocker.patch.object(
            S3ResourceManager, "upload_part", side_effect=RuntimeError
        )
        mocker.patch.object(S3ResourceManager, "complete_upload")
        mocker.patch.object(S3ResourceManager, "abort_upload")
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="test-key",
            secret_key="test-secret-key",
            bucket="test-bucket",
            path="test/path",
        )
        item_id = 1
        s3_manager = S3ResourceManager(s3_params, item_id)
        mocker.patch.object(
            im_act, "_create_s3_manager", return_value=s3_manager
        )
        act_env = ActivityEnvironment()
        params = DownloadAssetParams(
            ss_url="http://test.ss.url",
            boot_asset_item_id=1,
            s3_params=S3Params(
                endpoint="http://s3",
                access_key="test-key",
                secret_key="test-secret-key",
                bucket="test-bucket",
                path="test/path",
            ),
        )
        with pytest.raises(RuntimeError):
            await act_env.run(im_act.download_asset, params)
        im_act._create_s3_manager.assert_called_with(params.s3_params, 1)
        s3_manager._create_multipart_upload.assert_called_once()
        s3_manager.upload_part.assert_called_once()
        s3_manager.complete_upload.assert_not_called()
        s3_manager.abort_upload.assert_called_once()

    async def test_get_or_create_asset_retrieved(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        mock_response = mocker.create_autospec(Response)
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_response.json.return_value = {"items": [{"id": 2}]}
        im_act.client.get.return_value = mock_response

        act_env = ActivityEnvironment()
        params = GetOrCreateAssetParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            asset=BootAsset(
                boot_source_id=1,
                kind=BootAssetKind.BOOTLOADER,
                label=BootAssetLabel.CANDIDATE,
                os="ubuntu",
                arch="amd64",
                release="24.04",
                bootloader_type="pxe",
            ),
        )
        result = await act_env.run(im_act.get_or_create_asset, params)
        assert result == 2
        im_act.client.get.assert_called_with(
            f"{params.msm_base_url}/api/v1/bootassets",
            headers={"Authorization": f"bearer {params.msm_jwt}"},
            params={
                "kind": params.asset.kind,
                "label": params.asset.label,
                "os": params.asset.os,
                "arch": params.asset.arch,
            },
        )
        im_act.client.post.assert_not_called()

    async def test_get_or_create_asset_created(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        mock_response = mocker.create_autospec(Response)
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_response.json.return_value = {"items": []}
        im_act.client.get.return_value = mock_response

        mock_post_response = mocker.create_autospec(Response)
        type(mock_post_response).status_code = PropertyMock(return_value=200)
        mock_post_response.json.return_value = {"id": 2}
        im_act.client.post.return_value = mock_post_response

        act_env = ActivityEnvironment()
        params = GetOrCreateAssetParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            asset=BootAsset(
                boot_source_id=1,
                kind=BootAssetKind.BOOTLOADER,
                label=BootAssetLabel.CANDIDATE,
                os="ubuntu",
                arch="amd64",
                release="24.04",
                codename="Noble",
                title="Noble Bootloader",
                subarch="amd64",
                compatibility=["amd64"],
                flavor="flav",
                bootloader_type="pxe",
                eol=datetime(year=2026, month=3, day=24, tzinfo=UTC),
                esm_eol=datetime(year=2027, month=3, day=24, tzinfo=UTC),
            ),
        )
        result = await act_env.run(im_act.get_or_create_asset, params)
        assert result == 2
        im_act.client.get.assert_called_with(
            f"{params.msm_base_url}/api/v1/bootassets",
            headers={"Authorization": f"bearer {params.msm_jwt}"},
            params={
                "kind": params.asset.kind,
                "label": params.asset.label,
                "os": params.asset.os,
                "arch": params.asset.arch,
            },
        )
        im_act.client.post.assert_called_with(
            f"{params.msm_base_url}/api/v1/bootassets",
            json=asdict(params.asset),
            headers={"Authorization": f"bearer {params.msm_jwt}"},
        )

    async def test_get_or_create_version_retrieved(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        mock_response = mocker.create_autospec(Response)
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_response.json.return_value = {"items": [{"id": 2}]}
        im_act.client.get.return_value = mock_response

        act_env = ActivityEnvironment()
        params = GetOrCreateVersionParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            version=BootAssetVersion(boot_asset_id=1, version="20250903.1"),
        )
        result = await act_env.run(im_act.get_or_create_version, params)
        assert result == (False, 2)
        im_act.client.get.assert_called_with(
            f"{params.msm_base_url}/api/v1/bootasset-versions",
            headers={"Authorization": f"bearer {params.msm_jwt}"},
            params={
                "version": params.version.version,
                "boot_asset_id": params.version.boot_asset_id,
            },
        )
        im_act.client.post.assert_not_called()

    async def test_get_or_create_version_created(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        mock_response = mocker.create_autospec(Response)
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_response.json.return_value = {"items": []}
        im_act.client.get.return_value = mock_response

        mock_post_response = mocker.create_autospec(Response)
        type(mock_post_response).status_code = PropertyMock(return_value=200)
        mock_post_response.json.return_value = {"id": 2}
        im_act.client.post.return_value = mock_post_response

        act_env = ActivityEnvironment()
        params = GetOrCreateVersionParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            version=BootAssetVersion(boot_asset_id=1, version="20250903.1"),
        )
        result = await act_env.run(im_act.get_or_create_version, params)
        assert result == (True, 2)
        im_act.client.get.assert_called_with(
            f"{params.msm_base_url}/api/v1/bootasset-versions",
            headers={"Authorization": f"bearer {params.msm_jwt}"},
            params={
                "version": params.version.version,
                "boot_asset_id": params.version.boot_asset_id,
            },
        )
        im_act.client.post.assert_called_with(
            f"{params.msm_base_url}/api/v1/bootassets/{params.version.boot_asset_id}/versions",
            json={"version": params.version.version},
            headers={"Authorization": f"bearer {params.msm_jwt}"},
        )

    async def test_get_or_create_item_retrieved(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        mock_response = mocker.create_autospec(Response)
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_response.json.return_value = {"items": [{"id": 2}]}
        im_act.client.get.return_value = mock_response

        act_env = ActivityEnvironment()
        params = GetOrCreateItemParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            item=BootAssetItem(
                boot_asset_version_id=2,
                ftype="testftype",
                sha256="alskdjfl2k34jlkvjalsdkjf23l34nik",
                path="test/path",
                file_size=200,
                source_package="testpackage",
                source_version="testversion",
                source_release="testrelease",
            ),
        )
        result = await act_env.run(im_act.get_or_create_item, params)
        assert result == 2
        im_act.client.get.assert_called_with(
            f"{params.msm_base_url}/api/v1/bootasset-items",
            headers={"Authorization": f"bearer {params.msm_jwt}"},
            params={"sha256": params.item.sha256},
        )
        im_act.client.post.assert_not_called()

    async def test_get_or_create_item_created(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        mock_response = mocker.create_autospec(Response)
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_response.json.return_value = {"items": []}
        im_act.client.get.return_value = mock_response

        mock_post_response = mocker.create_autospec(Response)
        type(mock_post_response).status_code = PropertyMock(return_value=200)
        mock_post_response.json.return_value = {"id": 2}
        im_act.client.post.return_value = mock_post_response

        act_env = ActivityEnvironment()
        params = GetOrCreateItemParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            item=BootAssetItem(
                boot_asset_version_id=2,
                ftype="testftype",
                sha256="alskdjfl2k34jlkvjalsdkjf23l34nik",
                path="test/path",
                file_size=200,
                source_package="testpackage",
                source_version="testversion",
                source_release="testrelease",
            ),
        )
        result = await act_env.run(im_act.get_or_create_item, params)
        assert result == 2
        im_act.client.get.assert_called_with(
            f"{params.msm_base_url}/api/v1/bootasset-items",
            headers={"Authorization": f"bearer {params.msm_jwt}"},
            params={"sha256": params.item.sha256},
        )
        expected_body = asdict(params.item)
        expected_body.pop("boot_asset_version_id")
        expected_body.pop("path")
        im_act.client.post.assert_called_with(
            f"{params.msm_base_url}/api/v1/bootasset-versions/2/items",
            json=expected_body,
            headers={"Authorization": f"bearer {params.msm_jwt}"},
        )

    async def test_create_index_json(
        self, mocker: MockerFixture, im_act: typing.Any
    ) -> None:
        mock_response = mocker.create_autospec(Response)
        type(mock_response).status_code = PropertyMock(return_value=200)
        mock_response.json.side_effect = [
            {
                "items": [
                    {
                        "id": 1,
                        "boot_source_id": 1,
                        "kind": 0,
                        "label": "stable",
                        "os": "ubuntu",
                        "arch": "amd64",
                        "release": "noble",
                        "codename": "Noble Numbat",
                        "title": "24.04 LTS",
                        "subarch": "hwe-p",
                        "compatibility": ["generic"],
                        "flavor": "generic",
                        "base_image": None,
                        "eol": "2029-04-01T00:00:00Z",
                        "esm_eol": "2036-04-01T00:00:00Z",
                    },
                    {
                        "id": 2,
                        "boot_source_id": 1,
                        "kind": 1,
                        "label": "stable",
                        "os": "grub-efi-signed",
                        "arch": "amd64",
                        "bootloader_type": "uefi",
                    },
                    {
                        "id": 3,
                        "boot_source_id": 1,
                        "kind": 0,
                        "label": "stable",
                        "os": "centos",
                        "arch": "amd64",
                        "release": "centos70",
                        "title": "CentOS 7",
                        "subarch": "generic",
                        "compatibility": ["generic"],
                        "eol": "2029-04-01T00:00:00Z",
                        "esm_eol": "2036-04-01T00:00:00Z",
                    },
                ]
            },
            # noble asset
            {"items": [{"id": 1, "version": "20250819.0"}]},
            {
                "items": [
                    {
                        "ftype": "boot-initrd",
                        "path": "noble/amd64/boot-initrd",
                        "sha256": "alskdjflakjsdf",
                        "file_size": 1000,
                    }
                ]
            },
            # bootloader asset
            {"items": [{"id": 1, "version": "20240819.0"}]},
            {
                "items": [
                    {
                        "ftype": "archive.tar.xz",
                        "path": "bootloaders/uefi/grub2-signed.tar.xz",
                        "sha256": "alskdjflakjsdf",
                        "file_size": 1000,
                        "source_package": "grub2-signed",
                        "source_release": "focal",
                        "source_version": "1.167.2+2.04-1ubuntu44.2",
                    }
                ]
            },
            # centos asset
            {"items": [{"id": 1, "version": "20230819.0"}]},
            {
                "items": [
                    {
                        "ftype": "manifest",
                        "path": "centos/centos79/root-tgz.manifest",
                        "sha256": "alskdjflakjsdf",
                        "file_size": 1000,
                    }
                ]
            },
        ]
        im_act.client.get.return_value = mock_response
        mocker.patch.object(S3ResourceManager, "upload_file")
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="test-key",
            secret_key="test-secret-key",
            bucket="test-bucket",
            path="test/path",
        )
        item_id = 1
        s3_manager = S3ResourceManager(s3_params, item_id, multipart=False)
        mocker.patch.object(
            im_act, "_create_s3_manager", return_value=s3_manager
        )
        act_env = ActivityEnvironment()
        params = CreateIndexJsonParams(
            msm_fqdn="maas.site.manager",
            msm_base_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            s3_params=s3_params,
        )
        await act_env.run(im_act.create_index_json, params)
        expected_index_json = {
            "format": "index:1.0",
            "index": {
                "manager.site.maas:stream:v1:download": {
                    "datatype": "image-ids",
                    "format": "products:1.0",
                    "path": "streams/v1/manager.site.maas:stream:v1:download.json",
                    "products": [
                        "manager.site.maas.stream:ubuntu:noble:amd64:hwe-p-generic",
                        "manager.site.maas.stream:grub-efi-signed:uefi:amd64",
                        "manager.site.maas.stream:centos:centos70:amd64:generic",
                    ],
                },
            },
        }
        expected_download_json = {
            "content_id": "manager.site.maas:stream:v1:download",
            "datatype": "image-ids",
            "format": "products:1.0",
            "products": {
                "manager.site.maas.stream:ubuntu:noble:amd64:hwe-p-generic": {
                    "arch": "amd64",
                    "kflavor": "generic",
                    "label": "stable",
                    "os": "ubuntu",
                    "release": "noble",
                    "release_codename": "Noble Numbat",
                    "release_title": "24.04 LTS",
                    "subarch": "hwe-p",
                    "subarches": "generic",
                    "support_eol": "2029-04-01T00:00:00Z",
                    "support_esm_eol": "2036-04-01T00:00:00Z",
                    "versions": {
                        "20250819.0": {
                            "items": {
                                "boot-initrd": {
                                    "ftype": "boot-initrd",
                                    "path": "noble/amd64/boot-initrd",
                                    "sha256": "alskdjflakjsdf",
                                    "size": 1000,
                                }
                            }
                        }
                    },
                },
                "manager.site.maas.stream:grub-efi-signed:uefi:amd64": {
                    "arch": "amd64",
                    "label": "stable",
                    "os": "grub-efi-signed",
                    "bootloader-type": "uefi",
                    "versions": {
                        "20240819.0": {
                            "items": {
                                "grub2-signed": {
                                    "ftype": "archive.tar.xz",
                                    "path": "bootloaders/uefi/grub2-signed.tar.xz",
                                    "sha256": "alskdjflakjsdf",
                                    "size": 1000,
                                    "src_package": "grub2-signed",
                                    "src_release": "focal",
                                    "src_version": "1.167.2+2.04-1ubuntu44.2",
                                }
                            }
                        }
                    },
                },
                "manager.site.maas.stream:centos:centos70:amd64:generic": {
                    "arch": "amd64",
                    "label": "stable",
                    "os": "centos",
                    "release": "centos70",
                    "release_title": "CentOS 7",
                    "subarch": "generic",
                    "subarches": "generic",
                    "support_eol": "2029-04-01T00:00:00Z",
                    "support_esm_eol": "2036-04-01T00:00:00Z",
                    "versions": {
                        "20230819.0": {
                            "items": {
                                "manifest": {
                                    "ftype": "manifest",
                                    "path": "centos/centos79/root-tgz.manifest",
                                    "sha256": "alskdjflakjsdf",
                                    "size": 1000,
                                }
                            }
                        }
                    },
                },
            },
        }
        index_args, index_kwargs = s3_manager.upload_file.call_args_list[0]
        download_args, download_kwargs = s3_manager.upload_file.call_args_list[
            1
        ]
        index_json = json.loads(index_args[0])
        download_json = json.loads(download_args[0])
        index_filename = index_kwargs["key_override"]
        download_filename = download_kwargs["key_override"]
        assert index_filename == "index.json"
        assert download_filename == "manager.site.maas:stream:v1:download.json"
        # copy the timestamps, as we can't replicate it exactly
        updated = index_json["updated"]
        expected_index_json["updated"] = updated
        for key in index_json["index"]:
            expected_index_json["index"][key]["updated"] = updated  # type: ignore
        expected_download_json["updated"] = updated
        assert expected_index_json == index_json
        assert expected_download_json == download_json
