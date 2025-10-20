from datetime import UTC, datetime, timedelta
import typing

from httpx import AsyncClient, Response
import pytest
from pytest_mock import MockerFixture, MockType
from temporalio.testing import ActivityEnvironment

from msm.common.api.bootassets import AssetVersions
from msm.common.enums import BootAssetKind, BootAssetLabel
from msm.temporal.activities.bootasset import (
    BootAssetActivities,
    GetBootSourceParams,
    GetSourceLastSyncParams,
    GetSourceVersionsParams,
    GetSourceVersionsResult,
    PutAssetListParams,
    PutAssetListResult,
    PutAvailableAssetListParams,
    RemoveStaleVersionsParams,
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
                AvailableAsset(
                    os="ubuntu",
                    release="oracular",
                    label="candidate",
                    arch="amd64",
                ),
                AvailableAsset(
                    os="ubuntu",
                    release="jammy",
                    label="candidate",
                    arch="amd64",
                ),
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
        assert kwargs["json"]["available"][0]["os"] == "ubuntu"

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
                AvailableAsset(
                    os="ubuntu",
                    release="oracular",
                    label="candidate",
                    arch="amd64",
                ),
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


@pytest.mark.asyncio
class TestGetSourceVersionsActivity:
    async def test_get_source_versions_success(
        self,
        mocker: MockerFixture,
        ba_act: BootAssetActivities,
        mock_client: MockType,
        source_assets: dict[str, typing.Any],
    ) -> None:
        act_env = ActivityEnvironment()

        params = GetSourceVersionsParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            boot_source_id=42,
        )

        # mock response
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = source_assets
        mock_client.get.return_value = mock_response

        result = await act_env.run(ba_act.get_source_versions, params)
        assert isinstance(result, GetSourceVersionsResult)
        expected = GetSourceVersionsResult(
            versions=[
                AssetVersions.from_dict(p) for p in source_assets["versions"]
            ]
        )
        assert result == expected

    async def test_get_source_versions_failure(
        self,
        mocker: MockerFixture,
        ba_act: BootAssetActivities,
        mock_client: MockType,
    ) -> None:
        act_env = ActivityEnvironment()

        params = GetSourceVersionsParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            boot_source_id=42,
        )

        # mock response
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_client.get.return_value = mock_response

        with pytest.raises(Exception) as excinfo:
            await act_env.run(ba_act.get_source_versions, params)
        assert "Failed to retrieve versions" in str(excinfo.value)


@pytest.mark.asyncio
class TestGetSourceLastSyncActivity:
    async def test_get_last_sync_success(
        self,
        mocker: MockerFixture,
        ba_act: BootAssetActivities,
        mock_client: MockType,
    ) -> None:
        act_env = ActivityEnvironment()

        params = GetSourceLastSyncParams(
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
        mock_client.get.return_value = boot_source_response
        result = await act_env.run(ba_act.get_source_last_sync, params)
        assert isinstance(result, datetime)
        assert result == datetime.fromisoformat("2023-01-01T00:00:00Z")

    async def test_get_last_sync_failure(
        self,
        mocker: MockerFixture,
        ba_act: BootAssetActivities,
        mock_client: MockType,
    ) -> None:
        act_env = ActivityEnvironment()

        params = GetSourceLastSyncParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            boot_source_id=42,
        )

        fail_response = mocker.Mock()
        fail_response.status_code = 404
        fail_response.text = "Not found"
        mock_client.get.return_value = fail_response

        with pytest.raises(Exception) as excinfo:
            await act_env.run(ba_act.get_source_last_sync, params)

        assert "Failed to get boot source" in str(excinfo.value)


@pytest.mark.asyncio
class TestRemoveStaleVersionsActivity:
    async def test_remove_stale_versions_success(
        self,
        mocker: MockerFixture,
        ba_act: BootAssetActivities,
        mock_client: MockType,
        source_assets: dict[str, typing.Any],
    ) -> None:
        act_env = ActivityEnvironment()

        versions = [
            AssetVersions.from_dict(p) for p in source_assets["versions"]
        ]

        params = RemoveStaleVersionsParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            versions=versions,
            versions_to_keep=2,
            source_last_sync=datetime.now(UTC) - timedelta(hours=1),
        )

        # mock response
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        await act_env.run(ba_act.remove_stale_versions, params)

        mock_client.post.assert_called_once_with(
            "http://test.msm.url/api/v1/bootasset-versions:remove",
            headers=ba_act._get_header("test.jwt"),
            json={"to_remove": [{"asset_id": 1, "version": "20250716"}]},
        )

    async def test_remove_versions_missing_from_upstream(
        self,
        mocker: MockerFixture,
        ba_act: BootAssetActivities,
        mock_client: MockType,
        source_assets: dict[str, typing.Any],
    ) -> None:
        act_env = ActivityEnvironment()

        for k in source_assets["versions"][0]["versions"].keys():
            source_assets["versions"][0]["versions"][k]["last_seen"] = (
                datetime.now(UTC) - timedelta(hours=1)
            )

        versions = [
            AssetVersions.from_dict(p) for p in source_assets["versions"]
        ]

        params = RemoveStaleVersionsParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            versions=versions,
            versions_to_keep=2,
            source_last_sync=datetime.now(UTC),
        )

        # mock response
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        await act_env.run(ba_act.remove_stale_versions, params)

        mock_client.post.assert_called_once_with(
            "http://test.msm.url/api/v1/bootasset-versions:remove",
            headers=ba_act._get_header("test.jwt"),
            json={
                "to_remove": [
                    {"asset_id": 1, "version": "20250716"},
                    {"asset_id": 1, "version": "20250805"},
                    {"asset_id": 1, "version": "20250903"},
                ]
            },
        )

    async def test_remove_stale_versions_no_stale(
        self,
        ba_act: BootAssetActivities,
        mock_client: MockType,
        source_assets: dict[str, typing.Any],
    ) -> None:
        act_env = ActivityEnvironment()

        versions = [
            AssetVersions.from_dict(p) for p in source_assets["versions"]
        ]

        params = RemoveStaleVersionsParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            versions=versions,
            versions_to_keep=3,
            source_last_sync=datetime.now(UTC) - timedelta(hours=1),
        )
        await act_env.run(ba_act.remove_stale_versions, params)

        mock_client.post.assert_not_called()

    async def test_remove_stale_versions_failure(
        self,
        mocker: MockerFixture,
        ba_act: BootAssetActivities,
        mock_client: MockType,
        source_assets: dict[str, typing.Any],
    ) -> None:
        act_env = ActivityEnvironment()

        versions = [
            AssetVersions.from_dict(p) for p in source_assets["versions"]
        ]
        params = RemoveStaleVersionsParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            versions=versions,
            versions_to_keep=2,
            source_last_sync=datetime.now(UTC),
        )

        # mock response
        mock_response = mocker.Mock(spec=Response)
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_client.post.return_value = mock_response

        with pytest.raises(Exception) as excinfo:
            await act_env.run(ba_act.remove_stale_versions, params)
        assert "Failed to remove stale versions" in str(excinfo.value)
