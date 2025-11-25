# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
"""
Simplestream interaction activities.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
import re
import typing

from temporalio import activity
from temporalio.exceptions import ApplicationError

import msm.common.api as api_models
from msm.common.enums import BootAssetKind
from msm.temporal.management.utils import check_tree_paths, read_signed

from .base import BaseActivity, compose_url, get_selection_key

FETCH_SS_INDEXES = "fetch-simplestream-indexes"
LOAD_PRODUCT_MAP_ACTIVITY = "load-product-map"
FETCH_SS_ASSETS_ACTIVITY = "fetch-simplestream-asset-list"

INDEX_REGEX = re.compile(r"(?P<base>.*)/streams/v1/.*\.s?json$")


class ProductItem(api_models.ProductItem):
    """Product item representing a specific file in a SimpleStream.

    Extends the base ProductItem model to include conversion from SimpleStream format.
    """

    @classmethod
    def from_simplestream(cls, prod: dict[str, typing.Any]) -> typing.Self:
        """Create a ProductItem from SimpleStream product data.

        Args:
            prod: Dictionary containing SimpleStream product data with keys like
                 'ftype', 'sha256', 'path', 'size', and optional source info.

        Returns:
            ProductItem instance populated from the SimpleStream data.
        """
        return cls(
            ftype=prod["ftype"],
            sha256=prod["sha256"],
            path=prod["path"],
            file_size=prod["size"],
            source_package=prod.get("src_package", None),
            source_version=prod.get("src_version", None),
            source_release=prod.get("src_release", None),
        )


class Product(api_models.Product):
    """Product representing an OS or bootloader asset collection.

    Extends the base Product model to include conversion from SimpleStream format
    with automatic detection of asset kind and proper timezone handling.
    """

    @classmethod
    def from_simplestream(cls, prod: dict[str, typing.Any]) -> typing.Self:
        """Create a Product from SimpleStream product data.

        Automatically determines if the product is an OS image or bootloader based on
        the presence of 'bootloader-type' field. Handles timezone conversion for
        end-of-life dates.

        Args:
            prod: Dictionary containing SimpleStream product data with required fields
                 like 'label', 'os', 'arch' and optional fields for release info,
                 compatibility, and support dates.

        Returns:
            Product instance populated from the SimpleStream data with empty versions dict.
        """
        if "bootloader-type" not in prod:
            kind = BootAssetKind.OS
            compatibility = prod.get("subarches", "").split(",")
        else:
            kind = BootAssetKind.BOOTLOADER
            compatibility = prod.get("arches", "").split(",")

        eol = esm_eol = None
        if "support_eol" in prod:
            eol = datetime.fromisoformat(prod["support_eol"])
            if eol.tzinfo is None:
                eol = eol.replace(tzinfo=UTC)
        if "support_esm_eol" in prod:
            esm_eol = datetime.fromisoformat(prod["support_esm_eol"])
            if esm_eol.tzinfo is None:
                esm_eol = esm_eol.replace(tzinfo=UTC)
        return cls(
            kind=kind,
            label=prod["label"],
            os=prod["os"],
            arch=prod["arch"],
            release=prod.get("release", None),
            version=prod.get("version", None),
            krel=prod.get("krel", None),
            codename=prod.get("release_codename", None),
            title=prod.get("release_title", None),
            subarch=prod.get("subarch", None),
            compatibility=compatibility,
            flavor=prod.get("kflavor", None),
            base_image=prod.get("base_image", None),
            bootloader_type=prod.get("bootloader-type", None),
            eol=eol,
            esm_eol=esm_eol,
            versions={},
        )


@dataclass
class FetchSsIndexesParams:
    """Parameters for fetching SimpleStream indexes.

    Args:
        index_url: URL to the SimpleStream index file.
        keyring: Optional keyring file for signature verification.
    """

    index_url: str
    keyring: str | None = None


@dataclass
class FetchSsIndexesResult:
    """Result from fetching SimpleStream indexes.

    Args:
        base_url: Base URL extracted from the index URL.
        signed: Whether the index content was cryptographically signed.
        products: List of product URLs found in the index.
    """

    base_url: str
    signed: bool
    products: list[str]


@dataclass
class LoadProductMapParams:
    """Parameters for loading a SimpleStream product map.

    Args:
        index_url: URL to the SimpleStream product index file.
        keyring: Optional keyring file for signature verification.
        versions_to_keep: Maximum number of versions to retain per product (default: 1).
        selections: List of selection keys to filter products by.
    """

    index_url: str
    keyring: str | None = None
    versions_to_keep: int = 1
    selections: list[str] = field(default_factory=list)


@dataclass
class LoadProductMapResult:
    """Result from loading a SimpleStream product map.

    Args:
        items: List of Product objects with their versions populated.
    """

    items: list[Product]


@dataclass
class FetchAssetListParams:
    """Parameters for fetching available asset list.

    Args:
        index_url: URL to the SimpleStream product index file.
        keyring: Optional keyring file for signature verification.
    """

    index_url: str
    keyring: str | None = None


@dataclass(order=True)
class AvailableAsset:
    """Represents an asset available for download.

    Args:
        os: Operating system name.
        release: Release version or codename.
        label: Asset label or type.
        arch: Architecture (e.g., amd64, arm64).
    """

    os: str
    release: str
    label: str
    arch: str


@dataclass
class FetchAssetListResult:
    """Result from fetching available asset list.

    Args:
        assets: List of AvailableAsset objects sorted by their fields.
    """

    assets: list[AvailableAsset]


def extract_base_url(index_url: str) -> str:
    """Extract base URL from a SimpleStream index URL.

    Uses regex to extract the base URL portion from a full SimpleStream index URL
    by matching against the expected path pattern.

    Args:
        index_url: Full URL to a SimpleStream index file.

    Returns:
        Base URL portion if the URL matches the expected pattern, empty string otherwise.

    Example:
        >>> extract_base_url("https://images.maas.io/ephemeral-v3/daily/streams/v1/index.json")
        'https://images.maas.io/ephemeral-v3/daily'
    """
    if m := INDEX_REGEX.match(index_url):
        return m.group("base")
    return ""


class SimpleStreamActivities(BaseActivity):
    """Temporal activities for handling SimpleStream operations.

    Provides activities for fetching and parsing SimpleStream indexes and products,
    including support for signed content verification.
    """

    async def _download_json(
        self,
        url: str,
        keyring: str | None = None,
    ) -> tuple[typing.Any, bool]:
        """Download and parse JSON content from a URL.

        Supports both regular JSON files and signed JSON files (.sjson) with
        optional signature verification using a keyring.

        Args:
            url: URL to download JSON content from.
            keyring: Optional keyring file for verifying signed content.

        Returns:
            Tuple of (parsed_json_content, was_signed_by_cpc).

        Raises:
            ApplicationError: If the download fails or returns non-200 status.
        """
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

    @activity.defn(name=FETCH_SS_INDEXES)
    async def parse_ss_index(
        self, params: FetchSsIndexesParams
    ) -> FetchSsIndexesResult:
        """Parse a SimpleStream index to extract product index URLs.

        Args:
            params: Parameters containing the index URL and optional keyring.

        Returns:
            FetchSsIndexesResult containing the base URL, signature status,
            and list of product index URLs.

        Raises:
            ApplicationError: If download fails or content format is invalid.
        """
        content, signed = await self._download_json(
            params.index_url, params.keyring
        )
        check_tree_paths(content, format="index:1.0")

        activity.logger.info(
            "Index '%s' retrieved, signed: %s", params.index_url, signed
        )
        activity.heartbeat()

        base_url = extract_base_url(params.index_url)
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
        """Load and process a SimpleStream product map.

        Downloads a SimpleStream product file, filters products based on selections,
        and builds Product objects with their versions and items limited to the
        specified number of versions to keep. Bootloader products are always included.

        Args:
            params: Parameters containing the product URL, selections filter,
                   versions limit, and optional keyring.

        Returns:
            LoadProductMapResult containing filtered and processed Product objects
            sorted by OS, release, and architecture.

        Raises:
            ApplicationError: If download fails or content format is invalid.
        """
        content, signed = await self._download_json(
            params.index_url, params.keyring
        )
        check_tree_paths(content, format="products:1.0")

        activity.logger.info(
            "Index '%s' retrieved, signed: %s", params.index_url, signed
        )
        activity.heartbeat()

        download_items: list[Product] = []
        for product_data in content["products"].values():
            if "bootloader-type" not in product_data:
                key = get_selection_key(
                    product_data["os"],
                    product_data["release"],
                    product_data["arch"],
                )
                if key not in params.selections:
                    continue
            prod = Product.from_simplestream(product_data)
            versions = sorted(product_data["versions"].keys(), reverse=True)
            for i, ver in enumerate(versions):
                if i >= params.versions_to_keep:
                    break
                prod.versions[ver] = []
                items = product_data["versions"][ver]["items"]
                for asset in items.values():
                    prod.versions[ver].append(
                        ProductItem.from_simplestream(asset)
                    )
            download_items.append(prod)

        download_items.sort(key=lambda x: (x.os, x.release, x.arch))
        return LoadProductMapResult(download_items)

    @activity.defn(name=FETCH_SS_ASSETS_ACTIVITY)
    async def fetch_ss_asset_list(
        self, params: FetchAssetListParams
    ) -> FetchAssetListResult:
        """Fetch list of available OS assets from SimpleStream.

        Downloads a SimpleStream product file and extracts available OS assets
        (excluding bootloader assets) to provide a list of what's available for selection.

        Args:
            params: Parameters containing the product URL and optional keyring.

        Returns:
            FetchAssetListResult containing sorted list of available OS assets.

        Raises:
            ApplicationError: If download fails or content format is invalid.
        """
        content, signed = await self._download_json(
            params.index_url, params.keyring
        )
        check_tree_paths(content, format="products:1.0")

        activity.logger.info(
            "Index '%s' retrieved, signed: %s", params.index_url, signed
        )
        activity.heartbeat()

        available: list[AvailableAsset] = []
        for product_data in content["products"].values():
            if "bootloader-type" in product_data:
                continue
            available.append(
                AvailableAsset(
                    os=product_data["os"],
                    release=product_data["release"],
                    label=product_data["label"],
                    arch=product_data["arch"],
                )
            )

        available.sort()
        return FetchAssetListResult(assets=available)
