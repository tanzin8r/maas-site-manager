from functools import cached_property
from os.path import join
import typing

import boto3
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.service.base import Service
from msm.settings import Settings

if typing.TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_s3.type_defs import (
        CompletedPartTypeDef,
        GetObjectOutputTypeDef,
    )


class S3Service(Service):
    def __init__(
        self,
        connection: AsyncConnection,
        verify: bool = False,
        use_ssl: bool = False,
    ):
        super().__init__(connection)
        self.settings = Settings()
        self.verify = verify
        self.use_ssl = use_ssl

    @property
    def s3_endpoint(self) -> str:
        assert self.settings.s3_endpoint is not None
        return self.settings.s3_endpoint

    @property
    def s3_bucket(self) -> str:
        assert self.settings.s3_bucket is not None
        return self.settings.s3_bucket

    @property
    def s3_path(self) -> str:
        assert self.settings.s3_path is not None
        return self.settings.s3_path

    @property
    def s3_access_key(self) -> str:
        assert self.settings.s3_access_key is not None
        return self.settings.s3_access_key

    @property
    def s3_secret_key(self) -> str:
        assert self.settings.s3_secret_key is not None
        return self.settings.s3_secret_key

    @cached_property
    def s3_client(self) -> "S3Client":
        return boto3.client(
            "s3",
            use_ssl=self.use_ssl,
            verify=self.verify,
            endpoint_url=self.s3_endpoint,
            aws_access_key_id=self.s3_access_key,
            aws_secret_access_key=self.s3_secret_key,
        )

    def create_multipart_upload(self, path: str) -> tuple[str, str]:
        s3_key = join(self.s3_path, path)
        multipart_upload = self.s3_client.create_multipart_upload(
            ACL="public-read",
            Bucket=self.s3_bucket,
            Key=s3_key,
            ChecksumAlgorithm="SHA256",
        )
        return s3_key, multipart_upload["UploadId"]

    def upload_part(
        self, s3_key: str, upload_id: str, part_no: int, chunk: bytes
    ) -> str:
        part = self.s3_client.upload_part(
            Bucket=self.s3_bucket,
            Key=s3_key,
            UploadId=upload_id,
            PartNumber=part_no,
            Body=chunk,
            ChecksumAlgorithm="SHA256",
        )
        return part["ETag"]

    def complete_upload(
        self,
        s3_key: str,
        upload_id: str,
        parts: typing.Sequence["CompletedPartTypeDef"],
    ) -> None:
        self.s3_client.complete_multipart_upload(
            Bucket=self.s3_bucket,
            Key=s3_key,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts},
        )

    def abort_upload(
        self,
        s3_key: str,
        upload_id: str,
    ) -> None:
        self.s3_client.abort_multipart_upload(
            Bucket=self.s3_bucket,
            Key=s3_key,
            UploadId=upload_id,
        )

    def delete_object(self, path: str) -> None:
        s3_key = join(self.s3_path, path)
        self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_key)

    def get_object(self, path: str) -> "GetObjectOutputTypeDef":
        s3_key = join(self.s3_path, path)
        return self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_key)
