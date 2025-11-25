from hashlib import sha256
from logging import getLogger
from typing import TYPE_CHECKING, Annotated, Any
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import run_in_threadpool
from streaming_form_data import StreamingFormDataParser  # type: ignore
from streaming_form_data.targets import BaseTarget, ValueTarget  # type: ignore
import streaming_form_data.validators  # type: ignore

from msm.apiserver.db import CUSTOM_IMAGE_SOURCE_ID, models
from msm.apiserver.dependencies import services
from msm.apiserver.exceptions.catalog import (
    BadRequestException,
    BaseExceptionDetail,
    FileTooLargeException,
    ForbiddenException,
    NotFoundException,
)
from msm.apiserver.exceptions.constants import ExceptionCode
from msm.apiserver.exceptions.responses import (
    BadRequestErrorResponseModel,
    ForbiddenErrorResponseModel,
    NotFoundErrorResponseModel,
    UnauthorizedErrorResponseModel,
    ValidationErrorResponseModel,
)
from msm.apiserver.service import S3Service, ServiceCollection
from msm.apiserver.service.images import END_OF_TIME
from msm.apiserver.user.auth import (
    authenticated_user,
    verify_authenticated_user_or_worker,
)
import msm.common.api.images as dm
from msm.common.enums import (
    BootAssetKind,
    BootAssetLabel,
    ItemFileType,
)
from msm.common.settings import Settings
from msm.common.time import now_utc

if TYPE_CHECKING:
    from mypy_boto3_s3.type_defs import CompletedPartTypeDef

logger = getLogger()

v1_router = APIRouter(prefix="/v1")


class S3MultipartUploadTarget(BaseTarget):  # type: ignore
    MIN_PART_SIZE = 5 * 1024**2  # 5MiB

    def __init__(
        self,
        s3: S3Service,
        filename: str,
        max_upload_size_gb: int,
    ) -> None:
        self.s3 = s3
        self.max_upload_size_bytes = max_upload_size_gb * 1000000000
        self.s3_key, self.upload_id = self.s3.create_multipart_upload(filename)
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

    def upload_current_chunk(self) -> None:
        etag = self.s3.upload_part(
            self.s3_key, self.upload_id, self.part_no, self.current_chunk
        )
        self.parts.append({"ETag": etag, "PartNumber": self.part_no})
        self.sha256.update(self.current_chunk)
        self.part_no += 1
        self.bytes_sent += len(self.current_chunk)
        self.current_chunk = b""

    def abort_upload(self) -> None:
        self.s3.abort_upload(
            self.s3_key,
            self.upload_id,
        )

    def complete_upload(self) -> None:
        self.s3.complete_upload(
            self.s3_key,
            self.upload_id,
            self.parts,
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
    "tgz": ItemFileType.ROOT_TGZ,
    "tbz": ItemFileType.ROOT_TBZ,
    "txz": ItemFileType.ROOT_TXZ,
    "ddtgz": ItemFileType.ROOT_DDTGZ,
    "ddtbz": ItemFileType.ROOT_DDTBZ,
    "ddtxz": ItemFileType.ROOT_DDTXZ,
    "ddtar": ItemFileType.ROOT_DDTAR,
    "ddbz2": ItemFileType.ROOT_DDBZ2,
    "ddgz": ItemFileType.ROOT_DDGZ,
    "ddxz": ItemFileType.ROOT_DDXZ,
    "ddraw": ItemFileType.ROOT_DDRAW,
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


def get_file_type_from_filename(filename: str) -> ItemFileType:
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
        services.s3,
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

    decoded_os = os.value.decode()
    decoded_release = release.value.decode()
    krel = decoded_release if decoded_os.lower() == "ubuntu" else None

    _, asset = await services.boot_assets.get_or_create(
        models.BootAssetCreate(
            boot_source_id=CUSTOM_IMAGE_SOURCE_ID,
            kind=BootAssetKind.OS,
            label=BootAssetLabel.STABLE,
            os=decoded_os,
            release=decoded_release,
            krel=krel,
            codename=None,
            title=title.value.decode(),
            arch=arch.value.decode(),
            subarch=None,
            compatibility=None,
            flavor=None,
            base_image=f"{decoded_os}/{decoded_release}",
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


@v1_router.post(
    "/images:remove",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        403: {"model": ForbiddenErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
    status_code=204,
)
async def delete_images(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    post_request: dm.ImagesRemovePostRequest,
    request: Request,
) -> None:
    count, assets = await services.boot_assets.get_many_by_id(
        post_request.asset_ids
    )
    if count != len(post_request.asset_ids):
        missing_ids = set(post_request.asset_ids) - set([a.id for a in assets])
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Some images were not found.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[
                        f"Boot Assets with IDs {list(missing_ids)} could not be found"
                    ],
                    field="asset_ids",
                    location="body",
                )
            ],
        )
    non_custom = [
        asset.id
        for asset in assets
        if asset.boot_source_id != CUSTOM_IMAGE_SOURCE_ID
    ]
    if non_custom:
        raise ForbiddenException(
            code=ExceptionCode.MISSING_PERMISSIONS,
            message="Non-custom images cannot be deleted",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_PERMISSIONS,
                    messages=[
                        f"Boot assets with IDs {non_custom} are not custom images."
                    ],
                    field="id",
                    location="path",
                )
            ],
        )
    request.state.ids_to_delete = await services.boot_assets.purge_assets(
        post_request.asset_ids
    )


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
