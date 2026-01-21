# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.
"""
Image download and delete activities.
"""

from dataclasses import dataclass
import hashlib
from os.path import join
import typing

import boto3
from temporalio import activity
from temporalio.exceptions import ApplicationError

from msm.common.workflows.sync import S3Params

from .base import BaseActivity

if typing.TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_s3.type_defs import CompletedPartTypeDef

MIN_S3_PART_SIZE = 5 * 1024**2  # 5MiB

DOWNLOAD_ASSET_ACTIVITY = "download-asset"
DELETE_ITEM_ACTIVITY = "delete-item"


@dataclass
class DownloadAssetParams:
    """Parameters for downloading an asset from SimpleStream to S3 storage.

    Args:
        ss_url: Full URL to the asset file in the SimpleStream source.
        msm_url: Base URL of the MSM API server for progress updates.
        msm_jwt: JWT token for authenticating with the MSM API.
        boot_asset_item_id: Unique identifier of the asset item being downloaded.
        s3_params: S3 configuration including bucket, path, and credentials.
    """

    ss_url: str
    msm_url: str
    msm_jwt: str
    boot_asset_item_id: int
    s3_params: S3Params


@dataclass
class DeleteItemParams:
    """Parameters for deleting an asset item from S3 storage.

    Args:
        s3_params: S3 configuration including bucket, path, and credentials.
        boot_asset_item_id: Unique identifier of the asset item to delete.
    """

    s3_params: S3Params
    boot_asset_item_id: int


class S3ResourceManager:
    """Manages S3 operations for boot asset storage with multipart upload support.

    Provides a comprehensive interface for S3 operations including multipart uploads,
    progress tracking, and cleanup operations. Handles large file uploads efficiently
    by using S3's multipart upload feature with automatic part management.

    The manager maintains upload state and provides methods for uploading parts,
    completing uploads, aborting failed uploads, and deleting objects. It automatically
    tracks bytes transferred and provides public read access to uploaded objects.
    """

    def __init__(
        self,
        s3_params: S3Params,
        boot_asset_item_id: int,
        multipart: bool = True,
    ) -> None:
        self._s3_client: S3Client = boto3.client(
            "s3",
            verify="/etc/ssl/certs/ca-certificates.crt",
            endpoint_url=s3_params.endpoint,
            aws_access_key_id=s3_params.access_key,
            aws_secret_access_key=s3_params.secret_key,
        )
        self.s3_path: str = s3_params.path
        self.s3_key: str = join(s3_params.path, str(boot_asset_item_id))
        self.bucket: str = s3_params.bucket
        self._upload_id: str | None = None
        if multipart:
            self._upload_id = self._create_multipart_upload()
        self._part_no: int = 1
        self._parts: list[CompletedPartTypeDef] = []
        self._bytes_sent: int = 0

    @property
    def bytes_sent(self) -> int:
        """Get the total number of bytes uploaded so far.

        Returns:
            Total bytes successfully uploaded to S3.
        """
        return self._bytes_sent

    @property
    def s3_client(self) -> "S3Client":
        """Get the underlying S3 client instance.

        Returns:
            Configured boto3 S3 client.
        """
        return self._s3_client

    def _create_multipart_upload(self) -> str:
        """Initialize a multipart upload session.

        Creates a new multipart upload with public-read ACL and SHA256 checksums
        enabled for integrity verification.

        Returns:
            Upload ID for the multipart upload session.
        """
        multipart_upload = self.s3_client.create_multipart_upload(
            ACL="public-read",
            Bucket=self.bucket,
            Key=self.s3_key,
            ChecksumAlgorithm="SHA256",
        )
        return multipart_upload["UploadId"]

    def upload_part(self, chunk: bytes) -> None:
        """Upload a single part of the multipart upload.

        Uploads one chunk of data as a numbered part in the multipart upload session.
        Automatically increments part numbers and tracks ETags for completion.
        Sends activity heartbeat signals to indicate progress.

        Args:
            chunk: Binary data chunk to upload (typically 5MB or larger).

        Raises:
            RuntimeError: If no multipart upload is in progress.
        """
        if self._upload_id is None:
            raise RuntimeError("Multipart operation is not in progress")
        part = self.s3_client.upload_part(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self._upload_id,
            PartNumber=self._part_no,
            Body=chunk,
            ChecksumAlgorithm="SHA256",
            ChecksumSHA256=hashlib.sha256(chunk).hexdigest(),
        )
        activity.heartbeat(f"Uploaded part {self._part_no}")
        self._parts.append({"ETag": part["ETag"], "PartNumber": self._part_no})
        self._part_no += 1
        self._bytes_sent += len(chunk)

    def complete_upload(self) -> None:
        """Finalize the multipart upload.

        Raises:
            RuntimeError: If no multipart upload is in progress.
        """
        if self._upload_id is None:
            raise RuntimeError("Multipart operation is not in progress")
        _ = self.s3_client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self._upload_id,
            MultipartUpload={"Parts": self._parts},
        )
        self._upload_id = None

    def abort_upload(self) -> None:
        """Cancel and clean up the multipart upload.

        Aborts the multipart upload session and frees up any storage used
        by uploaded parts. This should be called if an error occurs during
        upload to prevent partial data from consuming storage.

        Raises:
            RuntimeError: If no multipart upload is in progress.
        """
        if self._upload_id is None:
            raise RuntimeError("Multipart operation is not in progress")
        _ = self.s3_client.abort_multipart_upload(
            Bucket=self.bucket,
            Key=self.s3_key,
            UploadId=self._upload_id,
        )
        self._upload_id = None

    def delete_item(self) -> None:
        """Delete the object from S3 storage."""
        self.s3_client.delete_object(Bucket=self.bucket, Key=self.s3_key)


class ImageManagementActivities(BaseActivity):
    """Temporal activities for boot asset image management.

    The activities coordinate between SimpleStream sources, MSM API for progress updates,
    and S3 storage for persistent asset storage.
    """

    def _create_s3_manager(
        self,
        params: S3Params,
        item_id: int,
        multipart: bool = True,
    ) -> S3ResourceManager:
        """Create an S3 resource manager instance.

        Args:
            params: S3 configuration parameters.
            item_id: Boot asset item identifier for object naming.
            multipart: Whether to enable multipart upload support.

        Returns:
            Configured S3ResourceManager instance.
        """
        return S3ResourceManager(params, item_id, multipart=multipart)

    async def _update_bytes_synced(
        self,
        url: str,
        headers: dict[str, str],
        bytes_synced: int,
    ) -> bool:
        """Update download progress for a boot asset item.

        Reports the current number of bytes synced to the MSM API, allowing
        for progress tracking and potential resume operations. The API may
        return 404 if the item was deleted during download.

        Args:
            url: MSM API URL for the specific boot asset item.
            headers: HTTP headers including authentication.
            bytes_synced: Total number of bytes successfully downloaded.

        Returns:
            True if the item still exists and was updated, False if item was deleted.

        Raises:
            ApplicationError: If API returns unexpected error status.
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
        """Download a boot asset from SimpleStream source to S3 storage.

        Performs a streaming download from the SimpleStream URL to S3 using multipart
        upload for efficiency.

        The download can be cancelled if the MSM API indicates the item no longer
        exists, in which case the S3 upload is aborted and -1 is returned.

        Args:
            params: Download parameters including URLs, credentials, and item ID.

        Returns:
            Total number of bytes downloaded, or -1 if cancelled due to item deletion.

        Raises:
            ApplicationError: If MSM API requests fail.
            Exception: Various exceptions from HTTP or S3 operations are propagated
                      after cleanup.
        """
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

    @activity.defn(name=DELETE_ITEM_ACTIVITY)
    async def delete_item(self, params: DeleteItemParams) -> None:
        """Delete a boot asset item from S3 storage.

        Args:
            params: Deletion parameters including S3 configuration and item ID.
        """
        s3_manager = self._create_s3_manager(
            params.s3_params,
            params.boot_asset_item_id,
            multipart=False,
        )
        s3_manager.delete_item()
