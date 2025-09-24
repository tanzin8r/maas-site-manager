from datetime import timedelta

from temporalio import workflow

from msm.common.workflows.sync import (
    DOWNLOAD_UPSTREAM_IMAGE_WF_NAME,
    DownloadUpstreamImageParams,
)
import msm.temporal.activities as act

MSM_API_TIMEOUT = timedelta(minutes=2)


@workflow.defn(name=DOWNLOAD_UPSTREAM_IMAGE_WF_NAME, sandboxed=False)
class DownloadUpstreamImageWorkflow:
    @workflow.run
    async def run(self, params: DownloadUpstreamImageParams) -> bool:
        item: act.GetBootAssetItemResult = await workflow.execute_activity(
            act.GET_BOOT_ASSET_ITEM_ACTIVITY,
            act.GetBootAssetItemParams(
                msm_base_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_asset_item_id=params.boot_asset_item_id,
            ),
            result_type=act.GetBootAssetItemResult,
            start_to_close_timeout=MSM_API_TIMEOUT,
        )

        if item.bytes_synced == item.file_size:
            return True

        bytes_synced: int = await workflow.execute_activity(
            act.DOWNLOAD_ASSET_ACTIVITY,
            act.DownloadAssetParams(
                ss_url="/".join([params.ss_root_url, item.path]),
                msm_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_asset_item_id=params.boot_asset_item_id,
                s3_params=params.s3_params,
            ),
            result_type=int,
            start_to_close_timeout=timedelta(minutes=params.timeout),
        )
        return bool(bytes_synced == item.file_size)
