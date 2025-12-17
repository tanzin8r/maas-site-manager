# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
"""
Workflows for syncing MSM with upstream SimpleStream source.
"""

from datetime import timedelta
import typing

from temporalio import workflow
from temporalio.common import RetryPolicy, WorkflowIDReusePolicy
from temporalio.exceptions import WorkflowAlreadyStartedError

from msm.common.workflows.sync import (
    DOWNLOAD_UPSTREAM_IMAGE_WF_NAME,
    REFRESH_UPSTREAM_SOURCE_WF_NAME,
    REMOVE_STALE_IMAGES_WF_NAME,
    SYNC_UPSTREAM_SOURCE_WF_NAME,
    DownloadUpstreamImageParams,
    RefreshUpstreamSourceParams,
    RemoveStaleImagesParams,
    S3Params,
    SyncUpstreamSourceParams,
)
import msm.temporal.activities as act

SS_DOWNLOAD_TIMEOUT = timedelta(minutes=5)
MSM_API_TIMEOUT = timedelta(minutes=2)


@workflow.defn(name=SYNC_UPSTREAM_SOURCE_WF_NAME, sandboxed=False)
class SyncUpstreamSourceWorkflow:
    """Comprehensive boot asset synchronization workflow from upstream SimpleStream sources.

    This workflow orchestrates the complete synchronization process for a boot source,
    including discovery, metadata updates, download coordination, and cleanup operations.
    The workflow is designed to be resilient and handles large-scale asset synchronization
    efficiently through parallel downloads and child workflow management.

    Workflow Process:
    1. Retrieves boot source configuration and selections from MSM API
    2. Fetches SimpleStream index to discover available products
    3. Processes each product index to build asset metadata
    4. Updates MSM with new assets and determines what needs downloading
    5. Initiates parallel download workflows for required assets
    6. Triggers stale image cleanup in a separate child workflow
    """

    async def start_download(
        self,
        ss_root_url: str,
        s3_params: S3Params,
        msm_url: str,
        msm_jwt: str,
        boot_asset_item_id: int,
    ) -> workflow.ChildWorkflowHandle[typing.Any, bool]:
        """Start a child workflow to download a specific boot asset item.

        Creates and launches a dedicated download workflow for a single boot asset
        item with proper isolation and retry policies. The child workflow is
        configured to be abandoned on parent close, allowing downloads to continue
        even if the main sync workflow completes or fails.

        Args:
            ss_root_url: Base URL of the SimpleStream source for asset retrieval.
            s3_params: S3 storage configuration for asset persistence.
            msm_url: Base URL of the MSM API for progress updates.
            msm_jwt: JWT token for MSM API authentication.
            boot_asset_item_id: Unique identifier of the asset item to download.

        Returns:
            Child workflow handle for the download operation.
        """
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
            execution_timeout=timedelta(hours=2),
            retry_policy=RetryPolicy(  # don't spin too fast
                initial_interval=timedelta(seconds=15),
                maximum_interval=timedelta(seconds=15),
            ),
        )

    async def remove_stale_images(
        self,
        msm_url: str,
        msm_jwt: str,
        boot_source_id: int,
    ) -> None:
        """Initiate stale image cleanup as a separate child workflow.

        Starts a dedicated workflow to identify and remove obsolete asset versions
        that are no longer needed. This operation is performed as a child workflow
        to ensure it can complete independently of the main sync process.

        Args:
            msm_url: Base URL of the MSM API.
            msm_jwt: JWT token for MSM API authentication.
            boot_source_id: Unique identifier of the boot source to clean up.
        """
        await workflow.start_child_workflow(
            REMOVE_STALE_IMAGES_WF_NAME,
            RemoveStaleImagesParams(
                msm_url=msm_url,
                msm_jwt=msm_jwt,
                boot_source_id=boot_source_id,
            ),
            id=f"remove-stale-images-{boot_source_id}",
            id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE,
            parent_close_policy=workflow.ParentClosePolicy.ABANDON,
            execution_timeout=timedelta(hours=1),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=15),
                maximum_interval=timedelta(seconds=15),
            ),
        )

    @workflow.run
    async def run(self, params: SyncUpstreamSourceParams) -> bool:
        """Execute the boot source synchronization workflow.

        Args:
            params: Synchronization parameters including boot source ID, MSM API
                   details, and S3 storage configuration.

        Returns:
            True if synchronization completed successfully, False otherwise.
        """
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

        items = []

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
            items += product_items.items

        assets: act.PutAssetListResult = await workflow.execute_activity(
            act.PUT_NEW_ASSETS_ACTIVITY,
            act.PutAssetListParams(
                msm_base_url=params.msm_url,
                msm_jwt=params.msm_jwt,
                boot_source_id=params.boot_source_id,
                items=items,
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
            len(items),
            len(assets.to_download),
        )

        await self.remove_stale_images(
            params.msm_url,
            params.msm_jwt,
            params.boot_source_id,
        )
        workflow.logger.info("Source %d sync completed", params.boot_source_id)
        return True


@workflow.defn(name=REFRESH_UPSTREAM_SOURCE_WF_NAME, sandboxed=False)
class RefreshUpstreamSourceWorkflow:
    """Lightweight workflow to refresh available asset catalog from upstream sources.

    This workflow provides a fast, metadata-only synchronization operation that
    updates the list of available assets without downloading actual files. It's
    designed for scenarios where users need to see what's available upstream
    before making selection changes or when checking for new releases.
    """

    @workflow.run
    async def run(self, params: RefreshUpstreamSourceParams) -> bool:
        """Execute the asset catalog refresh workflow.

        Args:
            params: Refresh parameters containing boot source ID and MSM API details.

        Returns:
            True if refresh completed successfully, False otherwise.
        """
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
