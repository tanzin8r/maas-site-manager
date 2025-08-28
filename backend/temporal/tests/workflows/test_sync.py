from datetime import timedelta
import typing
import uuid

from activities.bootasset import (  # type: ignore
    GET_BOOT_SOURCE_ACTIVITY,
    PUT_AVAILABLE_ASSETS_ACTIVITY,
    PUT_NEW_ASSETS_ACTIVITY,
    GetBootSourceParams,
    GetBootSourceResult,
    PutAssetListParams,
    PutAssetListResult,
    PutAvailableAssetListParams,
)
from activities.images import S3Params  # type: ignore
from activities.simplestream import (  # type: ignore
    FETCH_SS_ASSETS_ACTIVITY,
    FETCH_SS_INDEXES,
    LOAD_PRODUCT_MAP_ACTIVITY,
    AvailableAsset,
    BootAssetKind,
    BootAssetLabel,
    FetchAssetListParams,
    FetchAssetListResult,
    FetchSsIndexesParams,
    FetchSsIndexesResult,
    LoadProductMapParams,
    LoadProductMapResult,
    Product,
)
import pytest
from pytest_mock import MockerFixture
from temporalio import activity
from temporalio.exceptions import ApplicationError, WorkflowAlreadyStartedError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal.resources.workflows.sync import (
    RefreshUpstreamSourceParams,
    RefreshUpstreamSourceWorkflow,
    SyncUpstreamSourceParams,
    SyncUpstreamSourceWorkflow,
)

TEST_WF_TIMEOUT = timedelta(seconds=30)


@pytest.fixture
def s3_params() -> S3Params:
    return S3Params(
        endpoint="https://radosgw.ceph.example.com",
        access_key="test-access",
        secret_key="test-secret",
        bucket="test-bucket",
        path="images/",
    )


@pytest.fixture
def sync_params(s3_params: S3Params) -> SyncUpstreamSourceParams:
    return SyncUpstreamSourceParams(
        msm_url="http://msm.example.com",
        msm_jwt="jwt-token",
        boot_source_id=1,
        s3_params=s3_params,
    )


@pytest.fixture
def refresh_params() -> RefreshUpstreamSourceParams:
    return RefreshUpstreamSourceParams(
        msm_url="http://msm.example.com",
        msm_jwt="jwt-token",
        boot_source_id=1,
    )


@pytest.fixture
def boot_source_data() -> dict[str, typing.Any]:
    return {
        "boot-source": {
            "url": "http://upstream.example.com/streams/v1/index.sjson",
            "keyring": None,
        },
        "selections": {"ubuntu---noble---amd64"},
    }


@pytest.fixture
def available_assets() -> list[AvailableAsset]:
    return [
        AvailableAsset("ubuntu", "oracular", "candidate", "amd64"),
        AvailableAsset("ubuntu", "oracular", "candidate", "ppc64el"),
        AvailableAsset("ubuntu", "jammy", "candidate", "s390x"),
    ]


@pytest.fixture
def product_list() -> list[Product]:
    return [
        Product(
            kind=BootAssetKind.OS,
            label=BootAssetLabel.STABLE,
            os="ubuntu",
            release="noble",
            arch="amd64",
        )
    ]


class TestSyncUpstreamSourceWorkflow:
    @pytest.mark.asyncio
    async def test_success(
        self,
        sync_params: SyncUpstreamSourceParams,
        boot_source_data: dict[str, typing.Any],
        product_list: list[Product],
        mocker: MockerFixture,
    ) -> None:
        # Mock activities
        @activity.defn(name=GET_BOOT_SOURCE_ACTIVITY)
        async def get_boot_source_data_mock(
            params: GetBootSourceParams,
        ) -> GetBootSourceResult:
            return GetBootSourceResult(
                index_url=boot_source_data["boot-source"]["url"],
                keyring=boot_source_data["boot-source"]["keyring"],
                selections=boot_source_data["selections"],
            )

        @activity.defn(name=FETCH_SS_INDEXES)
        async def parse_ss_index_mock(
            params: FetchSsIndexesParams,
        ) -> FetchSsIndexesResult:
            assert (
                params.index_url
                == "http://upstream.example.com/streams/v1/index.sjson"
            )
            return FetchSsIndexesResult(
                "http://upstream.example.com/",
                True,
                ["http://upstream.example.com/streams/v1/prod1.json"],
            )

        @activity.defn(name=LOAD_PRODUCT_MAP_ACTIVITY)
        async def load_product_map_mock(
            params: LoadProductMapParams,
        ) -> LoadProductMapResult:
            if (
                params.index_url
                == "http://upstream.example.com/streams/v1/prod1.json"
            ):
                return LoadProductMapResult(items=product_list)
            raise ApplicationError("Unexpected URL", non_retryable=True)

        @activity.defn(name=PUT_NEW_ASSETS_ACTIVITY)
        async def put_asset_list_mock(
            params: PutAssetListParams,
        ) -> PutAssetListResult:
            return PutAssetListResult(to_download=[1])

        mock_start_download = mocker.patch.object(
            SyncUpstreamSourceWorkflow, "start_download"
        )

        # Act
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue="msm-queue",
                workflows=[SyncUpstreamSourceWorkflow],
                activities=[
                    get_boot_source_data_mock,
                    parse_ss_index_mock,
                    load_product_map_mock,
                    put_asset_list_mock,
                ],
            ) as worker:
                result = await env.client.execute_workflow(
                    SyncUpstreamSourceWorkflow.run,
                    sync_params,
                    id=f"workflow-{uuid.uuid4()}",
                    task_queue=worker.task_queue,
                    run_timeout=TEST_WF_TIMEOUT,
                )

        # Assert
        assert result is True
        mock_start_download.assert_called_once()

    @pytest.mark.asyncio
    async def test_success_download_in_progress(
        self,
        sync_params: SyncUpstreamSourceParams,
        boot_source_data: dict[str, typing.Any],
        product_list: list[Product],
        mocker: MockerFixture,
    ) -> None:
        # Mock activities
        @activity.defn(name=GET_BOOT_SOURCE_ACTIVITY)
        async def get_boot_source_data_mock(
            params: GetBootSourceParams,
        ) -> GetBootSourceResult:
            return GetBootSourceResult(
                index_url=boot_source_data["boot-source"]["url"],
                keyring=boot_source_data["boot-source"]["keyring"],
                selections=boot_source_data["selections"],
            )

        @activity.defn(name=FETCH_SS_INDEXES)
        async def parse_ss_index_mock(
            params: FetchSsIndexesParams,
        ) -> FetchSsIndexesResult:
            assert (
                params.index_url
                == "http://upstream.example.com/streams/v1/index.sjson"
            )
            return FetchSsIndexesResult(
                "http://upstream.example.com/",
                True,
                ["http://upstream.example.com/streams/v1/prod1.json"],
            )

        @activity.defn(name=LOAD_PRODUCT_MAP_ACTIVITY)
        async def load_product_map_mock(
            params: LoadProductMapParams,
        ) -> LoadProductMapResult:
            if (
                params.index_url
                == "http://upstream.example.com/streams/v1/prod1.json"
            ):
                return LoadProductMapResult(items=product_list)
            raise ApplicationError("Unexpected URL", non_retryable=True)

        @activity.defn(name=PUT_NEW_ASSETS_ACTIVITY)
        async def put_asset_list_mock(
            params: PutAssetListParams,
        ) -> PutAssetListResult:
            return PutAssetListResult(to_download=[1])

        mock_start_download = mocker.patch.object(
            SyncUpstreamSourceWorkflow,
            "start_download",
            side_effect=WorkflowAlreadyStartedError("", ""),
        )

        # Act
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue="msm-queue",
                workflows=[SyncUpstreamSourceWorkflow],
                activities=[
                    get_boot_source_data_mock,
                    parse_ss_index_mock,
                    load_product_map_mock,
                    put_asset_list_mock,
                ],
            ) as worker:
                result = await env.client.execute_workflow(
                    SyncUpstreamSourceWorkflow.run,
                    sync_params,
                    id=f"workflow-{uuid.uuid4()}",
                    task_queue=worker.task_queue,
                    run_timeout=TEST_WF_TIMEOUT,
                )

        # Assert
        assert result is True
        mock_start_download.assert_called_once()


class TestRefreshUpstreamSourceWorkflow:
    @pytest.mark.asyncio
    async def test_refresh_upstream_source_success(
        self,
        refresh_params: RefreshUpstreamSourceParams,
        boot_source_data: dict[str, typing.Any],
        available_assets: list[AvailableAsset],
    ) -> None:
        # Mock activities
        @activity.defn(name=GET_BOOT_SOURCE_ACTIVITY)
        async def get_boot_source_data(
            params: GetBootSourceParams,
        ) -> GetBootSourceResult:
            return GetBootSourceResult(
                index_url=boot_source_data["boot-source"]["url"],
                keyring=boot_source_data["boot-source"]["keyring"],
            )

        @activity.defn(name=FETCH_SS_ASSETS_ACTIVITY)
        async def fetch_ss_asset_list(
            params: FetchAssetListParams,
        ) -> FetchAssetListResult:
            return FetchAssetListResult(assets=available_assets)

        @activity.defn(name=PUT_AVAILABLE_ASSETS_ACTIVITY)
        async def put_available_asset_list(
            params: PutAvailableAssetListParams,
        ) -> bool:
            return bool(params.available == available_assets)

        # Act
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue="msm-queue",
                debug_mode=True,
                workflows=[RefreshUpstreamSourceWorkflow],
                activities=[
                    get_boot_source_data,
                    fetch_ss_asset_list,
                    put_available_asset_list,
                ],
            ) as worker:
                result = await env.client.execute_workflow(
                    RefreshUpstreamSourceWorkflow.run,
                    refresh_params,
                    id=f"workflow-{uuid.uuid4()}",
                    task_queue=worker.task_queue,
                    run_timeout=TEST_WF_TIMEOUT,
                )

        # Assert
        assert result is True
