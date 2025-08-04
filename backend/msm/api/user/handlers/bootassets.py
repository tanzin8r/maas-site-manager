from logging import getLogger
from typing import Annotated

import boto3  # type: ignore
from fastapi import APIRouter, Depends, Path
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import IntegrityError

from msm.api.dependencies import services
from msm.api.exceptions.catalog import (
    AlreadyExistsException,
    BaseExceptionDetail,
    ForbiddenException,
    NotFoundException,
)
from msm.api.exceptions.constants import ExceptionCode
from msm.api.exceptions.responses import (
    AlreadyExistsErrorResponseModel,
    ForbiddenErrorResponseModel,
    NotFoundErrorResponseModel,
    UnauthorizedErrorResponseModel,
    ValidationErrorResponseModel,
)
from msm.api.user.auth import (
    authenticated_user,
    verify_authenticated_user_or_worker,
)
from msm.api.user.forms import (
    BootAssetFilterParams,
    BootAssetItemFilterParams,
    BootAssetVersionFilterParams,
    boot_asset_filter_params,
    boot_asset_item_filter_params,
    boot_asset_version_filter_params,
)
import msm.api.user.models.bootassets as dm
from msm.db import models
from msm.schema import (
    PaginationParams,
    SortParam,
    SortParamParser,
)
from msm.service import ServiceCollection
from msm.settings import Settings

logger = getLogger()

v1_router = APIRouter(prefix="/v1")

boot_asset_sort_parameters = SortParamParser(
    fields=[
        "kind",
        "label",
        "os",
        "release",
        "codename",
        "title",
        "arch",
        "subarch",
        "compatibility",
        "flavor",
        "base_image",
        "bootloader_type",
        "eol",
        "esm_eol",
        "signed",
    ]
)


boot_sources_sort_parameters = SortParamParser(
    fields=[
        "url",
        "keyring",
        "sync_interval",
        "priority",
    ]
)


boot_source_selection_sort_parameters = SortParamParser(
    fields=[
        "label",
        "os",
        "release",
        "available",
    ]
)


@v1_router.get(
    "/bootassets",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get_boot_assets(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[
        models.User | None, Depends(verify_authenticated_user_or_worker)
    ],
    sort_params: Annotated[
        list[SortParam], Depends(boot_asset_sort_parameters)
    ],
    pagination_params: Annotated[PaginationParams, Depends()],
    filter_params: Annotated[
        BootAssetFilterParams, Depends(boot_asset_filter_params)
    ],
) -> dm.BootAssetsGetResponse:
    """Return boot assets."""
    total, results = await services.boot_assets.get(
        sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
        **filter_params._asdict(),
    )
    return dm.BootAssetsGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


@v1_router.post(
    "/bootassets",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        409: {"model": AlreadyExistsErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def post_boot_assets(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[
        models.User | None, Depends(verify_authenticated_user_or_worker)
    ],
    post_request: dm.BootAssetsPostRequest,
) -> dm.BootAssetsPostResponse:
    if not await services.boot_sources.get_by_id(post_request.boot_source_id):
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Source does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[
                        f"BootSource ID {post_request.boot_source_id} does not exist"
                    ],
                    field="bootsource_id",
                    location="body",
                )
            ],
        )
    try:
        boot_asset = await services.boot_assets.create(
            models.BootAssetCreate(**post_request.model_dump())
        )
        return dm.BootAssetsPostResponse(id=boot_asset.id)
    except IntegrityError:
        raise AlreadyExistsException(
            code=ExceptionCode.ALREADY_EXISTS,
            message="This boot asset already exists.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.ALREADY_EXISTS,
                    messages=[
                        "This boot asset already exists for the given boot source."
                    ],
                    field="os,release,arch,subarch",
                    location="body",
                )
            ],
        )


@v1_router.get(
    "/bootasset-sources",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get_boot_sources(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    sort_params: Annotated[
        list[SortParam], Depends(boot_sources_sort_parameters)
    ],
    pagination_params: Annotated[PaginationParams, Depends()],
) -> dm.BootSourcesGetResponse:
    """Return boot sources."""
    total, results = await services.boot_sources.get(
        sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
    )
    return dm.BootSourcesGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


@v1_router.get(
    "/bootasset-sources/{id}",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get_boot_source_by_id(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    id: int,
) -> dm.BootSourceGetResponse:
    bs = await services.boot_sources.get_by_id(id)
    if bs is None:
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Source does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"BootSource ID {id} does not exist"],
                    field="id",
                    location="path",
                )
            ],
        )
    return dm.BootSourceGetResponse.from_model(bs)


@v1_router.post(
    "/bootasset-sources",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def post_boot_sources(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    post_request: dm.BootSourcesPostRequest,
) -> dm.BootSourcesPostResponse:
    boot_source = await services.boot_sources.create(
        models.BootSourceCreate(**post_request.model_dump())
    )
    await services.index_service.refresh()
    return dm.BootSourcesPostResponse(id=boot_source.id)


@v1_router.patch(
    "/bootasset-sources/{id}",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def patch_boot_source(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    id: Annotated[
        int, Path(title="The ID of the Boot Source to update", ge=2)
    ],
    patch_request: dm.BootSourcesPatchRequest,
) -> dm.BootSourcePatchResponse:
    bs = await services.boot_sources.get_by_id(id)
    if bs is None:
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Source does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"BootSource ID {id} does not exist"],
                    field="id",
                    location="path",
                )
            ],
        )
    updated_source = await services.boot_sources.update(
        id, models.BootSourceUpdate(**patch_request.model_dump())
    )
    await services.index_service.refresh()
    return dm.BootSourcePatchResponse.from_model(updated_source)


@v1_router.delete(
    "/bootasset-sources/{id}",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def delete_boot_source(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    id: Annotated[
        int, Path(title="The ID of the Boot Source to delete", ge=2)
    ],
) -> None:
    bs = await services.boot_sources.get_by_id(id)
    if bs is None:
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Source does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"BootSource ID {id} does not exist"],
                    field="id",
                    location="path",
                )
            ],
        )
    await services.purge_source(id)
    await services.index_service.refresh()


@v1_router.get(
    "/bootasset-sources/{id}/selections",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get_boot_source_selections(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    id: int,
    sort_params: Annotated[
        list[SortParam], Depends(boot_source_selection_sort_parameters)
    ],
    pagination_params: Annotated[PaginationParams, Depends()],
) -> dm.BootSourceSelectionsGetResponse:
    """Return boot source selections."""
    total, results = await services.boot_source_selections.get(
        id,
        sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
    )
    return dm.BootSourceSelectionsGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


@v1_router.put(
    "/bootasset-sources/{id}/available-selections",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def put_boot_source_avail_selections(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    id: int,
    patch_request: dm.BootSourceAvailSelectionsPutRequest,
) -> dm.BootSourceAvailSelectionsPutResponse:
    bs = await services.boot_sources.get_by_id(id)
    if bs is None:
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Source does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"BootSource ID {id} does not exist"],
                    field="id",
                    location="path",
                )
            ],
        )

    _, existing = await services.boot_source_selections.get(id, [])
    incoming_map = {(p.os, p.release): p for p in patch_request.available}
    existing_map = {(p.os, p.release): p for p in existing}

    stale_keys = set(existing_map.keys()) - set(incoming_map.keys())

    for in_k, in_v in incoming_map.items():
        if cur := existing_map.get(in_k, None):
            await services.boot_source_selections.update(
                boot_source_id=cur.boot_source_id,
                selection_id=cur.id,
                details=models.BootSourceSelectionUpdate(
                    available=in_v.arches,
                ),
            )
        else:
            await services.boot_source_selections.create(
                models.BootSourceSelectionCreate(
                    boot_source_id=id,
                    label=in_v.label,
                    os=in_v.os,
                    release=in_v.release,
                    available=in_v.arches,
                    selected=[],
                )
            )

    stale = []
    for cur_k, cur_v in existing_map.items():
        if cur_k in stale_keys:
            stale.append(cur_v)
            if len(cur_v.selected) == 0:
                await services.boot_source_selections.delete(
                    cur_v.boot_source_id, cur_v.id
                )

    await services.index_service.refresh()
    return dm.BootSourceAvailSelectionsPutResponse(stale=stale)


@v1_router.post(
    "/bootassets/{id}/versions",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        409: {"model": AlreadyExistsErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def post_boot_asset_version(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[
        models.User | None, Depends(verify_authenticated_user_or_worker)
    ],
    id: int,
    post_request: dm.BootAssetVersionPostRequest,
) -> dm.BootAssetVersionPostResponse:
    if not await services.boot_assets.get_by_id(id):
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Asset does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"BootAsset ID {id} does not exist"],
                    field="id",
                    location="path",
                )
            ],
        )

    try:
        boot_asset_version = await services.boot_asset_versions.create(
            models.BootAssetVersionCreate(
                boot_asset_id=id, version=post_request.version
            )
        )
        return dm.BootAssetVersionPostResponse(id=boot_asset_version.id)
    except IntegrityError:
        raise AlreadyExistsException(
            code=ExceptionCode.ALREADY_EXISTS,
            message="This boot asset version already exists.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.ALREADY_EXISTS,
                    messages=[
                        "This boot asset version already exists for the given boot asset."
                    ],
                    field="version",
                    location="body",
                )
            ],
        )


boot_asset_version_sort_parameters = SortParamParser(
    fields=[
        "version",
    ]
)


@v1_router.get(
    "/bootasset-versions",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get_boot_asset_versions(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[
        models.User | None, Depends(verify_authenticated_user_or_worker)
    ],
    sort_params: Annotated[
        list[SortParam], Depends(boot_asset_version_sort_parameters)
    ],
    pagination_params: Annotated[PaginationParams, Depends()],
    filter_params: Annotated[
        BootAssetVersionFilterParams, Depends(boot_asset_version_filter_params)
    ],
) -> dm.BootAssetVersionsGetResponse:
    """Return Boot Asset Versions"""
    total, results = await services.boot_asset_versions.get(
        sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
        **filter_params._asdict(),
    )
    return dm.BootAssetVersionsGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


@v1_router.post(
    "/bootasset-versions/{id}/items",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        409: {"model": AlreadyExistsErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def post_boot_asset_item(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[
        models.User | None, Depends(verify_authenticated_user_or_worker)
    ],
    id: int,
    post_request: dm.BootAssetItemPostRequest,
) -> dm.BootAssetItemPostResponse:
    if not await services.boot_asset_versions.get_by_id(id):
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Asset Version does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"BootAssetVersion ID {id} does not exist"],
                    field="id",
                    location="path",
                )
            ],
        )

    try:
        item = await services.boot_asset_items.create(
            models.BootAssetItemCreate(
                boot_asset_version_id=id, **post_request.model_dump()
            )
        )
        await services.index_service.refresh()
        return dm.BootAssetItemPostResponse(id=item.id)
    except IntegrityError:
        raise AlreadyExistsException(
            code=ExceptionCode.ALREADY_EXISTS,
            message="This boot asset item already exists.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.ALREADY_EXISTS,
                    messages=[
                        "This boot asset item already exists for the given boot asset version."
                    ],
                    field="ftype",
                    location="body",
                )
            ],
        )


boot_asset_items_sort_parameters = SortParamParser(
    fields=[
        "ftype",
        "sha256",
        "path",
        "file_size",
        "source_package",
        "source_version",
        "source_release",
        "bytes_synced",
    ]
)


@v1_router.get(
    "/bootasset-items",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get_boot_asset_items(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[
        models.User | None, Depends(verify_authenticated_user_or_worker)
    ],
    sort_params: Annotated[
        list[SortParam], Depends(boot_asset_items_sort_parameters)
    ],
    pagination_params: Annotated[PaginationParams, Depends()],
    filter_params: Annotated[
        BootAssetItemFilterParams, Depends(boot_asset_item_filter_params)
    ],
) -> dm.BootAssetItemsGetResponse:
    total, results = await services.boot_asset_items.get(
        sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
        **filter_params._asdict(),
    )
    return dm.BootAssetItemsGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


@v1_router.delete(
    "/bootasset-items/{id}",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def delete_images(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    id: int,
) -> None:
    boot_asset_version = await services.boot_asset_items.get_by_id(id)
    if not boot_asset_version:
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Asset Item does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"BootAssetItem ID {id} does not exist"],
                    field="id",
                    location="path",
                )
            ],
        )
    settings = Settings()
    s3 = boto3.resource(
        "s3",
        use_ssl=False,
        verify=False,
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )
    await run_in_threadpool(
        s3.meta.client.delete_object, Bucket=settings.s3_bucket, Key=str(id)
    )
    await services.delete_item_and_purge(id)
    await services.index_service.refresh()


@v1_router.patch(
    "/bootasset-items/{id}",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        403: {"model": ForbiddenErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def patch_boot_asset_items(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[
        models.User | None, Depends(verify_authenticated_user_or_worker)
    ],
    id: int,
    patch_request: dm.BootAssetItemPatchRequest,
) -> dm.BootAssetItemPatchResponse:
    if (
        patch_request.bytes_synced is not None
        and authenticated_user is not None
    ):
        raise ForbiddenException(
            code=ExceptionCode.MISSING_PERMISSIONS,
            message="Insufficient permissions.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_PERMISSIONS,
                    messages=[
                        "Users cannot change a Boot Asset Item's bytes_synced field."
                    ],
                    field="Authorization",
                    location="header",
                )
            ],
        )
    boot_asset_item = await services.boot_asset_items.get_by_id(id)
    if not boot_asset_item:
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Boot Asset Item does not exist.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[f"BootAssetItem ID {id} does not exist"],
                    field="boot_asset_item_id",
                    location="path",
                )
            ],
        )
    updated_item = await services.boot_asset_items.update(
        id, models.BootAssetItemUpdate(**patch_request.model_dump())
    )
    await services.index_service.refresh()
    return dm.BootAssetItemPatchResponse.from_model(updated_item)
