from base64 import b64encode
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from hashlib import sha256
import json
from os.path import join
import typing

import boto3  # type: ignore
from httpx import AsyncClient
from temporalio import activity
from temporalio.exceptions import ApplicationError

MIN_S3_PART_SIZE = 5 * 1024**2  # 5MiB

DOWNLOAD_ASSET_ACTIVITY = "download-asset"
GET_OR_CREATE_ASSET_ACTIVITY = "get-or-create-asset"
GET_OR_CREATE_ITEM_ACTIVITY = "get-or-create-item"
GET_OR_CREATE_VERSION_ACTIVITY = "get-or-create-version"
UPDATE_BYTES_SYNCED_ACTIVITY = "update-bytes-synced"
CREATE_INDEX_JSON_ACTIVITY = "create-index-json"


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
class CreateIndexJsonParams:
    msm_fqdn: str
    msm_base_url: str
    msm_jwt: str
    s3_params: S3Params


class S3ResourceManager:
    def __init__(
        self,
        s3_params: S3Params,
        boot_asset_item_id: int,
        multipart: bool = True,
    ) -> None:
        self.s3_resource = boto3.resource(
            "s3",
            use_ssl=False,
            verify=False,
            endpoint_url=s3_params.endpoint,
            aws_access_key_id=s3_params.access_key,
            aws_secret_access_key=s3_params.secret_key,
        )
        self.s3_path = s3_params.path
        self.s3_key = join(s3_params.path, str(boot_asset_item_id))
        self.bucket = s3_params.bucket
        if multipart:
            self.multipart = True
            self.upload_id = self._create_multipart_upload()
            self.part_no = 1
            self.parts: list[dict[str, typing.Any]] = []
            self.bytes_sent = 0
        else:
            self.multipart = False

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
        if not self.multipart:
            raise RuntimeError(
                "S3ResourceManager was initialized in non-multipart mode, but a call to upload a part was made."
            )
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
        if not self.multipart:
            raise RuntimeError(
                "S3ResourceManager was initialized in non-multipart mode."
            )
        self.s3_resource.meta.client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self.upload_id,
            MultipartUpload={"Parts": self.parts},
        )

    def abort_upload(self) -> None:
        if not self.multipart:
            raise RuntimeError(
                "S3ResourceManager was initialized in non-multipart mode."
            )
        self.s3_resource.meta.client.abort_multipart_upload(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self.upload_id,
        )

    def upload_file(
        self, contents: str, key_override: str | None = None
    ) -> None:
        key = self.s3_key
        if key_override:
            key = join(self.s3_path, key_override)
        object = self.s3_resource.Object(self.bucket, key)
        checksum = sha256(contents.encode())
        object.put(
            Body=contents.encode(),
            ACL="public-read",
            ChecksumAlgorithm="SHA256",
            ChecksumSHA256=b64encode(checksum.digest()).decode(),
        )


def compose_url(prefix: str, path: str) -> str:
    return "/".join(
        [
            prefix.rstrip("/"),
            path,
        ]
    )


def reverse_fqdn(fqdn: str) -> str:
    sp = fqdn.split(".")
    sp.reverse()
    return ".".join(sp)


class ImageManagementActivity:
    """
    Activities for image management
    """

    def __init__(self) -> None:
        self.client = self._create_client()

    def _create_client(self) -> AsyncClient:
        return AsyncClient(trust_env=True)

    def _create_s3_manager(
        self,
        params: S3Params,
        item_id: int,
        multipart: bool = True,
    ) -> S3ResourceManager:
        return S3ResourceManager(params, item_id, multipart=multipart)

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

    @activity.defn(name=CREATE_INDEX_JSON_ACTIVITY)
    async def create_index_json(self, params: CreateIndexJsonParams) -> None:
        headers = self._get_header(params.msm_jwt)
        assets_url = compose_url(params.msm_base_url, "api/v1/bootassets")
        assets_resp = await self.client.get(assets_url, headers=headers)
        if assets_resp.status_code != 200:
            raise ApplicationError(
                f"Got unexpected response from API ({assets_resp.status_code}): {assets_resp.text}"
            )
        assets = assets_resp.json()["items"]
        activity.heartbeat(f"Found {len(assets)} items")
        reversed_fqdn = reverse_fqdn(params.msm_fqdn)
        download_json: dict[str, typing.Any] = {
            "content_id": f"{reversed_fqdn}:stream:v1:download",
            "datatype": "image-ids",
            "format": "products:1.0",
            "products": {},
        }
        index: dict[str, typing.Any] = {
            "format": "index:1.0",
            "index": {
                f"{reversed_fqdn}:stream:v1:download": {
                    "datatype": "image-ids",
                    "format": "products:1.0",
                    "path": f"streams/v1/{reversed_fqdn}:stream:v1:download.json",
                }
            },
        }
        products = []
        for asset in assets:
            os = asset.get("os")
            release = asset.get("release")
            arch = asset.get("arch")
            subarch = asset.get("subarch")
            flavor = asset.get("flavor")
            label = asset.get("label")
            compatibility = asset.get("compatibility")
            bootloader_type = asset.get("bootloader_type")
            if asset["kind"] == BootAssetKind.BOOTLOADER:
                product = (
                    f"{reversed_fqdn}.stream:{os}:{bootloader_type}:{arch}"
                )
            else:
                product = (
                    f"{reversed_fqdn}.stream:{os}:{release}:{arch}:{subarch}"
                )
                if flavor:
                    product += f"-{flavor}"
            products.append(product)
            product_json: dict[str, typing.Any] = {
                "arch": arch,
                "kflavor": flavor,
                "label": label,
                "os": os,
                "release": release,
                "release_codename": asset.get("codename"),
                "release_title": asset.get("title"),
                "subarch": subarch,
                "subarches": ",".join(compatibility)
                if compatibility
                else None,
                "bootloader-type": bootloader_type,
                "support_eol": asset.get("eol"),
                "support_esm_eol": asset.get("esm_eol"),
                "versions": {},
            }
            # get latest version, fill in items
            versions_url = compose_url(
                params.msm_base_url, "api/v1/bootasset-versions"
            )
            versions_resp = await self.client.get(
                versions_url,
                headers=headers,
                params={
                    "boot_asset_id": asset["id"],
                    "sort_by": "version-desc",
                },
            )
            if versions_resp.status_code != 200:
                raise ApplicationError(
                    f"Got unexpected response from API ({assets_resp.status_code}): {assets_resp.text}"
                )
            latest_version = versions_resp.json()["items"][0]
            activity.heartbeat(f"Found version {latest_version['version']}")
            # get items:
            items_url = compose_url(
                params.msm_base_url, "api/v1/bootasset-items"
            )
            items_resp = await self.client.get(
                items_url,
                headers=headers,
                params={"boot_asset_version_id": latest_version["id"]},
            )
            if items_resp.status_code != 200:
                raise ApplicationError(
                    f"Got unexpected response from API ({assets_resp.status_code}): {assets_resp.text}"
                )
            activity.heartbeat("Processing items")
            items = items_resp.json()["items"]
            items_json: dict[str, typing.Any] = {}
            for item in items:
                if asset["kind"] == BootAssetKind.BOOTLOADER:
                    i = {
                        "ftype": item.get("ftype"),
                        "path": item.get("path"),
                        "sha256": item.get("sha256"),
                        "size": item.get("file_size"),
                        "src_package": item.get("source_package"),
                        "src_release": item.get("source_release"),
                        "src_version": item.get("source_version"),
                    }
                    items_json[item["source_package"]] = {
                        k: v for k, v in i.items() if v is not None
                    }
                else:
                    i = {
                        "ftype": item.get("ftype"),
                        "path": item.get("path"),
                        "sha256": item.get("sha256"),
                        "size": item.get("file_size"),
                    }
                    items_json[item["ftype"]] = {
                        k: v for k, v in i.items() if v is not None
                    }
            product_json["versions"][latest_version["version"]] = {
                "items": items_json
            }
            download_json["products"][product] = {
                k: v for k, v in product_json.items() if v is not None
            }

        now = datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S %z")
        index["updated"] = now
        index["index"][f"{reversed_fqdn}:stream:v1:download"]["updated"] = now
        index["index"][f"{reversed_fqdn}:stream:v1:download"]["products"] = (
            products
        )
        download_json["updated"] = now
        index_str = json.dumps(index)
        download_str = json.dumps(download_json)
        s3_manager = self._create_s3_manager(
            params.s3_params,
            0,
            multipart=False,
        )
        try:
            s3_manager.upload_file(index_str, key_override="index.json")
            s3_manager.upload_file(
                download_str,
                key_override=f"{reversed_fqdn}:stream:v1:download.json",
            )
        except Exception as e:
            raise ApplicationError(
                f"Failed to upload index.json or download.json to storage: {e}"
            )
