from datetime import UTC, datetime, timedelta
import typing
import uuid

from pydantic import AwareDatetime
import pytest
from temporalio import activity
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from msm.common.api.bootassets import AssetVersions
from msm.common.workflows.sync import (
    DeleteItemsParams,
    RemoveStaleImagesParams,
    S3Params,
)
from msm.temporal.activities.bootasset import (
    GET_SOURCE_LAST_SYNC_ACTIVITY,
    GET_SOURCE_VERSIONS_ACTIVITY,
    REMOVE_STALE_VERSIONS_ACTIVITY,
    GetSourceLastSyncParams,
    GetSourceVersionsParams,
    GetSourceVersionsResult,
    RemoveStaleVersionsParams,
)
from msm.temporal.activities.images import (
    DELETE_ITEM_ACTIVITY,
    DeleteItemParams,
)
from msm.temporal.workflows import (
    DeleteItemsWorkflow,
    RemoveStaleImagesWorkflow,
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
def delete_items_params(s3_params: S3Params) -> DeleteItemsParams:
    return DeleteItemsParams(
        s3_params=s3_params,
        item_ids=[1, 2, 3],
    )


@pytest.fixture
def remove_stale_images_params() -> RemoveStaleImagesParams:
    return RemoveStaleImagesParams(
        msm_url="http://test.url",
        msm_jwt="test.jwt",
        boot_source_id=1,
        versions_to_keep=2,
    )


class TestDeleteItemsWorkflow:
    @pytest.mark.asyncio
    async def test_delete_items(
        self,
        delete_items_params: DeleteItemsParams,
    ) -> None:
        item_ids = []

        @activity.defn(name=DELETE_ITEM_ACTIVITY)
        async def delete_item_activity(
            params: DeleteItemParams,
        ) -> None:
            nonlocal item_ids
            item_ids.append(params.boot_asset_item_id)
            return

        # Act
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue="msm-queue",
                debug_mode=True,
                workflows=[DeleteItemsWorkflow],
                activities=[
                    delete_item_activity,
                ],
            ) as worker:
                await env.client.execute_workflow(
                    DeleteItemsWorkflow.run,
                    delete_items_params,
                    id=f"workflow-{uuid.uuid4()}",
                    task_queue=worker.task_queue,
                    run_timeout=TEST_WF_TIMEOUT,
                )
        item_ids.sort()
        assert item_ids == delete_items_params.item_ids


class TestRemoveStaleImagesWorkflow:
    @pytest.mark.asyncio
    async def test_remove_stale_images(
        self,
        remove_stale_images_params: RemoveStaleImagesParams,
        source_assets: dict[str, typing.Any],
    ) -> None:
        versions: list[AssetVersions] = []
        returned_versions = [
            AssetVersions.from_dict(p) for p in source_assets["versions"]
        ]
        last_sync = datetime.now(UTC)
        stale_versions_last_sync = None

        @activity.defn(name=GET_SOURCE_VERSIONS_ACTIVITY)
        async def get_source_versions_activity(
            params: GetSourceVersionsParams,
        ) -> GetSourceVersionsResult:
            return GetSourceVersionsResult(versions=returned_versions)

        @activity.defn(name=GET_SOURCE_LAST_SYNC_ACTIVITY)
        async def get_source_last_sync_activity(
            params: GetSourceLastSyncParams,
        ) -> AwareDatetime:
            return last_sync

        @activity.defn(name=REMOVE_STALE_VERSIONS_ACTIVITY)
        async def remove_stale_versions_activity(
            params: RemoveStaleVersionsParams,
        ) -> None:
            nonlocal versions
            nonlocal stale_versions_last_sync
            stale_versions_last_sync = params.source_last_sync
            versions += params.versions

        async with await WorkflowEnvironment.start_time_skipping(
            data_converter=pydantic_data_converter
        ) as env:
            async with Worker(
                env.client,
                task_queue="msm-queue",
                debug_mode=True,
                workflows=[RemoveStaleImagesWorkflow],
                activities=[
                    get_source_versions_activity,
                    get_source_last_sync_activity,
                    remove_stale_versions_activity,
                ],
            ) as worker:
                await env.client.execute_workflow(
                    RemoveStaleImagesWorkflow.run,
                    remove_stale_images_params,
                    id=f"workflow-{uuid.uuid4()}",
                    task_queue=worker.task_queue,
                    run_timeout=TEST_WF_TIMEOUT,
                )
        assert versions == returned_versions
        assert stale_versions_last_sync == last_sync
