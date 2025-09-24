from datetime import timedelta
import typing

from temporalio import workflow
from temporalio.common import RetryPolicy, WorkflowIDReusePolicy
from temporalio.exceptions import WorkflowAlreadyStartedError

from msm.common.workflows.sync import (
    DOWNLOAD_UPSTREAM_IMAGE_WF_NAME,
    REFRESH_UPSTREAM_SOURCE_WF_NAME,
    SYNC_UPSTREAM_SOURCE_WF_NAME,
    DownloadUpstreamImageParams,
    RefreshUpstreamSourceParams,
    S3Params,
    SyncUpstreamSourceParams,
)
import msm.temporal.activities as act

SS_DOWNLOAD_TIMEOUT = timedelta(minutes=5)
MSM_API_TIMEOUT = timedelta(minutes=2)


@workflow.defn(name=SYNC_UPSTREAM_SOURCE_WF_NAME, sandboxed=False)
class SyncUpstreamSourceWorkflow:
    """Synchronizes sources with the upstream.

    Downloads new assets and new versions of existing assets as needed,
    as directed by the user selections.

    The removal of stale/obsolete assets/versions is handled in another
    moment, as we need to complete the download of newer assets before
    dropping old ones.
    """

    async def start_download(
        self,
        ss_root_url: str,
        s3_params: S3Params,
        msm_url: str,
        msm_jwt: str,
        boot_asset_item_id: int,
    ) -> workflow.ChildWorkflowHandle[typing.Any, bool]:
        return await workflow.start_child_workflow(
            DOWNLOAD_UPSTREAM_IMAGE_WF_NAME,
            DownloadUpstreamImageParams(
                ss_root_url=ss_root_url,
                msm_url=msm_url,
                msm_jwt=msm_jwt,
                boot_asset_item_id=boot_asset_item_id,
                s3_params=s3_params,
            ),
            id=f"download-item-{boot_asset_item_id}",
            id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
            parent_close_policy=workflow.ParentClosePolicy.ABANDON,
            retry_policy=RetryPolicy(  # don't spin too fast
                initial_interval=timedelta(seconds=15),
                maximum_interval=timedelta(seconds=15),
            ),
        )

    @workflow.run
    async def run(self, params: SyncUpstreamSourceParams) -> bool:
        workflow.logger.info("Source %d sync started", params.boot_source_id)

        # download the source data from API
        source: act.GetBootSourceResult = await workflow.execute_activity(
            act.GET_BOOT_SOURCE_ACTIVITY,
            act.GetBootSourceParams(
                msm_base_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_source_id=params.boot_source_id,
            ),
            result_type=act.GetBootSourceResult,
            start_to_close_timeout=MSM_API_TIMEOUT,
        )
        # download upstream Index file and extract the products indexes
        indexes: act.FetchSsIndexesResult = await workflow.execute_activity(
            act.FETCH_SS_INDEXES,
            act.FetchSsIndexesParams(
                index_url=source.index_url,
                keyring=source.keyring,
            ),
            result_type=act.FetchSsIndexesResult,
            start_to_close_timeout=SS_DOWNLOAD_TIMEOUT,
        )

        for product_url in indexes.products:
            workflow.logger.info("Processing product index: %s", product_url)

            product_items: act.LoadProductMapResult = (
                await workflow.execute_activity(
                    act.LOAD_PRODUCT_MAP_ACTIVITY,
                    act.LoadProductMapParams(
                        index_url=product_url,
                        selections=source.selections,
                        keyring=source.keyring,
                    ),
                    result_type=act.LoadProductMapResult,
                    start_to_close_timeout=SS_DOWNLOAD_TIMEOUT,
                )
            )

            assets: act.PutAssetListResult = await workflow.execute_activity(
                act.PUT_NEW_ASSETS_ACTIVITY,
                act.PutAssetListParams(
                    msm_base_url=params.msm_url,
                    msm_jwt=params.msm_jwt,
                    boot_source_id=params.boot_source_id,
                    items=product_items.items,
                ),
                result_type=act.PutAssetListResult,
                start_to_close_timeout=MSM_API_TIMEOUT,
            )

            ss_root_url = act.extract_base_url(source.index_url)

            for item in assets.to_download:
                workflow.logger.debug("Downloading item %d", item)
                try:
                    await self.start_download(
                        ss_root_url=ss_root_url,
                        s3_params=params.s3_params,
                        msm_url=params.msm_url,
                        msm_jwt=params.msm_jwt,
                        boot_asset_item_id=item,
                    )
                except WorkflowAlreadyStartedError:
                    workflow.logger.debug(
                        "Download already in progress (item %d)", item
                    )

            workflow.logger.info(
                "Processed %d items, %d scheduled for download",
                len(product_items.items),
                len(assets.to_download),
            )

        workflow.logger.info("Source %d sync completed", params.boot_source_id)

        return True


@workflow.defn(name=REFRESH_UPSTREAM_SOURCE_WF_NAME, sandboxed=False)
class RefreshUpstreamSourceWorkflow:
    """Refreshes the list of available assets for a given upstream source."""

    @workflow.run
    async def run(self, params: RefreshUpstreamSourceParams) -> bool:
        # download the source data from API
        source: act.GetBootSourceResult = await workflow.execute_activity(
            act.GET_BOOT_SOURCE_ACTIVITY,
            act.GetBootSourceParams(
                msm_base_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_source_id=params.boot_source_id,
            ),
            result_type=act.GetBootSourceResult,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # download upstream Index file and extract the products indexes
        indexes: act.FetchSsIndexesResult = await workflow.execute_activity(
            act.FETCH_SS_INDEXES,
            act.FetchSsIndexesParams(
                index_url=source.index_url,
                keyring=source.keyring,
            ),
            result_type=act.FetchSsIndexesResult,
            start_to_close_timeout=SS_DOWNLOAD_TIMEOUT,
        )

        available_assets: list[act.AvailableAsset] = []
        for product_url in indexes.products:
            workflow.logger.info("Processing product index: %s", product_url)
            assets: act.FetchAssetListResult = await workflow.execute_activity(
                act.FETCH_SS_ASSETS_ACTIVITY,
                act.FetchAssetListParams(
                    index_url=product_url,
                    keyring=source.keyring,
                ),
                result_type=act.FetchAssetListResult,
                start_to_close_timeout=SS_DOWNLOAD_TIMEOUT,
            )
            available_assets.extend(assets.assets)

        # patch the available assets list
        await workflow.execute_activity(
            act.PUT_AVAILABLE_ASSETS_ACTIVITY,
            act.PutAvailableAssetListParams(
                msm_base_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_source_id=params.boot_source_id,
                available=available_assets,
            ),
            start_to_close_timeout=SS_DOWNLOAD_TIMEOUT,
        )

        workflow.logger.info(
            "Refreshed boot-source %d with %d items",
            params.boot_source_id,
            len(available_assets),
        )

        return True
