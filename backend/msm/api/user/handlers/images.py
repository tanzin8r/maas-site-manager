from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from msm.api.dependencies import services
from msm.api.exceptions.responses import (
    UnauthorizedErrorResponseModel,
    ValidationErrorResponseModel,
)
from msm.api.user.auth import authenticated_user
from msm.db import models
from msm.schema import (
    PaginatedResults,
    PaginationParams,
    SortParam,
    SortParamParser,
)
from msm.service import ServiceCollection

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
        "eol",
        "esm_eol",
    ]
)


class BootAssetsGetResponse(PaginatedResults):
    items: list[models.BootAsset]


boot_sources_sort_parameters = SortParamParser(
    fields=[
        "url",
        "keyring",
        "sync_interval",
        "priority",
    ]
)


class BootSourcesGetResponse(PaginatedResults):
    items: list[models.BootSource]


boot_source_selection_sort_parameters = SortParamParser(
    fields=[
        "label",
        "os",
        "release",
        "arches",
    ]
)


class BootSourceSelectionsGetResponse(PaginatedResults):
    items: list[models.BootSourceSelection]


@v1_router.get(
    "/bootassets",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get_boot_assets(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    sort_params: Annotated[
        list[SortParam], Depends(boot_asset_sort_parameters)
    ],
    pagination_params: Annotated[PaginationParams, Depends()],
) -> BootAssetsGetResponse:
    """Return boot assets."""
    total, results = await services.boot_assets.get(
        sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
    )
    return BootAssetsGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
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
) -> BootSourcesGetResponse:
    """Return boot sources."""
    total, results = await services.boot_sources.get(
        sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
    )
    return BootSourcesGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


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
) -> BootSourceSelectionsGetResponse:
    """Return boot source selections."""
    total, results = await services.boot_source_selections.get(
        id,
        sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
    )
    return BootSourceSelectionsGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )
