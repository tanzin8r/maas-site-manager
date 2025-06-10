from dataclasses import asdict
from datetime import UTC, datetime
import typing
from unittest.mock import AsyncMock, MagicMock, PropertyMock

from httpx import AsyncClient, Response
import pytest
from pytest_mock import MockerFixture
from temporalio.testing import ActivityEnvironment

from temporal.resources.activities.download_upstream_activities import (
    BootAsset,
    BootAssetItem,
    BootAssetKind,
    BootAssetLabel,
    BootAssetVersion,
    DownloadAssetParams,
    DownloadJsonParams,
    GetBootSourceParams,
    GetOrCreateAssetParams,
    GetOrCreateItemParams,
    GetOrCreateVersionParams,
    ImageManagementActivity,
    LoadProductMapParams,
    ParseSsIndexParams,
    S3Params,
    S3ResourceManager,
    UpdateBytesSyncedParams,
)


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
        s3_manager._create_multipart_upload.assert_called_once()  # type: ignore
        s3_manager.upload_part.assert_called_once_with(b"abcdef")  # type: ignore
        s3_manager.complete_upload.assert_called_once()  # type: ignore
        s3_manager.abort_upload.assert_not_called()  # type: ignore

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
        s3_manager._create_multipart_upload.assert_called_once()  # type: ignore
        s3_manager.upload_part.assert_called_once()  # type: ignore
        s3_manager.complete_upload.assert_not_called()  # type: ignore
        s3_manager.abort_upload.assert_called_once()  # type: ignore

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


class TestGetBootSourceActivity:
    @pytest.mark.asyncio
    async def test_get_boot_source_success(
        self, mocker: MockerFixture, im_act: ImageManagementActivity
    ) -> None:
        act_env = ActivityEnvironment()

        params = GetBootSourceParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            boot_source_id=42,
        )

        # Mock responses for boot source and selections
        boot_source_response = mocker.Mock()
        boot_source_response.status_code = 200
        boot_source_response.json.return_value = {
            "id": 42,
            "name": "test-source",
            "url": "http://test.source.url/streams/v1/index.sjson",
            "keyring": "test-keyring",
        }

        selections_response = mocker.Mock()
        selections_response.status_code = 200
        selections_response.json.return_value = {
            "items": [
                {
                    "os": "ubuntu",
                    "release": "oracular",
                    "arches": "amd64,arm64",
                },
                {"os": "ubuntu", "release": "questing", "arches": "amd64"},
            ]
        }

        # Patch the client.get method to return the correct response in order
        im_act.client.get.side_effect = [  # type: ignore[attr-defined]
            boot_source_response,
            selections_response,
        ]

        # Act
        result = await act_env.run(im_act.get_boot_source, params)

        # Assert
        assert result["boot_source"] == {
            "id": 42,
            "name": "test-source",
            "url": "http://test.source.url/streams/v1/index.sjson",
            "keyring": "test-keyring",
        }
        assert "selections" in result
        assert result["selections"]["ubuntu---oracular"] == ["amd64", "arm64"]
        assert result["selections"]["ubuntu---questing"] == ["amd64"]

    @pytest.mark.asyncio
    async def test_get_boot_source_failure(
        self, mocker: MockerFixture, im_act: ImageManagementActivity
    ) -> None:
        act_env = ActivityEnvironment()

        params = GetBootSourceParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            boot_source_id=42,
        )

        # Simulate failure on first call
        fail_response = mocker.Mock()
        fail_response.status_code = 404
        fail_response.text = "Not found"
        im_act.client.get.return_value = fail_response  # type: ignore[attr-defined]

        with pytest.raises(Exception):
            await act_env.run(im_act.get_boot_source, params)


class TestDownloadSSJsonActivity:
    @pytest.mark.asyncio
    async def test_download_json_plain(
        self, im_act: ImageManagementActivity, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = b'{"foo": "bar"}'
        mocker.patch.object(im_act.client, "get", return_value=mock_response)
        params = DownloadJsonParams(
            source_url="http://test.url/streams/v1/index.json"
        )

        # Act
        act_env = ActivityEnvironment()
        result = await act_env.run(im_act.download_json, params)

        # Assert
        assert result["json"] == {"foo": "bar"}
        assert result["signed_by_cpc"] is False

    @pytest.mark.asyncio
    async def test_download_json_signed(
        self, im_act: ImageManagementActivity, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = b'"signed-content"'
        mocker.patch.object(im_act.client, "get", return_value=mock_response)
        # Patch read_signed to return JSON string and True
        mocker.patch(
            "temporal.resources.activities.download_upstream_activities.read_signed",
            AsyncMock(return_value=('{"foo": "bar"}', True)),
        )
        params = DownloadJsonParams(
            source_url="http://test.url/streams/v1/index.sjson",
            keyring="keyring",
        )

        # Act
        act_env = ActivityEnvironment()
        result = await act_env.run(im_act.download_json, params)

        # Assert
        assert result["json"] == {"foo": "bar"}
        assert result["signed_by_cpc"] is True

    @pytest.mark.asyncio
    async def test_download_json_http_error(
        self, im_act: ImageManagementActivity, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mocker.patch.object(im_act.client, "get", return_value=mock_response)
        params = DownloadJsonParams(
            source_url="http://test.url/streams/v1/index.json"
        )

        # Act & Assert
        act_env = ActivityEnvironment()
        with pytest.raises(Exception) as excinfo:
            await act_env.run(im_act.download_json, params)
        assert "Failed to download JSON" in str(excinfo.value)


class TestParseSsIndexActivity:
    @pytest.mark.asyncio
    async def test_parse_ss_index_valid(
        self, im_act: ImageManagementActivity
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        index_url = "http://example.com/streams/v1/index.sjson"
        params = ParseSsIndexParams(
            index_url=index_url,
            content={
                "index": {
                    "prod1": {
                        "format": "products:1.0",
                        "path": "streams/v1/prod1.json",
                    },
                    "prod2": {
                        "format": "products:1.0",
                        "path": "streams/v1/prod2.json",
                    },
                    "other": {
                        "format": "other:1.0",
                        "path": "streams/v1/other.json",
                    },
                }
            },
        )

        # Act
        base_url, products = await act_env.run(im_act.parse_ss_index, params)

        # Assert
        assert base_url == "http://example.com/"
        assert "http://example.com/streams/v1/prod1.json" in products
        assert "http://example.com/streams/v1/prod2.json" in products
        assert all("other.json" not in p for p in products)

    @pytest.mark.asyncio
    async def test_parse_ss_index_empty_index(
        self, im_act: ImageManagementActivity
    ) -> None:
        act_env = ActivityEnvironment()
        params = ParseSsIndexParams(
            index_url="http://example.com/streams/v1/index.sjson",
            content={"index": {}},
        )

        base_url, products = await act_env.run(im_act.parse_ss_index, params)
        assert base_url == "http://example.com/"
        assert products == []

    @pytest.mark.asyncio
    async def test_parse_ss_index_missing_index(
        self, im_act: ImageManagementActivity
    ) -> None:
        act_env = ActivityEnvironment()
        params = ParseSsIndexParams(
            index_url="http://example.com/streams/v1/index.sjson",
            content={},
        )

        base_url, products = await act_env.run(im_act.parse_ss_index, params)
        assert base_url == "http://example.com/"
        assert products == []


class TestLoadProductMapActivity:
    @pytest.mark.asyncio
    async def test_load_product_map_valid(
        self, im_act: ImageManagementActivity
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        products = {
            "products": {
                "prod1": {
                    "arch": "amd64",
                    "os": "ubuntu",
                    "release": "oracular",
                    "versions": {
                        "20250601": {
                            "items": {
                                "item1": {
                                    "sha256": "abc123",
                                    "path": "prod1/item1.img",
                                    "size": 12345,
                                    "ftype": "kernel",
                                    "source_package": "linux-image",
                                    "source_version": "1.0",
                                    "source_release": "24.04",
                                }
                            }
                        }
                    },
                }
            }
        }
        selections = {"ubuntu---oracular": ["amd64"]}
        params = LoadProductMapParams(
            products=products,
            selections=selections,
            canonical_source=True,
        )

        # Act
        result = await act_env.run(im_act.load_product_map, params)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        item = result[0]
        assert item["arch"] == "amd64"
        assert item["os"] == "ubuntu"
        assert item["release"] == "oracular"
        assert item["sha256"] == "abc123"
        assert item["path"] == "prod1/item1.img"
        assert item["file_size"] == 12345
        assert item["ftype"] == "kernel"
        assert item["source_package"] == "linux-image"
        assert item["source_version"] == "1.0"
        assert item["source_release"] == "24.04"

    @pytest.mark.asyncio
    async def test_load_product_map_no_matching_selection(
        self, im_act: ImageManagementActivity
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        products = {
            "products": {
                "prod1": {
                    "arch": "arm64",
                    "os": "ubuntu",
                    "release": "noble",
                    "versions": {
                        "20250601": {
                            "items": {
                                "item1": {
                                    "sha256": "abc123",
                                    "path": "prod1/item1.img",
                                    "size": 12345,
                                    "ftype": "kernel",
                                }
                            }
                        }
                    },
                }
            }
        }
        selections = {"ubuntu---noble": ["amd64"]}
        params = LoadProductMapParams(
            products=products,
            selections=selections,
            canonical_source=True,
        )

        # Act
        result = await act_env.run(im_act.load_product_map, params)

        # Assert
        assert result == []
