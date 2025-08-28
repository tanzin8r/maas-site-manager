from dataclasses import dataclass
from datetime import timedelta

from activities.bootasset import (  # type: ignore
    GET_BOOT_ASSET_ITEM_ACTIVITY,
    GetBootAssetItemParams,
    GetBootAssetItemResult,
)
from activities.images import (  # type: ignore
    DOWNLOAD_ASSET_ACTIVITY,
    DownloadAssetParams,
    S3Params,
)
from temporalio import workflow

DOWNLOAD_UPSTREAM_IMAGE_WF_NAME = "DownloadUpstreamImage"
MSM_API_TIMEOUT = timedelta(minutes=2)


@dataclass
class DownloadUpstreamImageParams:
    ss_root_url: str
    msm_url: str
    msm_jwt: str
    boot_asset_item_id: int
    s3_params: S3Params
    timeout: int = 120


@workflow.defn(name=DOWNLOAD_UPSTREAM_IMAGE_WF_NAME, sandboxed=False)
class DownloadUpstreamImageWorkflow:
    @workflow.run
    async def run(self, params: DownloadUpstreamImageParams) -> bool:
        item: GetBootAssetItemResult = await workflow.execute_activity(
            GET_BOOT_ASSET_ITEM_ACTIVITY,
            GetBootAssetItemParams(
                msm_base_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_asset_item_id=params.boot_asset_item_id,
            ),
            result_type=GetBootAssetItemResult,
            start_to_close_timeout=MSM_API_TIMEOUT,
        )

        if item.bytes_synced == item.file_size:
            return True

        bytes_synced: int = await workflow.execute_activity(
            DOWNLOAD_ASSET_ACTIVITY,
            DownloadAssetParams(
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
