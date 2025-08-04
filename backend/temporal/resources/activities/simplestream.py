from collections import defaultdict
from dataclasses import dataclass, field
import json
import typing

from management.utils import check_tree_paths, read_signed  # type: ignore
from temporalio import activity
from temporalio.exceptions import ApplicationError

from .base import BaseActivity
from .images import compose_url

BASE_ASSET_ATTRS = frozenset(
    [
        "arch",
        "bootloader-type",
        "kflavor",
        "label",
        "os",
        "release_codename",
        "release_title",
        "release",
        "subarch",
        "subarches",
        "support_eol",
        "support_esm_eol",
    ]
)

GET_BOOT_SOURCE_ACTIVITY = "get-boot-source"
FETCH_SS_INDEXES = "fetch-simplestream-indexes"
LOAD_PRODUCT_MAP_ACTIVITY = "load-product-map"
FETCH_SS_ASSETS_ACTIVITY = "fetch-simplestream-asset-list"
PATCH_AVAILABLE_ASSETS_ACTIVITY = "patch-available-asset-list"


@dataclass
class GetBootSourceParams:
    msm_base_url: str
    msm_jwt: str
    boot_source_id: int


@dataclass
class GetBootSourceResult:
    index_url: str
    keyring: str | None = None
    selections: dict[str, list[str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Self:
        return cls(**data)


@dataclass
class FetchSsIndexesParams:
    index_url: str
    keyring: str | None = None


@dataclass
class FetchSsIndexesResult:
    base_url: str
    signed: bool
    products: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Self:
        return cls(**data)


@dataclass
class LoadProductMapParams:
    index_url: str
    keyring: str | None = None
    selections: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class LoadProductMapResult:
    items: list[dict[str, typing.Any]]

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Self:
        return cls(**data)


@dataclass
class FetchAssetListParams:
    index_url: str
    keyring: str | None = None


class AvailableAsset(typing.NamedTuple):
    os: str
    release: str
    label: str
    arches: list[str]


@dataclass
class FetchAssetListResult:
    assets: list[AvailableAsset]

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Self:
        return cls(**data)


@dataclass
class PatchAssetListParams:
    msm_base_url: str
    msm_jwt: str
    boot_source_id: int
    available: FetchAssetListResult


def get_selection_key(os: str, release: str) -> str:
    return f"{os}---{release}"


class SimpleStreamActivities(BaseActivity):
    async def _download_json(
        self,
        url: str,
        keyring: str | None = None,
    ) -> tuple[typing.Any, bool]:
        response = await self.client.get(
            url,
            timeout=7200,
        )
        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to download JSON: {response.status_code} {response.text}"
            )
        content = response.text

        if url.endswith(".sjson"):
            signed_content, signed_by_cpc = await read_signed(
                content,
                keyring=keyring,
            )
            json_content = json.loads(signed_content)
        else:
            json_content = json.loads(content)
            signed_by_cpc = False

        return json_content, signed_by_cpc

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
        selections = {
            get_selection_key(sel["os"], sel["release"]): sel["arches"].split(
                ","
            )
            for sel in response.json()["items"]
        }
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

    @activity.defn(name=FETCH_SS_INDEXES)
    async def parse_ss_index(
        self, params: FetchSsIndexesParams
    ) -> FetchSsIndexesResult:
        content, signed = await self._download_json(
            params.index_url, params.keyring
        )
        check_tree_paths(content, format="index:1.0")

        activity.logger.info(
            "Index '%s' retrieved, signed: %s", params.index_url, signed
        )
        activity.heartbeat()

        base_url = params.index_url
        for suffix in ["streams/v1/index.json", "streams/v1/index.sjson"]:
            base_url = base_url.removesuffix(suffix)

        products: list[str] = []

        for entry in content.get("index", {}).values():
            if entry.get("format") != "products:1.0":
                continue
            products.append(compose_url(base_url, entry["path"]))

        return FetchSsIndexesResult(base_url, signed, products)

    @activity.defn(name=LOAD_PRODUCT_MAP_ACTIVITY)
    async def load_product_map(
        self, params: LoadProductMapParams
    ) -> LoadProductMapResult:
        content, signed = await self._download_json(
            params.index_url, params.keyring
        )
        check_tree_paths(content, format="products:1.0")

        activity.logger.info(
            "Index '%s' retrieved, signed: %s", params.index_url, signed
        )
        activity.heartbeat()

        download_items: list[dict[str, typing.Any]] = []
        for product_data in content["products"].values():
            if "bootloader-type" not in product_data:
                key = get_selection_key(
                    product_data["os"], product_data["release"]
                )

                if key not in params.selections:
                    continue
                if product_data["arch"] not in params.selections[key]:
                    continue

            base_item = {
                k: product_data[k]
                for k in BASE_ASSET_ATTRS
                if k in product_data
            }

            version = sorted(product_data["versions"].keys())[-1]
            items = product_data["versions"][version]["items"]
            for asset in items.values():
                new_item = {
                    **base_item,
                    "sha256": asset["sha256"],
                    "path": asset["path"],
                    "file_size": asset["size"],
                    "ftype": asset["ftype"],
                    "source_package": asset.get("source_package", None),
                    "source_version": asset.get("source_version", None),
                    "source_release": asset.get("source_release", None),
                }
                download_items.append(new_item)

        return LoadProductMapResult(download_items)

    @activity.defn(name=FETCH_SS_ASSETS_ACTIVITY)
    async def fetch_ss_asset_list(
        self, params: FetchAssetListParams
    ) -> FetchAssetListResult:
        content, signed = await self._download_json(
            params.index_url, params.keyring
        )
        check_tree_paths(content, format="products:1.0")

        activity.logger.info(
            "Index '%s' retrieved, signed: %s", params.index_url, signed
        )
        activity.heartbeat()

        available: dict[tuple[str, str, str], list[str]] = defaultdict(list)
        for product_data in content["products"].values():
            if "bootloader-type" in product_data:
                continue
            available[
                (
                    product_data["os"],
                    product_data["release"],
                    product_data["label"],
                )
            ].append(product_data["arch"])

        return FetchAssetListResult(
            assets=[
                AvailableAsset(k[0], k[1], k[2], v)
                for k, v in available.items()
            ]
        )

    @activity.defn(name=PATCH_AVAILABLE_ASSETS_ACTIVITY)
    async def patch_asset_list(self, params: PatchAssetListParams) -> bool:
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
                    "arches": sel.arches,
                }
                for sel in params.available.assets
            ]
        }

        response = await self.client.put(url, headers=headers, json=put_req)

        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to update available asset list: {response.status_code} {response.text}"
            )

        return True
