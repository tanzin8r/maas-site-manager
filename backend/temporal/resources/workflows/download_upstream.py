from dataclasses import dataclass
from datetime import timedelta

from activities.images import (  # type: ignore
    DOWNLOAD_ASSET_ACTIVITY,
    GET_OR_CREATE_ASSET_ACTIVITY,
    GET_OR_CREATE_ITEM_ACTIVITY,
    GET_OR_CREATE_VERSION_ACTIVITY,
    BootAsset,
    BootAssetItem,
    BootAssetVersion,
    DownloadAssetParams,
    GetOrCreateAssetParams,
    GetOrCreateItemParams,
    GetOrCreateVersionParams,
    S3Params,
)
from temporalio import workflow

DOWNLOAD_UPSTREAM_IMAGE_WF_NAME = "DownloadUpstreamImage"
GET_OR_CREATE_PRODUCT_WF_NAME = "GetOrCreateProduct"
CREATE_INDEX_JSON_WF_NAME = "CreateIndexJson"


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


@workflow.defn(name=DOWNLOAD_UPSTREAM_IMAGE_WF_NAME, sandboxed=False)
class DownloadUpstreamImage:
    @workflow.run
    async def run(self, params: DownloadUpstreamImageParams) -> bool:
        bytes_synced = await workflow.execute_activity(
            DOWNLOAD_ASSET_ACTIVITY,
            DownloadAssetParams(
                ss_url=params.ss_url,
                msm_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_asset_item_id=params.boot_asset_item_id,
                s3_params=params.s3_params,
            ),
            start_to_close_timeout=timedelta(hours=2),
        )
        # mypy doesn't let you do `return x == y  # type: ignore`
        if bytes_synced == -1:
            return False
        return True


@workflow.defn(name=GET_OR_CREATE_PRODUCT_WF_NAME, sandboxed=False)
class GetOrCreateProduct:
    @workflow.run
    async def run(self, params: GetOrCreateProductParams) -> tuple[bool, int]:
        asset_id = await workflow.execute_activity(
            GET_OR_CREATE_ASSET_ACTIVITY,
            GetOrCreateAssetParams(
                params.msm_base_url, params.msm_jwt, params.asset
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )
        version = params.version
        version.boot_asset_id = asset_id
        created, version_id = await workflow.execute_activity(
            GET_OR_CREATE_VERSION_ACTIVITY,
            GetOrCreateVersionParams(
                params.msm_base_url, params.msm_jwt, version
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )
        item = params.item
        item.boot_asset_version_id = version_id
        item_id = await workflow.execute_activity(
            GET_OR_CREATE_ITEM_ACTIVITY,
            GetOrCreateItemParams(params.msm_base_url, params.msm_jwt, item),
            start_to_close_timeout=timedelta(seconds=30),
        )
        return created, item_id
