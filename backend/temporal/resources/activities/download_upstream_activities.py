from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from os.path import join
import typing

import boto3  # type: ignore
from httpx import AsyncClient
from temporalio import activity
from temporalio.exceptions import ApplicationError

MIN_S3_PART_SIZE = 5 * 1024**2  # 5MiB
UPDATE_BYTES_SYNCED_ACTIVITY = "update-bytes-synced"
DOWNLOAD_ASSET_ACTIVITY = "download-asset"
GET_OR_CREATE_ASSET_ACTIVITY = "get-or-create-asset"
GET_OR_CREATE_VERSION_ACTIVITY = "get-or-create-version"
GET_OR_CREATE_ITEM_ACTIVITY = "get-or-create-item"


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
    TODO: refactor to make default values None
    """

    boot_source_id: int
    kind: BootAssetKind
    label: BootAssetLabel
    os: str
    arch: str
    release: str = ""
    codename: str = ""
    title: str = ""
    subarch: str = ""
    compatibility: list[str] = field(default_factory=list)
    flavor: str = ""
    base_image: str = ""  # TODO: Remove field when nullable in DB, only used for custom images
    eol: datetime = field(
        default_factory=lambda: datetime.strptime(
            "1970-01-01+0000", "%Y-%m-%d%z"
        )
    )
    esm_eol: datetime = field(
        default_factory=lambda: datetime.strptime(
            "1970-01-01+0000", "%Y-%m-%d%z"
        )
    )


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


class ImageManagementActivity:
    """
    Activities for image management
    """

    def __init__(self) -> None:
        self.client = self._create_client()

    def _create_client(self) -> AsyncClient:
        return AsyncClient()

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
    ) -> int:
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
                return resp.json()["items"][0]["id"]  # type: ignore
            elif resp.status_code == 200:
                return resp.json()["id"]  # type: ignore
            else:
                raise ApplicationError(
                    f"Got an unexpected response ({resp.status_code}) from MSM API: {resp.text}"
                )
        return items[0]["id"]  # type: ignore

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

        return await self._get_or_create(
            url, get_params, url, asset_dict, headers
        )

    @activity.defn(name=GET_OR_CREATE_VERSION_ACTIVITY)
    async def get_or_create_version(
        self, params: GetOrCreateVersionParams
    ) -> int:
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
        return await self._get_or_create(
            get_url, get_params, post_url, item_dict, headers
        )
