from datetime import timedelta
import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from msm.common.workflows.sync import (
    DownloadUpstreamImageParams,
    S3Params,
)
from msm.temporal.activities.bootasset import (
    GET_BOOT_ASSET_ITEM_ACTIVITY,
    GetBootAssetItemParams,
    GetBootAssetItemResult,
)
from msm.temporal.activities.images import (
    DOWNLOAD_ASSET_ACTIVITY,
    DownloadAssetParams,
)
from msm.temporal.workflows import DownloadUpstreamImageWorkflow

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
def wf_params(s3_params: S3Params) -> DownloadUpstreamImageParams:
    return DownloadUpstreamImageParams(
        ss_root_url="http://stable.images.com",
        msm_url="http://msm.example.com",
        msm_jwt="jwt-token",
        boot_asset_item_id=1,
        s3_params=s3_params,
    )


class TestDownloadUpstreamImageWorkflow:
    @pytest.mark.asyncio
    async def test_download_success(
        self,
        wf_params: DownloadUpstreamImageParams,
    ) -> None:
        download_url = ""
        remote_path = "bootloaders/uefi/amd64/20210819.0/shim-signed.tar.xz"
        file_size = 1234123

        # Mock activities
        @activity.defn(name=GET_BOOT_ASSET_ITEM_ACTIVITY)
        async def get_boot_asset_item_activity(
            params: GetBootAssetItemParams,
        ) -> GetBootAssetItemResult:
            return GetBootAssetItemResult(
                path=remote_path,
                sha256="07b42d0aa2540b6999c726eacf383e2c8f172378c964bdefab6d71410e2b72db",
                file_size=file_size,
                bytes_synced=0,
            )

        @activity.defn(name=DOWNLOAD_ASSET_ACTIVITY)
        async def download_asset_activity(
            params: DownloadAssetParams,
        ) -> int:
            nonlocal download_url
            download_url = params.ss_url
            return file_size

        # Act
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue="msm-queue",
                debug_mode=True,
                workflows=[DownloadUpstreamImageWorkflow],
                activities=[
                    get_boot_asset_item_activity,
                    download_asset_activity,
                ],
            ) as worker:
                result = await env.client.execute_workflow(
                    DownloadUpstreamImageWorkflow.run,
                    wf_params,
                    id=f"workflow-{uuid.uuid4()}",
                    task_queue=worker.task_queue,
                    run_timeout=TEST_WF_TIMEOUT,
                )

        # Assert
        assert result is True
        assert download_url == f"{wf_params.ss_root_url}/{remote_path}"

    @pytest.mark.asyncio
    async def test_already_complete(
        self,
        wf_params: DownloadUpstreamImageParams,
    ) -> None:
        download_called = False
        file_size = 1234123

        # Mock activities
        @activity.defn(name=GET_BOOT_ASSET_ITEM_ACTIVITY)
        async def get_boot_asset_item_activity(
            params: GetBootAssetItemParams,
        ) -> GetBootAssetItemResult:
            return GetBootAssetItemResult(
                path="bootloaders/uefi/amd64/20210819.0/shim-signed.tar.xz",
                sha256="07b42d0aa2540b6999c726eacf383e2c8f172378c964bdefab6d71410e2b72db",
                file_size=file_size,
                bytes_synced=file_size,
            )

        @activity.defn(name=DOWNLOAD_ASSET_ACTIVITY)
        async def download_asset_activity(
            params: DownloadAssetParams,
        ) -> int:
            nonlocal download_called
            download_called = True
            return file_size

        # Act
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue="msm-queue",
                debug_mode=True,
                workflows=[DownloadUpstreamImageWorkflow],
                activities=[
                    get_boot_asset_item_activity,
                    download_asset_activity,
                ],
            ) as worker:
                result = await env.client.execute_workflow(
                    DownloadUpstreamImageWorkflow.run,
                    wf_params,
                    id=f"workflow-{uuid.uuid4()}",
                    task_queue=worker.task_queue,
                    run_timeout=TEST_WF_TIMEOUT,
                )

        # Assert
        assert result is True
        assert download_called is False
