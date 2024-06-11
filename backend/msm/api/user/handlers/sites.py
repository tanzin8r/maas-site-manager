from collections.abc import Iterable
from typing import (
    Annotated,
    cast,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from pydantic import (
    BaseModel,
    Field,
)

from msm.api._dependencies import services
from msm.api._utils import (
    not_found,
    raise_on_empty_request,
)
from msm.api.user._auth import authenticated_user
from msm.api.user._forms import (
    SiteFilterParams,
    site_filter_parameters,
)
from msm.db import models
from msm.schema import (
    PaginatedResults,
    PaginationParams,
    SortParam,
    SortParamParser,
    TimeZone,
)
from msm.service import (
    InvalidPendingSites,
    ServiceCollection,
)

v1_router = APIRouter(prefix="/v1")

site_sort_parameters = SortParamParser(
    fields=[
        "name",
        "name_unique",
        "country",
        "city",
        "state",
        "address",
        "postal_code",
        "timezone",
        "connection_status",
    ]
)


class PendingSitesGetResponse(PaginatedResults):
    items: list[models.PendingSite]


@v1_router.get("/sites/pending")
async def get_pending(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    pagination_params: Annotated[PaginationParams, Depends()],
) -> PendingSitesGetResponse:
    """Return pending sites."""
    total, results = await services.sites.get_pending(
        offset=pagination_params.offset,
        limit=pagination_params.size,
    )
    return PendingSitesGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


class PendingSitesPostRequest(BaseModel):
    """Request to accept/reject sites."""

    ids: list[int]
    accept: bool


@v1_router.post("/sites/pending", status_code=204)
async def post_pending(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    action: PendingSitesPostRequest,
) -> None:
    """Accept or reject pending sites."""
    try:
        await services.sites.accept_reject_pending(
            action.ids,
            action.accept,
        )
    except InvalidPendingSites as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(error), "ids": error.ids},
        )

    return None


class SitesGetResponse(PaginatedResults):
    """Response with paginated accepted sites."""

    items: list[models.Site]


@v1_router.get("/sites")
async def get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    pagination_params: Annotated[PaginationParams, Depends()],
    filter_params: Annotated[
        SiteFilterParams, Depends(site_filter_parameters)
    ],
    sort_params: Annotated[list[SortParam], Depends(site_sort_parameters)],
    missing_coordinates: bool = Query(  # don't add to SiteFilterParams, since it's also used for /get/coordinates
        default=False, title="Filter for sites that do not have coordinates"
    ),
) -> SitesGetResponse:
    """Return accepted sites."""
    total, results = await services.sites.get(
        sort_params=sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
        **filter_params._asdict(),
        missing_coordinates=missing_coordinates,
    )
    return SitesGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


@v1_router.get("/sites/coordinates")
async def get_coordinates(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    filter_params: Annotated[
        SiteFilterParams, Depends(site_filter_parameters)
    ],
) -> Iterable[models.SiteCoordinates]:
    """Return coordinates for all accepted sites."""
    return await services.sites.get_coordinates(**filter_params._asdict())


@v1_router.get("/sites/{id}")
async def get_id(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    id: int,
) -> models.Site:
    """Return a specific site."""
    if site := await services.sites.get_by_id(id):
        return site
    raise not_found("Site")


class SiteUpdateRequest(BaseModel):
    """Update a site."""

    city: str | None = None
    country: str | None = Field(default=None, min_length=2, max_length=2)
    coordinates: list[
        float
    ] | None = None  # first item is the lon, second is the lat
    note: str | None = None
    state: str | None = None
    address: str | None = None
    postal_code: str | None = None
    # XXX: mypy can't grok that this is an str/enum with lots of members
    timezone: TimeZone | None = None  # type: ignore[valid-type]


@v1_router.patch("/sites/{id}")
async def patch(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    id: int,
    patch_request: SiteUpdateRequest,
) -> models.Site:
    """Modify a site."""
    if not await services.sites.id_exists(id):
        raise not_found("Site")

    raise_on_empty_request(patch_request)
    data = patch_request.model_dump(exclude_none=True)
    await services.sites.update(id, models.SiteUpdate(**data))
    return cast(models.Site, await services.sites.get_by_id(id))


@v1_router.delete("/sites/{id}", status_code=204)
async def delete(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.Site, Depends(authenticated_user)],
    id: int,
) -> None:
    """Delete a site from the database."""
    await services.sites.delete(id)
    return None


@v1_router.delete("/sites", status_code=204)
async def delete_many(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.Site, Depends(authenticated_user)],
    ids: Annotated[list[int], Query()] = [],
) -> None:
    """Delete multiple sites from the database."""
    # unfortunately, we can't use fastapi to validate that at least one id was
    # pased, so we need to do it manually
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "No ID's provided"},
        )
    requested_ids = set(ids)
    deleted_ids = await services.sites.delete_many(ids)
    if deleted_ids != requested_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": (
                    f"The following ID's were not found: {requested_ids - deleted_ids}."
                    + (
                        f" The following ID's were deleted: {deleted_ids}"
                        if deleted_ids
                        else ""
                    )
                )
            },
        )
    return None
