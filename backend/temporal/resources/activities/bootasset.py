from dataclasses import dataclass, field

from temporalio import activity
from temporalio.exceptions import ApplicationError

from .base import BaseActivity, compose_url, get_selection_key
from .simplestream import AvailableAsset, Product

GET_BOOT_SOURCE_ACTIVITY = "get-boot-source"
GET_BOOT_ASSET_ITEM_ACTIVITY = "get-boot-asset-item"
PUT_AVAILABLE_ASSETS_ACTIVITY = "patch-available-asset-list"
PUT_NEW_ASSETS_ACTIVITY = "put-new-asset-list"


@dataclass
class GetBootSourceParams:
    msm_base_url: str
    msm_jwt: str
    boot_source_id: int


@dataclass
class GetBootSourceResult:
    index_url: str
    keyring: str | None = None
    selections: list[str] = field(default_factory=list)


@dataclass
class PutAvailableAssetListParams:
    msm_base_url: str
    msm_jwt: str
    boot_source_id: int
    available: list[AvailableAsset]


@dataclass
class PutAssetListParams:
    msm_base_url: str
    msm_jwt: str
    boot_source_id: int
    items: list[Product]


@dataclass
class PutAssetListResult:
    to_download: list[int]


@dataclass
class GetBootAssetItemParams:
    msm_base_url: str
    msm_jwt: str
    boot_asset_item_id: int


@dataclass
class GetBootAssetItemResult:
    path: str
    sha256: str
    file_size: int
    bytes_synced: int


class BootAssetActivities(BaseActivity):
    @activity.defn(name=GET_BOOT_SOURCE_ACTIVITY)
    async def get_boot_source(
        self, params: GetBootSourceParams
    ) -> GetBootSourceResult:
        headers = self._get_header(params.msm_jwt)

        # get source
        url = compose_url(
            params.msm_base_url,
            f"api/v1/bootasset-sources/{params.boot_source_id}",
        )
        response = await self.client.get(url, headers=headers)
        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to get boot source: {response.status_code} {response.text}"
            )
        boot_source = response.json()

        # get selections
        url = compose_url(
            params.msm_base_url,
            f"api/v1/bootasset-sources/{params.boot_source_id}/selections",
        )
        response = await self.client.get(url, headers=headers)
        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to get asset selections: {response.status_code} {response.text}"
            )
        selections = [
            get_selection_key(sel["os"], sel["release"], sel["arch"])
            for sel in response.json()["items"]
        ]
        activity.logger.debug(
            "Boot source %d has %d selections",
            params.boot_source_id,
            len(selections),
        )

        return GetBootSourceResult(
            index_url=boot_source["url"],
            keyring=boot_source["keyring"],
            selections=selections,
        )

    @activity.defn(name=GET_BOOT_ASSET_ITEM_ACTIVITY)
    async def get_boot_asset_item(
        self, params: GetBootAssetItemParams
    ) -> GetBootAssetItemResult:
        headers = self._get_header(params.msm_jwt)

        # get source
        url = compose_url(
            params.msm_base_url,
            f"api/v1/bootasset-items/{params.boot_asset_item_id}",
        )
        response = await self.client.get(url, headers=headers)
        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to get boot asset item: {response.status_code} {response.text}"
            )
        item = response.json()

        return GetBootAssetItemResult(
            path=item["path"],
            sha256=item["sha256"],
            file_size=item["file_size"],
            bytes_synced=item["bytes_synced"],
        )

    @activity.defn(name=PUT_AVAILABLE_ASSETS_ACTIVITY)
    async def put_available_asset_list(
        self, params: PutAvailableAssetListParams
    ) -> bool:
        headers = self._get_header(params.msm_jwt)

        url = compose_url(
            params.msm_base_url,
            f"api/v1/bootasset-sources/{params.boot_source_id}/available-selections",
        )

        put_req = {
            "available": [
                {
                    "os": sel.os,
                    "release": sel.release,
                    "label": sel.label,
                    "arch": sel.arch,
                }
                for sel in params.available
            ]
        }

        response = await self.client.put(url, headers=headers, json=put_req)

        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to update available asset list: {response.status_code} {response.text}"
            )

        return True

    @activity.defn(name=PUT_NEW_ASSETS_ACTIVITY)
    async def put_asset_list(
        self, params: PutAssetListParams
    ) -> PutAssetListResult:
        headers = self._get_header(params.msm_jwt)

        url = compose_url(
            params.msm_base_url,
            f"api/v1/bootasset-sources/{params.boot_source_id}/assets",
        )

        put_req = {"products": params.items}

        response = await self.client.put(url, headers=headers, json=put_req)

        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to update assets: {response.status_code} {response.text}"
            )

        ret = response.json()["to_download"]
        return PutAssetListResult(to_download=ret)
