import typing
from unittest.mock import PropertyMock

from activities.images import (  # type: ignore
    DownloadAssetParams,
    ImageManagementActivities,
    S3Params,
    S3ResourceManager,
)
from httpx import AsyncClient, Response
from mypy_boto3_s3 import S3Client
import pytest
from pytest_mock import MockerFixture, MockType
from temporalio.testing import ActivityEnvironment

from temporal.tests.activities import AsyncIterator


@pytest.fixture
def image_data() -> bytes:
    return b"abcdef"


@pytest.fixture
def s3_client(mocker: MockerFixture) -> MockType:
    mock_s3 = mocker.create_autospec(S3Client)
    mocker.patch.object(
        S3ResourceManager,
        "s3_client",
        new_callable=PropertyMock(return_value=mock_s3),
    )
    return mock_s3


@pytest.fixture
def s3_params() -> S3Params:
    return S3Params(
        endpoint="http://s3",
        access_key="test-key",
        secret_key="test-secret-key",
        bucket="test-bucket",
        path="test/path",
    )


@pytest.fixture
async def im_act(
    mocker: MockerFixture, image_data: bytes
) -> ImageManagementActivities:
    mock_response = mocker.create_autospec(Response)
    mock_response.aiter_raw.return_value = AsyncIterator([image_data])

    mock_client = mocker.create_autospec(AsyncClient)
    mock_client.stream.return_value.__aenter__.return_value = mock_response
    mocker.patch.object(
        ImageManagementActivities, "_create_client", return_value=mock_client
    )
    return ImageManagementActivities()


class TestDownloadUpstreamActivities:
    async def test_download_asset(
        self,
        mocker: MockerFixture,
        im_act: typing.Any,
        s3_client: MockType,
        s3_params: S3Params,
        image_data: bytes,
    ) -> None:
        mocker.patch.object(
            S3ResourceManager,
            "bytes_sent",
            new_callable=PropertyMock(return_value=len(image_data)),
        )
        item_id = 1
        s3_manager = S3ResourceManager(s3_params, item_id)
        mocker.patch.object(
            im_act, "_create_s3_manager", return_value=s3_manager
        )

        mock_response = mocker.create_autospec(Response)
        type(mock_response).status_code = PropertyMock(return_value=200)
        im_act.client.patch.return_value = mock_response

        act_env = ActivityEnvironment()
        params = DownloadAssetParams(
            ss_url="http://test.ss.url",
            msm_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            boot_asset_item_id=item_id,
            s3_params=s3_params,
        )

        result = await act_env.run(im_act.download_asset, params)
        assert result == len(image_data)
        s3_client.create_multipart_upload.assert_called_once()
        s3_client.upload_part.assert_called_once()
        assert s3_client.upload_part.call_args.kwargs["Body"] == b"abcdef"
        s3_client.complete_multipart_upload.assert_called_once()
        s3_client.abort_multipart_upload.assert_not_called()
        im_act.client.patch.assert_called_once_with(
            f"{params.msm_url}/api/v1/bootasset-items/{item_id}",
            headers={"Authorization": f"bearer {params.msm_jwt}"},
            json={"bytes_synced": len(image_data)},
        )

    async def test_download_asset_item_deleted(
        self,
        mocker: MockerFixture,
        im_act: typing.Any,
        s3_client: MockType,
        s3_params: S3Params,
        image_data: bytes,
    ) -> None:
        mocker.patch.object(
            S3ResourceManager,
            "bytes_sent",
            new_callable=PropertyMock(return_value=len(image_data)),
        )
        item_id = 1
        s3_manager = S3ResourceManager(s3_params, item_id)
        mocker.patch.object(
            im_act, "_create_s3_manager", return_value=s3_manager
        )

        mock_response = mocker.create_autospec(Response)
        type(mock_response).status_code = PropertyMock(return_value=404)
        im_act.client.patch.return_value = mock_response

        act_env = ActivityEnvironment()
        params = DownloadAssetParams(
            ss_url="http://test.ss.url",
            msm_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            boot_asset_item_id=item_id,
            s3_params=s3_params,
        )

        result = await act_env.run(im_act.download_asset, params)

        assert result == -1
        s3_client.create_multipart_upload.assert_called_once()
        s3_client.upload_part.assert_called_once()
        assert s3_client.upload_part.call_args.kwargs["Body"] == b"abcdef"
        s3_client.complete_multipart_upload.assert_not_called()
        s3_client.abort_multipart_upload.assert_called_once()
        im_act.client.patch.assert_called_once_with(
            f"{params.msm_url}/api/v1/bootasset-items/{item_id}",
            headers={"Authorization": f"bearer {params.msm_jwt}"},
            json={"bytes_synced": len(image_data)},
        )

    async def test_download_asset_is_aborted(
        self,
        mocker: MockerFixture,
        im_act: typing.Any,
        s3_client: MockType,
        s3_params: S3Params,
    ) -> None:
        mocker.patch.object(
            S3ResourceManager, "upload_part", side_effect=RuntimeError
        )
        item_id = 1
        s3_manager = S3ResourceManager(s3_params, item_id)
        mocker.patch.object(
            im_act, "_create_s3_manager", return_value=s3_manager
        )
        act_env = ActivityEnvironment()
        params = DownloadAssetParams(
            ss_url="http://test.ss.url",
            msm_url="http://test.msm.url",
            msm_jwt="test.msm.jwt",
            boot_asset_item_id=1,
            s3_params=s3_params,
        )
        with pytest.raises(RuntimeError):
            await act_env.run(im_act.download_asset, params)
        im_act._create_s3_manager.assert_called_with(params.s3_params, 1)

        s3_client.create_multipart_upload.assert_called_once()
        s3_client.complete_multipart_upload.assert_not_called()
        s3_client.abort_multipart_upload.assert_called_once()
