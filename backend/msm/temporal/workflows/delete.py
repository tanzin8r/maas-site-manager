from asyncio import gather
from datetime import timedelta

from pydantic import AwareDatetime
from temporalio import workflow

from msm.common.workflows.sync import (
    DELETE_ITEMS_WF_NAME,
    REMOVE_STALE_IMAGES_WF_NAME,
    DeleteItemsParams,
    RemoveStaleImagesParams,
)
import msm.temporal.activities as act

S3_TIMEOUT = timedelta(seconds=15)
MSM_API_TIMEOUT = timedelta(minutes=2)


@workflow.defn(name=DELETE_ITEMS_WF_NAME, sandboxed=False)
class DeleteItemsWorkflow:
    """Delete Items from S3 storage."""

    @workflow.run
    async def run(self, params: DeleteItemsParams) -> None:
        hdls = [
            workflow.execute_activity(
                act.DELETE_ITEM_ACTIVITY,
                act.DeleteItemParams(
                    s3_params=params.s3_params,
                    boot_asset_item_id=id,
                ),
                start_to_close_timeout=S3_TIMEOUT,
            )
            for id in params.item_ids
        ]
        await gather(*hdls)


@workflow.defn(name=REMOVE_STALE_IMAGES_WF_NAME, sandboxed=False)
class RemoveStaleImagesWorkflow:
    """Remove stale images from MSM database and S3 storage.

    An image is deemed stale if two more recent versions exist
    and are fully downloaded.
    """

    @workflow.run
    async def run(self, params: RemoveStaleImagesParams) -> None:
        versions: act.GetSourceVersionsResult = (
            await workflow.execute_activity(
                act.GET_SOURCE_VERSIONS_ACTIVITY,
                act.GetSourceVersionsParams(
                    msm_base_url=params.msm_url,
                    msm_jwt=params.msm_jwt,
                    boot_source_id=params.boot_source_id,
                ),
                result_type=act.GetSourceVersionsResult,
                start_to_close_timeout=MSM_API_TIMEOUT,
            )
        )
        last_sync: AwareDatetime = await workflow.execute_activity(
            act.GET_SOURCE_LAST_SYNC_ACTIVITY,
            act.GetSourceLastSyncParams(
                msm_base_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_source_id=params.boot_source_id,
            ),
            result_type=AwareDatetime,
            start_to_close_timeout=MSM_API_TIMEOUT,
        )
        await workflow.execute_activity(
            act.REMOVE_STALE_VERSIONS_ACTIVITY,
            act.RemoveStaleVersionsParams(
                msm_base_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                versions=versions.versions,
                versions_to_keep=params.versions_to_keep,
                source_last_sync=last_sync,
            ),
            start_to_close_timeout=MSM_API_TIMEOUT,
        )
