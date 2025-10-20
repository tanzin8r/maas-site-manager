from dataclasses import dataclass, field
from typing import Any

from pydantic import AwareDatetime
from temporalio import activity
from temporalio.exceptions import ApplicationError

from msm.common.api.bootassets import (
    AssetVersions,
    AvailableBootSourceSelection,
    BootAssetItemGetResponse,
    BootSourceAvailSelectionsPutRequest,
    BootSourceGetResponse,
    BootSourcesAssetsPutRequest,
    BootSourceSelectionsGetResponse,
)
from msm.common.enums import BootAssetLabel

from .base import BaseActivity, compose_url, get_selection_key
from .simplestream import AvailableAsset, Product

GET_BOOT_SOURCE_ACTIVITY = "get-boot-source"
GET_BOOT_ASSET_ITEM_ACTIVITY = "get-boot-asset-item"
PUT_AVAILABLE_ASSETS_ACTIVITY = "patch-available-asset-list"
PUT_NEW_ASSETS_ACTIVITY = "put-new-asset-list"
GET_SOURCE_VERSIONS_ACTIVITY = "get-source-versions"
REMOVE_STALE_VERSIONS_ACTIVITY = "remove-stale-versions"
GET_SOURCE_LAST_SYNC_ACTIVITY = "get-source-last-sync"


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
class GetSourceVersionsParams:
    msm_base_url: str
    msm_jwt: str
    boot_source_id: int


@dataclass
class GetSourceVersionsResult:
    versions: list[AssetVersions]


@dataclass
class RemoveStaleVersionsParams:
    msm_base_url: str
    msm_jwt: str
    versions: list[AssetVersions]
    versions_to_keep: int
    source_last_sync: AwareDatetime


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


@dataclass
class GetSourceLastSyncParams:
    msm_base_url: str
    msm_jwt: str
    boot_source_id: int


class BootAssetActivities(BaseActivity):
    async def _get_boot_source(
        self, msm_base_url: str, headers: dict[str, str], boot_source_id: int
    ) -> BootSourceGetResponse:
        url = compose_url(
            msm_base_url,
            f"api/v1/bootasset-sources/{boot_source_id}",
        )
        response = await self.client.get(url, headers=headers)
        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to get boot source: {response.status_code} {response.text}"
            )
        return BootSourceGetResponse.from_dict(response.json())

    @activity.defn(name=GET_BOOT_SOURCE_ACTIVITY)
    async def get_boot_source(
        self, params: GetBootSourceParams
    ) -> GetBootSourceResult:
        headers = self._get_header(params.msm_jwt)

        boot_source = await self._get_boot_source(
            params.msm_base_url, headers, params.boot_source_id
        )

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
        selection_response = BootSourceSelectionsGetResponse.from_dict(
            response.json()
        )
        selections = [
            get_selection_key(sel.os, sel.release, sel.arch)
            for sel in selection_response.items
            if sel.selected
        ]
        activity.logger.debug(
            "Boot source %d has %d selections",
            params.boot_source_id,
            len(selections),
        )

        return GetBootSourceResult(
            index_url=boot_source.url,
            keyring=boot_source.keyring,
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
        item = BootAssetItemGetResponse.from_dict(response.json())

        return GetBootAssetItemResult(
            path=item.path,
            sha256=item.sha256,
            file_size=item.file_size,
            bytes_synced=item.bytes_synced,
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

        put_req = BootSourceAvailSelectionsPutRequest(
            available=[
                AvailableBootSourceSelection(
                    os=sel.os,
                    release=sel.release,
                    label=BootAssetLabel(sel.label),
                    arch=sel.arch,
                )
                for sel in params.available
            ]
        )

        response = await self.client.put(
            url, headers=headers, json=put_req.model_dump(mode="json")
        )

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

        put_req = BootSourcesAssetsPutRequest(
            products=[p for p in params.items]
        )

        response = await self.client.put(
            url, headers=headers, json=put_req.model_dump(mode="json")
        )

        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to update assets: {response.status_code} {response.text}"
            )

        ret = response.json()["to_download"]
        return PutAssetListResult(to_download=ret)

    @activity.defn(name=GET_SOURCE_LAST_SYNC_ACTIVITY)
    async def get_source_last_sync(
        self, params: GetSourceLastSyncParams
    ) -> AwareDatetime:
        headers = self._get_header(params.msm_jwt)
        boot_source = await self._get_boot_source(
            params.msm_base_url, headers, params.boot_source_id
        )
        return boot_source.last_sync

    @activity.defn(name=GET_SOURCE_VERSIONS_ACTIVITY)
    async def get_source_versions(
        self, params: GetSourceVersionsParams
    ) -> GetSourceVersionsResult:
        headers = self._get_header(params.msm_jwt)
        url = compose_url(
            params.msm_base_url,
            f"api/v1/bootasset-sources/{params.boot_source_id}/versions",
        )
        response = await self.client.get(url, headers=headers)
        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to retrieve versions for source {params.boot_source_id}: {response.status_code} {response.text}"
            )
        versions = [
            AssetVersions.from_dict(a) for a in response.json()["versions"]
        ]
        return GetSourceVersionsResult(versions=versions)

    @activity.defn(name=REMOVE_STALE_VERSIONS_ACTIVITY)
    async def remove_stale_versions(
        self,
        params: RemoveStaleVersionsParams,
    ) -> None:
        # first get rid of versions that have been removed from upstream
        versions_removed_from_up: list[tuple[int, dict[str, Any]]] = []
        for i, av in enumerate(params.versions):
            for v, vs in av.versions.items():
                if vs.last_seen < params.source_last_sync:
                    versions_removed_from_up.append(
                        (
                            i,
                            {
                                "asset_id": av.asset_id,
                                "version": v,
                            },
                        )
                    )

        for i, rv in versions_removed_from_up:
            params.versions[i].versions.pop(rv["version"])

        # next, check if we have more than required number of versions
        versions_to_remove = [v[1] for v in versions_removed_from_up]
        for av in params.versions:
            complete_versions = [
                v for v, s in av.versions.items() if s.complete
            ]
            if len(complete_versions) > params.versions_to_keep:
                stale = complete_versions[: -params.versions_to_keep]
                versions_to_remove += [
                    {"asset_id": av.asset_id, "version": v} for v in stale
                ]
        if versions_to_remove:
            headers = self._get_header(params.msm_jwt)
            url = compose_url(
                params.msm_base_url,
                "api/v1/bootasset-versions:remove",
            )
            response = await self.client.post(
                url, headers=headers, json={"to_remove": versions_to_remove}
            )
            if response.status_code != 200:
                raise ApplicationError(
                    f"Failed to remove stale versions {versions_to_remove}: {response.status_code} {response.text}"
                )
        else:
            activity.logger.debug("No stale versions to remove")
