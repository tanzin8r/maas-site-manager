from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import json
from os.path import join
import typing

import boto3  # type: ignore
from httpx import AsyncClient
from management.utils import check_tree_paths, read_signed  # type: ignore
from temporalio import activity
from temporalio.exceptions import ApplicationError

MIN_S3_PART_SIZE = 5 * 1024**2  # 5MiB

DOWNLOAD_ASSET_ACTIVITY = "download-asset"
DOWNLOAD_SS_JSON_ACTIVITY = "download_simplestream-index"
GET_BOOT_SOURCE_ACTIVITY = "get-boot-source"
GET_OR_CREATE_ASSET_ACTIVITY = "get-or-create-asset"
GET_OR_CREATE_ITEM_ACTIVITY = "get-or-create-item"
GET_OR_CREATE_VERSION_ACTIVITY = "get-or-create-version"
PARSE_SS_INDEX_ACTIVITY = "parse-simplestream-index"
LOAD_PRODUCT_MAP_ACTIVITY = "load-product-map"
UPDATE_BYTES_SYNCED_ACTIVITY = "update-bytes-synced"


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


@dataclass
class S3Params:
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    path: str


@dataclass
class UpdateBytesSyncedParams:
    msm_url: str
    msm_jwt: str
    bytes_synced: int


@dataclass
class DownloadAssetParams:
    ss_url: str
    boot_asset_item_id: int
    s3_params: S3Params


@dataclass
class BootAssetVersion:
    """
    A boot asset version to either find or create.
    """

    boot_asset_id: int
    version: str


@dataclass
class BootAssetItem:
    """
    A boot asset item to either find or create.
    """

    boot_asset_version_id: int
    ftype: str
    sha256: str
    path: str
    file_size: int
    source_package: str | None = None
    source_version: str | None = None
    source_release: str | None = None


class BootAssetKind(int, Enum):
    OS = 0
    BOOTLOADER = 1


class BootAssetLabel(str, Enum):
    STABLE = "stable"
    CANDIDATE = "candidate"


@dataclass
class BootAsset:
    """
    A boot asset to either find or create.
    """

    boot_source_id: int
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
    bootloader_type: str | None = None
    eol: datetime | None = None
    esm_eol: datetime | None = None


@dataclass
class GetOrCreateAssetParams:
    msm_base_url: str
    msm_jwt: str
    asset: BootAsset


@dataclass
class GetOrCreateVersionParams:
    msm_base_url: str
    msm_jwt: str
    version: BootAssetVersion


@dataclass
class GetOrCreateItemParams:
    msm_base_url: str
    msm_jwt: str
    item: BootAssetItem


@dataclass
class GetBootSourceParams:
    msm_base_url: str
    msm_jwt: str
    boot_source_id: int


@dataclass
class DownloadJsonParams:
    source_url: str
    keyring: str | None = None


@dataclass
class ParseSsIndexParams:
    index_url: str
    content: dict[str, typing.Any]


@dataclass
class LoadProductMapParams:
    products: dict[str, typing.Any]
    selections: dict[str, list[str]]
    canonical_source: bool


class S3ResourceManager:
    def __init__(self, s3_params: S3Params, boot_asset_item_id: int) -> None:
        self.s3_resource = boto3.resource(
            "s3",
            use_ssl=False,
            verify=False,
            endpoint_url=s3_params.endpoint,
            aws_access_key_id=s3_params.access_key,
            aws_secret_access_key=s3_params.secret_key,
        )
        self.s3_key = join(s3_params.path, str(boot_asset_item_id))
        self.bucket = s3_params.bucket
        self.upload_id = self._create_multipart_upload()
        self.part_no = 1
        self.parts: list[dict[str, typing.Any]] = []
        self.bytes_sent = 0

    def _create_multipart_upload(self) -> str:
        multipart_upload = (
            self.s3_resource.meta.client.create_multipart_upload(
                ACL="public-read",
                Bucket=self.bucket,
                Key=self.s3_key,
                ChecksumAlgorithm="SHA256",
            )
        )
        return multipart_upload["UploadId"]  # type: ignore

    def upload_part(self, chunk: bytes) -> None:
        multipart_upload_part = self.s3_resource.MultipartUploadPart(
            self.bucket, self.s3_key, self.upload_id, self.part_no
        )
        part = multipart_upload_part.upload(
            Body=chunk,
            ChecksumAlgorithm="SHA256",
        )

        activity.heartbeat(f"Uploaded part {self.part_no}")
        self.parts.append({"ETag": part["ETag"], "PartNumber": self.part_no})
        self.part_no += 1
        self.bytes_sent += len(chunk)

    def complete_upload(self) -> None:
        self.s3_resource.meta.client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self.upload_id,
            MultipartUpload={"Parts": self.parts},
        )

    def abort_upload(self) -> None:
        self.s3_resource.meta.client.abort_multipart_upload(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self.upload_id,
        )


def compose_url(prefix: str, path: str) -> str:
    return "/".join(
        [
            prefix.rstrip("/"),
            path,
        ]
    )


def get_selection_key(os: str, release: str) -> str:
    return f"{os}---{release}"


class ImageManagementActivity:
    """
    Activities for image management
    """

    def __init__(self) -> None:
        self.client = self._create_client()

    def _create_client(self) -> AsyncClient:
        return AsyncClient(trust_env=True)

    def _create_s3_manager(
        self, params: S3Params, item_id: int
    ) -> S3ResourceManager:
        return S3ResourceManager(params, item_id)

    def _get_header(self, jwt: str) -> dict[str, str]:
        return {"Authorization": f"bearer {jwt}"}

    async def _get_or_create(
        self,
        get_url: str,
        get_params: dict[str, typing.Any],
        post_url: str,
        post_data: dict[str, typing.Any],
        headers: dict[str, str],
    ) -> tuple[bool, int]:
        """
        Get or create the given asset/version/item.

        Returns: tuple of (created, ID)
        """
        resp = await self.client.get(
            get_url,
            headers=headers,
            params=get_params,
        )
        if resp.status_code != 200:
            raise ApplicationError(
                f"Got an unexpected response ({resp.status_code}) from MSM API: {resp.text}"
            )
        items = resp.json()["items"]
        if len(items) == 0:
            resp = await self.client.post(
                post_url, json=post_data, headers=headers
            )
            if resp.status_code == 409:
                resp = await self.client.get(
                    get_url,
                    headers=headers,
                    params=get_params,
                )
                return False, resp.json()["items"][0]["id"]
            elif resp.status_code == 200:
                return True, resp.json()["id"]
            else:
                raise ApplicationError(
                    f"Got an unexpected response ({resp.status_code}) from MSM API: {resp.text}"
                )
        return False, items[0]["id"]

    @activity.defn(name=UPDATE_BYTES_SYNCED_ACTIVITY)
    async def update_bytes_synced(
        self, params: UpdateBytesSyncedParams
    ) -> int:
        msm_headers = self._get_header(params.msm_jwt)
        new_item = {"bytes_synced": params.bytes_synced}
        response = await self.client.patch(
            params.msm_url, headers=msm_headers, json=new_item
        )
        return response.status_code

    @activity.defn(name=DOWNLOAD_ASSET_ACTIVITY)
    async def download_asset(self, params: DownloadAssetParams) -> int:
        s3_manager = self._create_s3_manager(
            params.s3_params, params.boot_asset_item_id
        )
        chunk = b""
        try:
            async with self.client.stream(
                "GET", params.ss_url, timeout=7200
            ) as r:
                async for data in r.aiter_bytes():
                    chunk += data
                    if len(chunk) >= MIN_S3_PART_SIZE:
                        s3_manager.upload_part(chunk)
                        chunk = b""
                # finalize upload
                if chunk:
                    s3_manager.upload_part(chunk)
                s3_manager.complete_upload()
        except:
            s3_manager.abort_upload()
            raise
        return s3_manager.bytes_sent

    @activity.defn(name=GET_OR_CREATE_ASSET_ACTIVITY)
    async def get_or_create_asset(self, params: GetOrCreateAssetParams) -> int:
        headers = self._get_header(params.msm_jwt)
        url = compose_url(params.msm_base_url, "api/v1/bootassets")
        get_params = {
            "kind": params.asset.kind,
            "label": params.asset.label,
            "os": params.asset.os,
            "arch": params.asset.arch,
        }
        asset_dict = asdict(params.asset)

        _, id = await self._get_or_create(
            url, get_params, url, asset_dict, headers
        )
        return id

    @activity.defn(name=GET_OR_CREATE_VERSION_ACTIVITY)
    async def get_or_create_version(
        self, params: GetOrCreateVersionParams
    ) -> tuple[bool, int]:
        headers = self._get_header(params.msm_jwt)
        get_url = compose_url(params.msm_base_url, "api/v1/bootasset-versions")
        post_url = compose_url(
            params.msm_base_url,
            f"api/v1/bootassets/{params.version.boot_asset_id}/versions",
        )
        version_dict = {"version": params.version.version}
        get_params = {
            "version": params.version.version,
            "boot_asset_id": params.version.boot_asset_id,
        }
        return await self._get_or_create(
            get_url, get_params, post_url, version_dict, headers
        )

    @activity.defn(name=GET_OR_CREATE_ITEM_ACTIVITY)
    async def get_or_create_item(self, params: GetOrCreateItemParams) -> int:
        headers = self._get_header(params.msm_jwt)
        get_url = compose_url(params.msm_base_url, "api/v1/bootasset-items")
        get_params = {"sha256": params.item.sha256}
        post_url = compose_url(
            params.msm_base_url,
            f"api/v1/bootasset-versions/{params.item.boot_asset_version_id}/items",
        )
        item_dict = asdict(params.item)
        item_dict.pop("boot_asset_version_id")
        item_dict.pop("path")
        _, id = await self._get_or_create(
            get_url, get_params, post_url, item_dict, headers
        )
        return id

    @activity.defn(name=GET_BOOT_SOURCE_ACTIVITY)
    async def get_boot_source(
        self, params: GetBootSourceParams
    ) -> dict[str, typing.Any]:
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

        return {
            "boot_source": boot_source,
            "selections": selections,
        }

    @activity.defn(name=DOWNLOAD_SS_JSON_ACTIVITY)
    async def download_json(
        self, params: DownloadJsonParams
    ) -> dict[str, typing.Any]:
        response = await self.client.get(
            params.source_url,
            timeout=7200,
        )
        if response.status_code != 200:
            raise ApplicationError(
                f"Failed to download JSON: {response.status_code} {response.text}"
            )
        content = response.text

        if params.source_url.endswith(".sjson"):
            signed_content, signed_by_cpc = await read_signed(
                content,
                keyring=params.keyring,
            )
            json_content = json.loads(signed_content)
        else:
            json_content = json.loads(content)
            signed_by_cpc = False

        return {
            "json": json_content,
            "signed_by_cpc": signed_by_cpc,
        }

    @activity.defn(name=PARSE_SS_INDEX_ACTIVITY)
    async def parse_ss_index(
        self, params: ParseSsIndexParams
    ) -> tuple[str, list[str]]:
        check_tree_paths(params.content, format="index:1.0")

        base_url = params.index_url
        for suffix in ["streams/v1/index.json", "streams/v1/index.sjson"]:
            base_url = base_url.removesuffix(suffix)

        products: list[str] = []

        for entry in params.content.get("index", {}).values():
            if entry.get("format") != "products:1.0":
                continue
            products.append(compose_url(base_url, entry["path"]))

        return base_url, products

    @activity.defn(name=LOAD_PRODUCT_MAP_ACTIVITY)
    async def load_product_map(
        self, params: LoadProductMapParams
    ) -> list[dict[str, typing.Any]]:
        target: list[dict[str, typing.Any]] = []

        source = params.products
        check_tree_paths(source, format="products:1.0")

        for product_data in source["products"].values():
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
                target.append(new_item)

        return target
