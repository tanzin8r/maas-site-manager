from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, StrEnum
import json
import re
import typing

from management.utils import check_tree_paths, read_signed  # type: ignore
from temporalio import activity
from temporalio.exceptions import ApplicationError

from .base import BaseActivity, compose_url, get_selection_key

FETCH_SS_INDEXES = "fetch-simplestream-indexes"
LOAD_PRODUCT_MAP_ACTIVITY = "load-product-map"
FETCH_SS_ASSETS_ACTIVITY = "fetch-simplestream-asset-list"

INDEX_REGEX = re.compile(r"(?P<base>.*)/streams/v1/.*\.s?json$")


class BootAssetKind(IntEnum):
    OS = 0
    BOOTLOADER = 1


class BootAssetLabel(StrEnum):
    STABLE = "stable"
    CANDIDATE = "candidate"


class ItemFileType(StrEnum):
    # Tarball of root image.
    ROOT_TGZ = "root-tgz"
    ROOT_TBZ = "root-tbz"
    ROOT_TXZ = "root-txz"

    # Tarball of dd image.
    ROOT_DD = "root-dd"
    ROOT_DDTAR = "root-dd.tar"

    # Raw dd image
    ROOT_DDRAW = "root-dd.raw"

    # Compressed dd image types
    ROOT_DDBZ2 = "root-dd.bz2"
    ROOT_DDGZ = "root-dd.gz"
    ROOT_DDXZ = "root-dd.xz"

    # Compressed tarballs of dd images
    ROOT_DDTBZ = "root-dd.tar.bz2"
    ROOT_DDTXZ = "root-dd.tar.xz"
    # For backwards compatibility, DDTGZ files are named root-dd
    ROOT_DDTGZ = "root-dd"

    # Following are not allowed on user upload. Only used for syncing
    # from another simplestreams source. (Most likely images.maas.io)

    # Root Image (gets converted to root-image root-tgz, on the rack)
    ROOT_IMAGE = "root-image.gz"

    # Root image in SquashFS form, does not need to be converted
    SQUASHFS_IMAGE = "squashfs"

    # Boot Kernel
    BOOT_KERNEL = "boot-kernel"

    # Boot Initrd
    BOOT_INITRD = "boot-initrd"

    # Boot DTB
    BOOT_DTB = "boot-dtb"

    # tar.xz of files which need to be extracted so the files are usable
    # by MAAS
    ARCHIVE_TAR_XZ = "archive.tar.xz"

    # Manifest
    MANIFEST = "manifest"


@dataclass
class ProductItem:
    ftype: ItemFileType
    sha256: str
    path: str
    file_size: int
    source_package: str | None = None
    source_version: str | None = None
    source_release: str | None = None

    @classmethod
    def from_simplestream(cls, prod: dict[str, typing.Any]) -> typing.Self:
        return cls(
            ftype=prod["ftype"],
            sha256=prod["sha256"],
            path=prod["path"],
            file_size=prod["size"],
            source_package=prod.get("src_package", None),
            source_version=prod.get("src_version", None),
            source_release=prod.get("src_release", None),
        )


@dataclass
class Product:
    kind: BootAssetKind
    label: BootAssetLabel
    os: str
    arch: str
    release: str | None = None
    codename: str | None = None
    title: str | None = None
    subarch: str | None = None
    compatibility: list[str] | None = None
    flavor: str | None = None
    base_image: str | None = None
    bootloader_type: str | None = None
    eol: datetime | None = None
    esm_eol: datetime | None = None
    signed: bool = False
    versions: dict[str, list[ProductItem]] = field(default_factory=dict)

    @classmethod
    def from_simplestream(cls, prod: dict[str, typing.Any]) -> typing.Self:
        if "bootloader-type" not in prod:
            kind = BootAssetKind.OS
            compatibility = prod.get("subarches", "").split(",")
        else:
            kind = BootAssetKind.BOOTLOADER
            compatibility = prod.get("arches", "").split(",")

        eol = esm_eol = None
        if "support_eol" in prod:
            eol = datetime.fromisoformat(prod["support_eol"])
        if "support_esm_eol" in prod:
            esm_eol = datetime.fromisoformat(prod["support_esm_eol"])

        return cls(
            kind=kind,
            label=prod["label"],
            os=prod["os"],
            arch=prod["arch"],
            release=prod.get("release", None),
            codename=prod.get("release_codename", None),
            title=prod.get("release_title", None),
            subarch=prod.get("subarch", None),
            compatibility=compatibility,
            flavor=prod.get("kflavor", None),
            base_image=prod.get("base_image", None),
            bootloader_type=prod.get("bootloader_type", None),
            eol=eol,
            esm_eol=esm_eol,
        )


@dataclass
class FetchSsIndexesParams:
    index_url: str
    keyring: str | None = None


@dataclass
class FetchSsIndexesResult:
    base_url: str
    signed: bool
    products: list[str]


@dataclass
class LoadProductMapParams:
    index_url: str
    keyring: str | None = None
    versions_to_keep: int = 1
    selections: list[str] = field(default_factory=list)


@dataclass
class LoadProductMapResult:
    items: list[Product]


@dataclass
class FetchAssetListParams:
    index_url: str
    keyring: str | None = None


class AvailableAsset(typing.NamedTuple):
    os: str
    release: str
    label: str
    arch: str


@dataclass
class FetchAssetListResult:
    assets: list[AvailableAsset]


def extract_base_url(index_url: str) -> str:
    if m := INDEX_REGEX.match(index_url):
        return m.group("base")
    return ""


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
                    product_data["os"],
                    product_data["release"],
                    product_data["label"],
                    product_data["arch"],
                )
            )

        available.sort()
        return FetchAssetListResult(assets=available)
