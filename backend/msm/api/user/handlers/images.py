from hashlib import sha256
import json
from logging import getLogger
from math import ceil
from os.path import join
from socket import gethostname
from typing import TYPE_CHECKING, Annotated, Any
from urllib.parse import urlparse

import boto3
from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from starlette.types import Send
from streaming_form_data import StreamingFormDataParser  # type: ignore
from streaming_form_data.targets import BaseTarget, ValueTarget  # type: ignore
import streaming_form_data.validators  # type: ignore

from msm.api.dependencies import services
from msm.api.exceptions.catalog import (
    BadRequestException,
    BaseExceptionDetail,
    FileTooLargeException,
    NotFoundException,
)
from msm.api.exceptions.constants import ExceptionCode
from msm.api.exceptions.responses import (
    BadRequestErrorResponseModel,
    NotFoundErrorResponseModel,
    UnauthorizedErrorResponseModel,
    ValidationErrorResponseModel,
)
from msm.api.user.auth import (
    authenticated_user,
    verify_authenticated_user_or_worker,
)
import msm.api.user.models.images as dm
from msm.db import CUSTOM_IMAGE_SOURCE_ID, models
from msm.service import ServiceCollection
from msm.service.images import END_OF_TIME, reverse_fqdn
from msm.settings import Settings
from msm.time import now_utc

if TYPE_CHECKING:
    from mypy_boto3_s3.type_defs import CompletedPartTypeDef

logger = getLogger()

v1_router = APIRouter(prefix="/v1")


class S3StreamResponse(StreamingResponse):
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str = "application/octet-stream",
        background: BackgroundTask | None = None,
        file_id: str = "",
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)
        settings = Settings()
        assert settings.s3_bucket is not None
        self.file_path = join(
            settings.s3_path if settings.s3_path else "",
            file_id,
        )
        self.s3_bucket = settings.s3_bucket
        self.s3 = boto3.resource(
            "s3",
            use_ssl=False,
            verify=False,
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )

    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )

        result = self.s3.meta.client.get_object(
            Bucket=self.s3_bucket, Key=self.file_path
        )

        for chunk in result["Body"]:
            await send(
                {
                    "type": "http.response.body",
                    "body": chunk,
                    "more_body": True,
                }
            )

        await send(
            {"type": "http.response.body", "body": b"", "more_body": False}
        )


class IndexStreamResponse(StreamingResponse):
    def __init__(
        self,
        content: Any,
        json_obj: dict[str, Any],
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str = "application/json",
        background: BackgroundTask | None = None,
        chunk_size: int = 1024**2,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)
        self.json_obj = json_obj
        self.chunk_size = chunk_size

    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        json_str = json.dumps(self.json_obj).encode()
        chunks = ceil(len(json_str) / self.chunk_size)
        for c in range(chunks):
            await send(
                {
                    "type": "http.response.body",
                    "body": json_str[
                        c * self.chunk_size : c * self.chunk_size
                        + self.chunk_size
                    ],
                    "more_body": True,
                }
            )

        await send(
            {"type": "http.response.body", "body": b"", "more_body": False}
        )


@v1_router.get(
    "/images/{track}/{risk}/streams/v1/{index_path:path}",
    responses={
        400: {"model": BadRequestErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
    },
)
async def download_index(
    services: Annotated[ServiceCollection, Depends(services)],
    track: str,
    risk: str,
    index_path: str,
) -> StreamingResponse:
    errors: list[BaseExceptionDetail] = []

    if track != "latest":
        errors.append(
            BaseExceptionDetail(
                reason=ExceptionCode.INVALID_PARAMS,
                messages=[f"Invalid track '{track}' requested"],
                field="track",
                location="path",
            )
        )

    if risk != "stable":
        errors.append(
            BaseExceptionDetail(
                reason=ExceptionCode.INVALID_PARAMS,
                messages=[f"Invalid risk '{risk}' requested"],
                field="risk",
                location="path",
            )
        )

    if errors:
        raise BadRequestException(
            code=ExceptionCode.INVALID_PARAMS,
            message="Invalid track/risk requested.",
            details=errors,
        )

    service_url = await services.settings.get_service_url()
    parsed = urlparse(service_url)
    fqdn = parsed.hostname if parsed.hostname else gethostname()
    reversed_fqdn = reverse_fqdn(fqdn)

    if index_path == "index.json":
        index = await services.index_service.get(models.IndexType.INDEX, fqdn)
        return IndexStreamResponse(None, index)
    elif index_path == f"{reversed_fqdn}:stream:v1:download.json":
        index = await services.index_service.get(
            models.IndexType.DOWNLOAD, fqdn
        )
        return IndexStreamResponse(None, index)
    else:
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Index file does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"Index file '{index_path}' does not exist"],
                    field="index_path",
                    location="path",
                )
            ],
        )


@v1_router.get(
    "/images/{track}/{risk}/{boot_source_id}/{file_path:path}",
    responses={
        400: {"model": BadRequestErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
    },
)
async def download(
    services: Annotated[ServiceCollection, Depends(services)],
    track: str,
    risk: str,
    boot_source_id: int,
    file_path: str,
) -> StreamingResponse:
    errors: list[BaseExceptionDetail] = []

    if track != "latest":
        errors.append(
            BaseExceptionDetail(
                reason=ExceptionCode.INVALID_PARAMS,
                messages=[f"Invalid track '{track}' requested"],
                field="track",
                location="path",
            )
        )

    if risk != "stable":
        errors.append(
            BaseExceptionDetail(
                reason=ExceptionCode.INVALID_PARAMS,
                messages=[f"Invalid risk '{risk}' requested"],
                field="risk",
                location="path",
            )
        )

    if errors:
        raise BadRequestException(
            code=ExceptionCode.INVALID_PARAMS,
            message="Invalid track/risk requested.",
            details=errors,
        )

    boot_item = await services.boot_asset_items.get_by_path(
        boot_source_id, file_path
    )
    if not boot_item:
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Asset Item does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"BootAssetItem '{file_path}' does not exist"],
                    field="file_path",
                    location="path",
                )
            ],
        )
    return S3StreamResponse(content=None, file_id=str(boot_item.id))


class S3MultipartUploadTarget(BaseTarget):  # type: ignore
    MIN_PART_SIZE = 5 * 1024**2  # 5MiB

    def __init__(
        self, settings: Settings, filename: str, max_upload_size_gb: int
    ) -> None:
        self.s3 = boto3.resource(
            "s3",
            use_ssl=False,
            verify=False,
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )
        assert settings.s3_bucket is not None
        self.s3_bucket = settings.s3_bucket
        self.filename = join(
            settings.s3_path if settings.s3_path else "",
            filename,
        )
        self.max_upload_size_bytes = max_upload_size_gb * 1000000000
        multipart_upload = self.s3.meta.client.create_multipart_upload(
            ACL="public-read",
            Bucket=settings.s3_bucket,
            Key=filename,
            ChecksumAlgorithm="SHA256",
        )
        self.upload_id = multipart_upload["UploadId"]
        self.current_chunk = b""
        self.part_no = 1
        self.parts: list[CompletedPartTypeDef] = []
        self.bytes_sent = 0
        self.sha256 = sha256()
        super().__init__(
            validator=streaming_form_data.validators.MaxSizeValidator(
                self.max_upload_size_bytes
            )
        )

    def upload(self) -> None:
        multipart_upload_part = self.s3.MultipartUploadPart(
            self.s3_bucket, self.filename, self.upload_id, self.part_no
        )
        part = multipart_upload_part.upload(
            Body=self.current_chunk,
            ChecksumAlgorithm="SHA256",
        )
        self.parts.append({"ETag": part["ETag"], "PartNumber": self.part_no})

    def upload_current_chunk(self) -> None:
        self.upload()
        self.sha256.update(self.current_chunk)
        self.part_no += 1
        self.bytes_sent += len(self.current_chunk)
        self.current_chunk = b""

    def abort_upload(self) -> None:
        self.s3.meta.client.abort_multipart_upload(
            Bucket=self.s3_bucket,
            Key=self.filename,
            UploadId=self.upload_id,
        )

    def complete_upload(self) -> None:
        self.s3.meta.client.complete_multipart_upload(
            Bucket=self.s3_bucket,
            Key=self.filename,
            UploadId=self.upload_id,
            MultipartUpload={"Parts": self.parts},
        )

    def on_data_received(self, chunk: bytes) -> None:
        self.current_chunk += chunk
        if len(self.current_chunk) < self.MIN_PART_SIZE:
            return
        self.upload_current_chunk()


class BootAssetItemValueValidator:
    def __init__(self, type: type, name: str, invalid_values: list[Any] = []):
        self._type = type
        self._name = name
        self._invalid_values = invalid_values

    def __call__(self, chunk: bytes) -> None:
        try:
            self._type(chunk)
        except:
            raise BadRequestException(
                message=f"Invalid type for {self._name}, expected {self._type}",
                code=ExceptionCode.INVALID_PARAMS,
                details=[
                    BaseExceptionDetail(
                        reason=ExceptionCode.INVALID_PARAMS,
                        messages=[f"Invalid type for {self._name}"],
                        field=self._name,
                        location="body",
                    )
                ],
            )
        value = self._type(chunk.decode())
        if value in self._invalid_values:
            raise BadRequestException(
                message=f"Invalid value for {self._name}: {value}",
                code=ExceptionCode.INVALID_PARAMS,
                details=[
                    BaseExceptionDetail(
                        reason=ExceptionCode.INVALID_PARAMS,
                        messages=[
                            f"{self._name} cannot be any of {self._invalid_values}"
                        ],
                        field=self._name,
                        location="body",
                    )
                ],
            )


CUSTOM_IMAGE_FILE_EXTENSIONS = {
    "tgz": models.ItemFileType.ROOT_TGZ,
    "tbz": models.ItemFileType.ROOT_TBZ,
    "txz": models.ItemFileType.ROOT_TXZ,
    "ddtgz": models.ItemFileType.ROOT_DDTGZ,
    "ddtbz": models.ItemFileType.ROOT_DDTBZ,
    "ddtxz": models.ItemFileType.ROOT_DDTXZ,
    "ddtar": models.ItemFileType.ROOT_DDTAR,
    "ddbz2": models.ItemFileType.ROOT_DDBZ2,
    "ddgz": models.ItemFileType.ROOT_DDGZ,
    "ddxz": models.ItemFileType.ROOT_DDXZ,
    "ddraw": models.ItemFileType.ROOT_DDRAW,
}


class FilenameValueValidator:
    def __init__(self, type: type, name: str):
        self._type = type
        self._name = name

    def __call__(self, chunk: bytes) -> None:
        try:
            self._type(chunk)
        except:
            raise BadRequestException(
                message=f"Invalid type for {self._name}, expected {self._type}",
                code=ExceptionCode.INVALID_PARAMS,
                details=[
                    BaseExceptionDetail(
                        reason=ExceptionCode.INVALID_PARAMS,
                        messages=[f"Invalid type for {self._name}"],
                        field=self._name,
                        location="body",
                    )
                ],
            )
        ext = chunk.decode().split(".")[-1]
        if ext not in CUSTOM_IMAGE_FILE_EXTENSIONS.keys():
            raise BadRequestException(
                message="Unsupported file type",
                code=ExceptionCode.INVALID_PARAMS,
                details=[
                    BaseExceptionDetail(
                        reason=ExceptionCode.INVALID_PARAMS,
                        messages=[
                            f"Unsupported file type {ext}, must be one of {CUSTOM_IMAGE_FILE_EXTENSIONS.keys()}"
                        ],
                        field="filename",
                        location="body",
                    )
                ],
            )


def get_file_type_from_filename(filename: str) -> models.ItemFileType:
    ext = filename.split(".")[-1]
    # ext is verified above, don't need to handle KeyError
    return CUSTOM_IMAGE_FILE_EXTENSIONS[ext]


@v1_router.post(
    "/images",
    responses={
        400: {"model": BadRequestErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "properties": {
                            "os": {
                                "type": "string",
                                "example": "ubuntu",
                            },
                            "release": {
                                "type": "string",
                                "example": "noble",
                            },
                            "title": {
                                "type": "string",
                                "example": "My Custom Image",
                            },
                            "arch": {
                                "type": "string",
                                "example": "amd64",
                            },
                            "file_size": {
                                "type": "number",
                                "example": 123456789,
                            },
                            "filename": {
                                "type": "string",
                                "example": "custom-image.tgz",
                            },
                            "file": {
                                "type": "string",
                                "format": "binary",
                            },
                        }
                    }
                }
            },
        },
    },
)
async def post_images(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    request: Request,
) -> dm.ImagesPostResponse:
    settings = Settings()
    api_settings = await services.settings.get()
    if not urlparse(settings.s3_endpoint).scheme:
        settings.s3_endpoint = f"http://{settings.s3_endpoint}"

    parser = StreamingFormDataParser(headers=request.headers)
    os = ValueTarget(
        validator=BootAssetItemValueValidator(
            str, "os", invalid_values=["ubuntu"]
        )
    )
    parser.register("os", os)
    release = ValueTarget(
        validator=BootAssetItemValueValidator(str, "release")
    )
    parser.register("release", release)
    title = ValueTarget(validator=BootAssetItemValueValidator(str, "title"))
    parser.register("title", title)
    arch = ValueTarget(validator=BootAssetItemValueValidator(str, "arch"))
    parser.register("arch", arch)
    file_size = ValueTarget(
        validator=BootAssetItemValueValidator(int, "file_size")
    )
    parser.register("file_size", file_size)
    filename = ValueTarget(validator=FilenameValueValidator(str, "filename"))
    parser.register("filename", filename)

    tmp_item = await services.boot_asset_items.create_temporary()
    s3_upload_target = S3MultipartUploadTarget(
        settings,
        str(tmp_item.id),
        api_settings.max_image_upload_size_gb,
    )
    parser.register("file", s3_upload_target)

    async for chunk in request.stream():
        try:
            await run_in_threadpool(parser.data_received, chunk)
        except streaming_form_data.validators.ValidationError:
            await services.boot_asset_items.delete(tmp_item.id)
            await run_in_threadpool(s3_upload_target.abort_upload)
            raise FileTooLargeException(
                message="Uploaded file is too large",
                code=ExceptionCode.FILE_TOO_LARGE,
                details=[
                    BaseExceptionDetail(
                        reason=ExceptionCode.FILE_TOO_LARGE,
                        messages=["Uploaded file is too large"],
                        field="file",
                        location="body",
                    )
                ],
            )
        except BadRequestException:
            await services.boot_asset_items.delete(tmp_item.id)
            raise

    # last part may have been left behind if it was smaller than
    # the minimum upload size.
    # the last upload has no minimum upload size requirement.
    if s3_upload_target.current_chunk:
        await run_in_threadpool(s3_upload_target.upload_current_chunk)

    _, asset = await services.boot_assets.get_or_create(
        models.BootAssetCreate(
            boot_source_id=CUSTOM_IMAGE_SOURCE_ID,
            kind=models.BootAssetKind.OS,
            label=models.BootAssetLabel.STABLE,
            os=os.value.decode(),
            release=release.value.decode(),
            codename=None,
            title=title.value.decode(),
            arch=arch.value.decode(),
            subarch=None,
            compatibility=None,
            flavor=None,
            base_image=f"{os.value.decode()}/{release.value.decode()}",
            eol=END_OF_TIME,
            esm_eol=END_OF_TIME,
            signed=False,
        )
    )
    version = await services.boot_asset_versions.create_next_revision(
        asset.id, now_utc()
    )
    clean_filename = filename.value.decode().replace(" ", "")
    boot_asset_item = await services.boot_asset_items.update(
        tmp_item.id,
        models.BootAssetItemUpdate(
            boot_asset_version_id=version.id,
            ftype=get_file_type_from_filename(clean_filename),
            path=f"{asset.release}/{asset.arch}/{version.version}/{clean_filename}",
            file_size=int(file_size.value),
            sha256=s3_upload_target.sha256.hexdigest(),
        ),
    )
    if boot_asset_item.file_size != s3_upload_target.bytes_sent:
        await services.boot_asset_items.delete(boot_asset_item.id)
        await services.boot_asset_versions.delete(version.id)
        await services.boot_assets.delete(asset.id)
        await run_in_threadpool(s3_upload_target.abort_upload)
        raise BadRequestException(
            message="The size of the uploaded file does not match the 'file_size' parameter in the request",
            code=ExceptionCode.INVALID_PARAMS,
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.INVALID_PARAMS,
                    messages=["File size does not match uploaded bytes"],
                    field="size",
                    location="body",
                )
            ],
        )
    await services.boot_asset_items.update_bytes_synced(
        boot_asset_item.id, s3_upload_target.bytes_sent
    )
    await run_in_threadpool(s3_upload_target.complete_upload)
    return dm.ImagesPostResponse.from_model(boot_asset_item)


@v1_router.get(
    "/refresh-index",
)
async def refresh_index(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[
        models.User | models.Worker,
        Depends(verify_authenticated_user_or_worker),
    ],
) -> None:
    await services.index_service.refresh()
