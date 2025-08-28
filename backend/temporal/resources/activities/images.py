from dataclasses import dataclass
from os.path import join
import typing

import boto3
from temporalio import activity
from temporalio.exceptions import ApplicationError

from .base import BaseActivity

if typing.TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_s3.type_defs import CompletedPartTypeDef

MIN_S3_PART_SIZE = 5 * 1024**2  # 5MiB

DOWNLOAD_ASSET_ACTIVITY = "download-asset"
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


class S3ResourceManager:
    def __init__(
        self,
        s3_params: S3Params,
        boot_asset_item_id: int,
        use_ssl: bool = False,
        verify: bool = False,
    ) -> None:
        self._s3_client = boto3.client(
            "s3",
            use_ssl=use_ssl,
            verify=verify,
            endpoint_url=s3_params.endpoint,
            aws_access_key_id=s3_params.access_key,
            aws_secret_access_key=s3_params.secret_key,
        )
        self.s3_path = s3_params.path
        self.s3_key = join(s3_params.path, str(boot_asset_item_id))
        self.bucket = s3_params.bucket
        self._upload_id: str | None = self._create_multipart_upload()
        self._part_no = 1
        self._parts: list[CompletedPartTypeDef] = []
        self._bytes_sent = 0

    @property
    def bytes_sent(self) -> int:
        return self._bytes_sent

    @property
    def s3_client(self) -> "S3Client":
        return self._s3_client

    def _create_multipart_upload(self) -> str:
        multipart_upload = self.s3_client.create_multipart_upload(
            ACL="public-read",
            Bucket=self.bucket,
            Key=self.s3_key,
            ChecksumAlgorithm="SHA256",
        )
        return multipart_upload["UploadId"]

    def upload_part(self, chunk: bytes) -> None:
        if self._upload_id is None:
            raise RuntimeError("Multipart operation is not in progress")
        part = self.s3_client.upload_part(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self._upload_id,
            PartNumber=self._part_no,
            Body=chunk,
            ChecksumAlgorithm="SHA256",
        )
        activity.heartbeat(f"Uploaded part {self._part_no}")
        self._parts.append({"ETag": part["ETag"], "PartNumber": self._part_no})
        self._part_no += 1
        self._bytes_sent += len(chunk)

    def complete_upload(self) -> None:
        if self._upload_id is None:
            raise RuntimeError("Multipart operation is not in progress")
        self.s3_client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self._upload_id,
            MultipartUpload={"Parts": self._parts},
        )
        self._upload_id = None

    def abort_upload(self) -> None:
        if self._upload_id is None:
            raise RuntimeError("Multipart operation is not in progress")
        self.s3_client.abort_multipart_upload(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self._upload_id,
        )
        self._upload_id = None


class ImageManagementActivities(BaseActivity):
    """
    Activities for image management
    """

    def _create_s3_manager(
        self,
        params: S3Params,
        item_id: int,
    ) -> S3ResourceManager:
        return S3ResourceManager(params, item_id)

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

        msm_url = "/".join(
            [
                params.msm_url.rstrip("/"),
                f"api/v1/bootasset-items/{params.boot_asset_item_id}",
            ],
        )
        msm_headers = self._get_header(params.msm_jwt)
        try:
            async with self.client.stream(
                "GET", params.ss_url, timeout=7200
            ) as r:
                async for data in r.aiter_raw(chunk_size=MIN_S3_PART_SIZE):
                    s3_manager.upload_part(data)
                    activity.heartbeat(
                        f"Uploaded {s3_manager.bytes_sent} bytes to storage."
                    )
                    if not await self._update_bytes_synced(
                        msm_url, msm_headers, s3_manager.bytes_sent
                    ):
                        activity.logger.info(
                            f"Item at {msm_url} no longer exists, aborting download"
                        )
                        s3_manager.abort_upload()
                        return -1
                s3_manager.complete_upload()
        except:
            s3_manager.abort_upload()
            raise
        return s3_manager.bytes_sent
