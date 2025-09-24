from httpx import AsyncClient, Response
import pytest
from pytest_mock import MockerFixture, MockType
from temporalio.testing import ActivityEnvironment

from msm.common.enums import BootAssetKind, BootAssetLabel
from msm.temporal.activities.bootasset import (
    BootAssetActivities,
    GetBootSourceParams,
    PutAssetListParams,
    PutAssetListResult,
    PutAvailableAssetListParams,
)
from msm.temporal.activities.simplestream import (
    AvailableAsset,
    Product,
)
from tests import AsyncIterator


@pytest.fixture
def mock_client(mocker: MockerFixture) -> MockType:
    return mocker.create_autospec(AsyncClient)


@pytest.fixture
def ba_act(
    mocker: MockerFixture, mock_client: MockType
) -> BootAssetActivities:
    mock_response = mocker.create_autospec(Response)
    mock_response.aiter_bytes.return_value = AsyncIterator([b"abc", b"def"])

    mock_client.stream.return_value.__aenter__.return_value = mock_response
    mocker.patch.object(
        BootAssetActivities, "_create_client", return_value=mock_client
    )
    return BootAssetActivities()


class TestGetBootSourceActivity:
    @pytest.mark.asyncio
    async def test_get_boot_source_success(
        self,
        mocker: MockerFixture,
        ba_act: BootAssetActivities,
        mock_client: MockType,
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
            "priority": 10,
            "sync_interval": 3600,
            "last_sync": "2023-01-01T00:00:00Z",
        }

        selections_response = mocker.Mock()
        selections_response.status_code = 200
        selections_response.json.return_value = {
            "total": 3,
            "page": 1,
            "size": 3,
            "items": [
                {
                    "id": 1,
                    "boot_source_id": 42,
                    "label": "stable",
                    "selected": True,
                    "os": "ubuntu",
                    "release": "oracular",
                    "arch": "amd64",
                },
                {
                    "id": 2,
                    "boot_source_id": 42,
                    "label": "stable",
                    "selected": True,
                    "os": "ubuntu",
                    "release": "oracular",
                    "arch": "arm64",
                },
                {
                    "id": 3,
                    "boot_source_id": 42,
                    "label": "stable",
                    "selected": True,
                    "os": "ubuntu",
                    "release": "questing",
                    "arch": "amd64",
                },
            ],
        }

        # Patch the client.get method to return the correct response in order
        mock_client.get.side_effect = [
            boot_source_response,
            selections_response,
        ]

        # Act
        result = await act_env.run(ba_act.get_boot_source, params)

        # Assert
        assert (
            result.index_url == "http://test.source.url/streams/v1/index.sjson"
        )
        assert result.keyring == "test-keyring"
        assert result.selections == [
            "ubuntu---oracular---amd64",
            "ubuntu---oracular---arm64",
            "ubuntu---questing---amd64",
        ]

    @pytest.mark.asyncio
    async def test_get_boot_source_failure(
        self,
        mocker: MockerFixture,
        ba_act: BootAssetActivities,
        mock_client: MockType,
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
        mock_client.get.return_value = fail_response

        with pytest.raises(Exception):
            await act_env.run(ba_act.get_boot_source, params)


@pytest.mark.asyncio
class TestPatchAvailableAssetsActivity:
    async def test_patch_asset_list_success(
        self,
        ba_act: BootAssetActivities,
        mocker: MockerFixture,
        mock_client: MockType,
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        params = PutAvailableAssetListParams(
            msm_base_url="http://msm.example.com",
            msm_jwt="jwt-token",
            boot_source_id=1,
            available=[
                AvailableAsset("ubuntu", "oracular", "candidate", "amd64"),
                AvailableAsset("ubuntu", "jammy", "candidate", "amd64"),
            ],
        )
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = 200
        mock_client.put.return_value = mock_response

        # Act
        result = await act_env.run(ba_act.put_available_asset_list, params)

        # Assert
        assert result is True
        mock_client.put.assert_called_once()
        call_args = mock_client.put.call_args
        assert call_args is not None
        _, kwargs = call_args
        assert kwargs["json"].available[0].os == "ubuntu"

    async def test_patch_asset_list_failure(
        self,
        ba_act: BootAssetActivities,
        mocker: MockerFixture,
        mock_client: MockType,
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        params = PutAvailableAssetListParams(
            msm_base_url="http://msm.example.com",
            msm_jwt="jwt-token",
            boot_source_id=1,
            available=[
                AvailableAsset("ubuntu", "oracular", "candidate", "amd64"),
            ],
        )
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_client.put.return_value = mock_response

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            await act_env.run(ba_act.put_available_asset_list, params)
        assert "Failed to update available asset list" in str(excinfo.value)


@pytest.mark.asyncio
class TestPutNewAssetsActivity:
    async def test_put_asset_list_success(
        self,
        ba_act: BootAssetActivities,
        mocker: MockerFixture,
        mock_client: MockType,
    ) -> None:
        act_env = ActivityEnvironment()
        params = PutAssetListParams(
            msm_base_url="http://msm.example.com",
            msm_jwt="jwt-token",
            boot_source_id=1,
            items=[
                Product(
                    kind=BootAssetKind.OS,
                    os="ubuntu",
                    release="oracular",
                    arch="amd64",
                    label=BootAssetLabel.CANDIDATE,
                    title="Ubuntu Oracular",
                    versions={},
                )
            ],
        )
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"to_download": [101, 102]}
        mock_client.put.return_value = mock_response

        result = await act_env.run(ba_act.put_asset_list, params)
        assert isinstance(result, PutAssetListResult)
        assert result.to_download == [101, 102]
        mock_client.put.assert_called_once()

    async def test_put_asset_list_failure(
        self,
        ba_act: BootAssetActivities,
        mocker: MockerFixture,
        mock_client: MockType,
    ) -> None:
        act_env = ActivityEnvironment()
        params = PutAssetListParams(
            msm_base_url="http://msm.example.com",
            msm_jwt="jwt-token",
            boot_source_id=1,
            items=[
                Product(
                    kind=BootAssetKind.OS,
                    os="ubuntu",
                    release="oracular",
                    arch="amd64",
                    label=BootAssetLabel.CANDIDATE,
                    title="Ubuntu Oracular",
                    versions={},
                )
            ],
        )
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_client.put.return_value = mock_response

        with pytest.raises(Exception) as excinfo:
            await act_env.run(ba_act.put_asset_list, params)
        assert "Failed to update assets" in str(excinfo.value)
