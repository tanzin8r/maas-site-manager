from dataclasses import dataclass
from datetime import timedelta

from activities.download_upstream_activities import (  # type: ignore
    DOWNLOAD_SS_JSON_ACTIVITY,
    GET_BOOT_SOURCE_ACTIVITY,
    LOAD_PRODUCT_MAP_ACTIVITY,
    PARSE_SS_INDEX_ACTIVITY,
    DownloadJsonParams,
    GetBootSourceParams,
    LoadProductMapParams,
    ParseSsIndexParams,
    S3Params,
    compose_url,
)
from management.objectstore import MSMImageStore  # type: ignore
from temporalio import workflow

SYNC_UPSTREAM_SOURCE_WF_NAME = "SyncUpstreamSource"


@dataclass
class SyncUpstreamSourceParams:
    msm_url: str
    msm_jwt: str
    boot_source_id: int
    s3_params: S3Params


@workflow.defn(name=SYNC_UPSTREAM_SOURCE_WF_NAME, sandboxed=False)
class SyncUpstreamSourceWorkflow:
    @workflow.run
    async def run(self, params: SyncUpstreamSourceParams) -> bool:
        # download the source data from API
        source = await workflow.execute_activity(
            GET_BOOT_SOURCE_ACTIVITY,
            GetBootSourceParams(
                msm_base_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_source_id=params.boot_source_id,
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )
        # download upstream Index file
        source_index = await workflow.execute_activity(
            DOWNLOAD_SS_JSON_ACTIVITY,
            DownloadJsonParams(
                source_url=source["boot_source"]["url"],
                keyring=source["boot_source"]["keyring"],
            ),
            start_to_close_timeout=timedelta(minutes=5),
        )
        # get products list from Index file
        base_url, products = await workflow.execute_activity(
            PARSE_SS_INDEX_ACTIVITY,
            ParseSsIndexParams(
                index_url=source["boot_source"]["url"],
                content=source_index["json"],
            ),
            start_to_close_timeout=timedelta(minutes=5),
        )

        store = MSMImageStore(
            msm_base_url=params.msm_url,
            msm_jwt=params.msm_jwt,
            s3_params=params.s3_params,
        )

        for product_url in products:
            workflow.logger.info(f"Processing product URL: {product_url}")
            product = await workflow.execute_activity(
                DOWNLOAD_SS_JSON_ACTIVITY,
                DownloadJsonParams(
                    source_url=product_url,
                    keyring=source["boot_source"]["keyring"],
                ),
                start_to_close_timeout=timedelta(minutes=5),
            )

            product_items = await workflow.execute_activity(
                LOAD_PRODUCT_MAP_ACTIVITY,
                LoadProductMapParams(
                    products=product["json"],
                    selections=source["selections"],
                    canonical_source=product["signed_by_cpc"],
                ),
                start_to_close_timeout=timedelta(minutes=5),
            )
            for item in product_items:
                workflow.logger.debug(
                    f"Processing item: {item['path']} with SHA256: {item['sha256'][:8]}"
                )
                await store.insert(
                    item,
                    compose_url(base_url, item["path"]),
                    params.boot_source_id,
                )
            workflow.logger.info(f"Processed {len(product_items)} items")

        await store.finalize()
        return True
