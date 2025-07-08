from base64 import b64encode
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from os.path import join
import typing

import boto3  # type: ignore
from temporalio import activity
from temporalio.exceptions import ApplicationError

from .base import BaseActivity

MIN_S3_PART_SIZE = 5 * 1024**2  # 5MiB

DOWNLOAD_ASSET_ACTIVITY = "download-asset"
GET_OR_CREATE_ASSET_ACTIVITY = "get-or-create-asset"
GET_OR_CREATE_ITEM_ACTIVITY = "get-or-create-item"
GET_OR_CREATE_VERSION_ACTIVITY = "get-or-create-version"
UPDATE_BYTES_SYNCED_ACTIVITY = "update-bytes-synced"


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
    msm_url: str
    msm_jwt: str
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
    signed: bool = False


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


class ImageManagementActivity(BaseActivity):
    """
    Activities for image management
    """

    def _create_s3_manager(
        self,
        params: S3Params,
        item_id: int,
        multipart: bool = True,
    ) -> S3ResourceManager:
        return S3ResourceManager(params, item_id, multipart=multipart)

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

    async def _update_bytes_synced(
        self,
        url: str,
        headers: dict[str, str],
        bytes_synced: int,
    ) -> bool:
        """
        Update the bytes synced for the item at the given url.
        Returns: Whether the item still exists.
        """
        response = await self.client.patch(
            url, headers=headers, json={"bytes_synced": bytes_synced}
        )
        if response.status_code == 404:
            return False
        if response.status_code != 200:
            raise ApplicationError(
                f"Got an unexpected response ({response.status_code}) from MSM API: {response.text}"
            )
        return True

    @activity.defn(name=DOWNLOAD_ASSET_ACTIVITY)
    async def download_asset(self, params: DownloadAssetParams) -> int:
        s3_manager = self._create_s3_manager(
            params.s3_params, params.boot_asset_item_id
        )
        msm_headers = self._get_header(params.msm_jwt)
        chunk = b""
        try:
            async with self.client.stream(
                "GET", params.ss_url, timeout=7200
            ) as r:
                async for data in r.aiter_bytes():
                    chunk += data
                    if len(chunk) >= MIN_S3_PART_SIZE:
                        s3_manager.upload_part(chunk)
                        activity.heartbeat(
                            f"Uploaded {s3_manager.bytes_sent} bytes to storage."
                        )
                        if not await self._update_bytes_synced(
                            params.msm_url, msm_headers, s3_manager.bytes_sent
                        ):
                            activity.logger.info(
                                f"Item at {params.msm_url} no longer exists, aborting download"
                            )
                            s3_manager.abort_upload()
                            return -1
                        chunk = b""
                # finalize upload
                if chunk:
                    s3_manager.upload_part(chunk)
                    if not await self._update_bytes_synced(
                        params.msm_url, msm_headers, s3_manager.bytes_sent
                    ):
                        activity.logger.info(
                            f"Item at {params.msm_url} no longer exists, aborting download"
                        )
                        s3_manager.abort_upload()
                        return -1
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
