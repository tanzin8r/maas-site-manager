from asyncio import gather
from datetime import datetime
import typing

from activities.download_upstream_activities import (  # type: ignore
    BootAsset,
    BootAssetItem,
    BootAssetKind,
    BootAssetLabel,
    BootAssetVersion,
    S3Params,
)
from simplestreams.objectstores import ObjectStore  # type: ignore
from temporalio import workflow
from temporalio.common import WorkflowIDReusePolicy
from temporalio.exceptions import ApplicationError
from temporalio.workflow import ParentClosePolicy
from workflows.download_upstream import (  # type: ignore
    DOWNLOAD_UPSTREAM_IMAGE_WF_NAME,
    GET_OR_CREATE_PRODUCT_WF_NAME,
    DownloadUpstreamImageParams,
    GetOrCreateProductParams,
)


class MSMImageStore(ObjectStore):  # type: ignore
    def __init__(
        self, msm_base_url: str, msm_jwt: str, s3_params: S3Params
    ) -> None:
        self._files_to_download: dict[str, dict[str, typing.Any]] = {}
        self._msm_base_url = msm_base_url
        self._jwt = msm_jwt
        self._s3_params = s3_params

    def _start_download_workflow(
        self, item: dict[str, typing.Any]
    ) -> typing.Coroutine[typing.Any, typing.Any, typing.Any]:
        return workflow.execute_child_workflow(
            DOWNLOAD_UPSTREAM_IMAGE_WF_NAME,
            DownloadUpstreamImageParams(
                item["ss_url"],
                "/".join(
                    [
                        self._msm_base_url.rstrip("/"),
                        f"api/v1/bootasset-items/{item['id']}",
                    ],
                ),
                self._jwt,
                item["id"],
                self._s3_params,
            ),
            id=f"download-item-{item['id']}",
            id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
            parent_close_policy=ParentClosePolicy.ABANDON,
        )

    def _get_asset_from_product(
        self, product: dict[str, str], boot_source_id: int
    ) -> BootAsset:
        bootloader_type = product.get("bootloader-type")
        if bootloader_type is None:
            # TODO: replace +0000 with .replace(UTC) when python version is 3.12
            eol = datetime.strptime(
                product.get("support_eol", "1970-01-01") + "+0000",
                "%Y-%m-%d%z",
            )
            esm_eol = datetime.strptime(
                product.get("support_esm_eol", "1970-01-01") + "+0000",
                "%Y-%m-%d%z",
            )
            return BootAsset(
                boot_source_id=boot_source_id,
                kind=BootAssetKind.OS,
                label=BootAssetLabel(product.get("label")),
                os=product.get("os"),
                arch=product.get("arch"),
                release=product.get("release"),
                codename=product.get("release_codename"),
                title=product.get("release_title"),
                subarch=product.get("subarch"),
                compatibility=product.get("subarches", "").split(","),
                flavor=product.get("kflavor"),
                eol=eol,
                esm_eol=esm_eol,
            )
        else:
            return BootAsset(
                boot_source_id=boot_source_id,
                kind=BootAssetKind.BOOTLOADER,
                label=BootAssetLabel(product.get("label")),
                os=product.get("os"),
                arch=product.get("arch"),
            )

    def _get_version_from_product(
        self, product: dict[str, str]
    ) -> BootAssetVersion:
        return BootAssetVersion(
            boot_asset_id=0, version=product.get("version", "")
        )

    def _get_item_from_product(self, product: dict[str, str]) -> BootAssetItem:
        return BootAssetItem(
            boot_asset_version_id=0,
            ftype=product.get("ftype"),
            sha256=product.get("sha256"),
            path=product.get("path"),
            file_size=product.get("size"),
            source_package=product.get("src_package"),
            source_version=product.get("src_version"),
            source_release=product.get("src_release"),
        )

    async def _get_or_create_product(
        self, product: dict[str, str], boot_source_id: int
    ) -> int:
        """
        Get or create a Boot Asset, Boot Asset Version, and Boot Asset Item in the Site Manager DB.

        Returns: Boot Asset Item ID
        """
        asset = self._get_asset_from_product(product, boot_source_id)
        version = self._get_version_from_product(product)
        item = self._get_item_from_product(product)
        params = GetOrCreateProductParams(
            msm_base_url=self._msm_base_url,
            msm_jwt=self._jwt,
            asset=asset,
            version=version,
            item=item,
        )
        return await workflow.execute_child_workflow(  # type: ignore
            GET_OR_CREATE_PRODUCT_WF_NAME,
            params,
            id=f"get-or-create-product-{item.sha256}",
            id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
            parent_close_policy=ParentClosePolicy.TERMINATE,
        )

    async def insert(
        self, product: dict[str, str], ss_url: str, boot_source_id: int
    ) -> None:
        item_id = await self._get_or_create_product(product, boot_source_id)
        self._mark_for_download(ss_url, item_id, product.get("sha256", ""))

    def _mark_for_download(
        self, ss_url: str, item_id: int, sha256: str
    ) -> None:
        self._files_to_download[sha256] = {
            "ss_url": ss_url,
            "id": item_id,
        }

    async def finalize(self) -> None:
        child_workflows = [
            self._start_download_workflow(item_info)
            for item_info in self._files_to_download.values()
        ]
        if child_workflows:
            workflow.logger.info(f"Downloading {len(child_workflows)} items")
            successes = await gather(*child_workflows)
            if not all(successes):
                raise ApplicationError(
                    "Some files could not be downloaded, aborting",
                    non_retryable=True,
                )
