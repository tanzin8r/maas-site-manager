from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities.download_upstream_activities import (  # type: ignore
        DOWNLOAD_ASSET_ACTIVITY,
        GET_OR_CREATE_ASSET_ACTIVITY,
        GET_OR_CREATE_ITEM_ACTIVITY,
        GET_OR_CREATE_VERSION_ACTIVITY,
        UPDATE_BYTES_SYNCED_ACTIVITY,
        BootAsset,
        BootAssetItem,
        BootAssetVersion,
        DownloadAssetParams,
        GetOrCreateAssetParams,
        GetOrCreateItemParams,
        GetOrCreateVersionParams,
        S3Params,
        UpdateBytesSyncedParams,
    )

DOWNLOAD_UPSTREAM_IMAGE_WF_NAME = "DownloadUpstreamImage"
GET_OR_CREATE_PRODUCT_WF_NAME = "GetOrCreateProduct"


@dataclass
class DownloadUpstreamImageParams:
    ss_url: str
    msm_url: str
    msm_jwt: str
    boot_asset_item_id: int
    s3_params: S3Params


@dataclass
class GetOrCreateProductParams:
    msm_base_url: str
    msm_jwt: str
    asset: BootAsset
    version: BootAssetVersion
    item: BootAssetItem


@workflow.defn(name=DOWNLOAD_UPSTREAM_IMAGE_WF_NAME)
class DownloadUpstreamImage:
    @workflow.run
    async def run(self, params: DownloadUpstreamImageParams) -> bool:
        bytes_synced = await workflow.execute_activity(
            DOWNLOAD_ASSET_ACTIVITY,
            DownloadAssetParams(
                ss_url=params.ss_url,
                boot_asset_item_id=params.boot_asset_item_id,
                s3_params=params.s3_params,
            ),
            start_to_close_timeout=timedelta(hours=2),
        )
        result = await workflow.execute_activity(
            UPDATE_BYTES_SYNCED_ACTIVITY,
            UpdateBytesSyncedParams(
                msm_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                bytes_synced=bytes_synced,
            ),
            start_to_close_timeout=timedelta(minutes=1),
        )
        # mypy doesn't let you do `return x == y  # type: ignore`
        if result == 200:
            return True
        return False


@workflow.defn(name=GET_OR_CREATE_PRODUCT_WF_NAME)
class GetOrCreateProduct:
    @workflow.run
    async def run(self, params: GetOrCreateProductParams) -> int:
        asset_id = await workflow.execute_activity(
            GET_OR_CREATE_ASSET_ACTIVITY,
            GetOrCreateAssetParams(
                params.msm_base_url, params.msm_jwt, params.asset
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )
        version = params.version
        version.boot_asset_id = asset_id
        version_id = await workflow.execute_activity(
            GET_OR_CREATE_VERSION_ACTIVITY,
            GetOrCreateVersionParams(
                params.msm_base_url, params.msm_jwt, version
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )
        item = params.item
        item.boot_asset_version_id = version_id
        return await workflow.execute_activity(  # type: ignore
            GET_OR_CREATE_ITEM_ACTIVITY,
            GetOrCreateItemParams(params.msm_base_url, params.msm_jwt, item),
            start_to_close_timeout=timedelta(seconds=30),
        )
