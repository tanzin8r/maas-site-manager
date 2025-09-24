from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from msm.apiserver.db import CUSTOM_IMAGE_SOURCE_ID, models
from msm.apiserver.dependencies import services
from msm.apiserver.exceptions.catalog import (
    BaseExceptionDetail,
    NotFoundException,
)
from msm.apiserver.exceptions.constants import ExceptionCode
from msm.apiserver.exceptions.responses import (
    NotFoundErrorResponseModel,
    UnauthorizedErrorResponseModel,
    ValidationErrorResponseModel,
)
from msm.apiserver.schema import (
    SortParam,
)
from msm.apiserver.service import ServiceCollection
from msm.apiserver.user.auth import (
    authenticated_user,
)
import msm.common.api.selections as dm

v1_router = APIRouter(prefix="/v1")


@v1_router.post(
    "/selectable-images:select",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
    status_code=201,
)
async def select_images(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    post_request: dm.SelectImagesPostRequest,
) -> None:
    count, selections = await services.boot_source_selections.get_many_by_id(
        post_request.selection_ids
    )
    if count != len(post_request.selection_ids):
        missing_ids = set(post_request.selection_ids) - set(
            [s.id for s in selections]
        )
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Some selections were not found.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[
                        f"Boot Source Selections with IDs {list(missing_ids)} could not be found"
                    ],
                    field="selection_ids",
                    location="body",
                )
            ],
        )
    await services.boot_source_selections.update_many(
        post_request.selection_ids, select=True
    )


@v1_router.get(
    "/selectable-images",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
    },
)
async def get_selectable_images(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
) -> dm.GetSelectableImagesResponse:
    selectable: dict[tuple[str, str, str], models.SelectableImage] = {}
    selected: set[tuple[str, str, str]] = set()
    images_found: set[tuple[str, str, str]] = set()
    _, sources = await services.boot_sources.get(
        [SortParam("priority", asc=False)]
    )
    for source in sources:
        _, selections = await services.boot_source_selections.get(
            [], boot_source_id=[source.id]
        )
        for selection in selections:
            key = (selection.os, selection.release, selection.arch)
            if not selection.selected:
                # ignore if os/release/arch already exists in a higher prio source
                if key not in images_found:
                    selectable[key] = models.SelectableImage(
                        selection_id=selection.id,
                        os=selection.os,
                        release=selection.release,
                        arch=selection.arch,
                        boot_source_id=source.id,
                        boot_source_name=source.name,
                        boot_source_url=source.url,
                    )
            # if something is not selected in a high prio source,
            # but is selected in a low prio source, we need to remove it later
            elif key in selectable:
                selected.add(key)
            images_found.add(key)
    for key in selected:
        selectable.pop(key, None)
    items = list(selectable.values())
    items.sort(key=lambda x: (x.os, x.release, x.arch))
    return dm.GetSelectableImagesResponse(items=items)


@v1_router.get(
    "/selected-images",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
    },
)
async def get_selected_images(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
) -> dm.GetSelectedImagesResponse:
    images_found: set[tuple[str, str, str]] = set()
    selected = []
    _, sources = await services.boot_sources.get(
        [SortParam("priority", asc=False)]
    )

    async def get_total_size_and_downloaded(asset_id: int) -> tuple[int, int]:
        if latest_ver := await services.boot_asset_versions.get_latest_version(
            asset_id
        ):
            _, items = await services.boot_asset_items.get(
                [], boot_asset_version_id=[latest_ver.id]
            )
            total_size = 0
            total_downloaded = 0
            for item in items:
                total_size += item.file_size
                total_downloaded += item.bytes_synced
            return total_size, total_downloaded
        return 0, 0

    for source in sources:
        _, selections = await services.boot_source_selections.get(
            [],
            boot_source_id=[source.id],
        )
        for selection in selections:
            if (
                selection.os,
                selection.release,
                selection.arch,
            ) not in images_found and selection.selected:
                images_found.add(
                    (selection.os, selection.release, selection.arch)
                )
                _, assets = await services.boot_assets.get(
                    [],
                    boot_source_id=[source.id],
                    os=[selection.os],
                    arch=[selection.arch],
                    release=[selection.release],
                )
                asset = next(iter(assets))
                (
                    total_size,
                    total_downloaded,
                ) = await get_total_size_and_downloaded(asset.id)
                selected.append(
                    models.SelectedImage(
                        os=selection.os,
                        release=selection.release,
                        arch=selection.arch,
                        boot_source_id=source.id,
                        boot_source_name=source.name,
                        boot_source_url=source.url,
                        size=total_size,
                        downloaded=total_downloaded,
                        custom_image_id=None,
                        selection_id=selection.id,
                    )
                )
    # Selections don't exist for custom images, add them manually
    custom_source = await services.boot_sources.get_by_id(
        CUSTOM_IMAGE_SOURCE_ID
    )
    assert custom_source is not None
    _, assets = await services.boot_assets.get(
        [], boot_source_id=[custom_source.id]
    )
    for asset in assets:
        total_size, total_downloaded = await get_total_size_and_downloaded(
            asset.id
        )
        selected.append(
            models.SelectedImage(
                os=asset.os,
                release=asset.release,
                arch=asset.arch,
                boot_source_id=custom_source.id,
                boot_source_name=custom_source.name,
                boot_source_url=custom_source.url,
                size=total_size,
                downloaded=total_downloaded,
                custom_image_id=asset.id,
            )
        )
    selected.sort(key=lambda x: (x.os, x.release, x.arch))
    return dm.GetSelectedImagesResponse(items=selected)


@v1_router.post(
    "/selected-images:remove",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
    status_code=204,
)
async def remove_selections(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    background_tasks: BackgroundTasks,
    post_request: dm.RemoveSelectedImagesPostRequest,
) -> None:
    count, selections = await services.boot_source_selections.get_many_by_id(
        post_request.selection_ids
    )
    if count != len(post_request.selection_ids):
        missing_ids = set(post_request.selection_ids) - set(
            [s.id for s in selections]
        )
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Some selections were not found.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=[
                        f"Boot Source Selections with IDs {list(missing_ids)} could not be found"
                    ],
                    field="selection_ids",
                    location="body",
                )
            ],
        )
    await services.boot_source_selections.update_many(
        post_request.selection_ids, False
    )

    asset_ids = []
    for selection in selections:
        _, assets = await services.boot_assets.get(
            [],
            boot_source_id=[selection.boot_source_id],
            label=[selection.label],
            os=[selection.os],
            release=[selection.release],
            arch=[selection.arch],
        )
        asset_ids += [a.id for a in assets]

    background_tasks.add_task(
        services.boot_assets.purge_assets,
        asset_ids,
    )


@v1_router.get(
    "/image-sources",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get_image_sources(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    os: str,
    release: str,
    arch: str,
) -> dm.GetImageSourcesResponse:
    available_sources = []
    _, sources = await services.boot_sources.get([])
    for source in sources:
        count, selections = await services.boot_source_selections.get(
            [],
            boot_source_id=[source.id],
            os=[os],
            release=[release],
            arch=[arch],
        )
        if count:
            selection = next(iter(selections))
            available_sources.append(
                dm.ImageSource(
                    selection_id=selection.id,
                    id=source.id,
                    name=source.name,
                    url=source.url,
                )
            )
    return dm.GetImageSourcesResponse(items=available_sources)
