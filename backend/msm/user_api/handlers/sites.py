from typing import (
    Annotated,
    Iterable,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel

from ...db.models import (
    PendingSite,
    Site,
    SiteCoordinates,
    User,
)
from ...schema import (
    PaginatedResults,
    pagination_params,
    PaginationParams,
    SortParam,
    SortParamParser,
)
from ...service import (
    InvalidPendingSites,
    ServiceCollection,
)
from .._auth import authenticated_user
from .._dependencies import services
from .._forms import (
    site_filter_parameters,
    SiteFilterParams,
)

v1_router = APIRouter(prefix="/v1")

site_sort_parameters = SortParamParser(
    fields=[
        "name",
        "name_unique",
        "country",
        "city",
        "region",
        "street",
        "timezone",
        "connection_status",
    ]
)


class SitesGetResponse(PaginatedResults):
    """Response with paginated accepted sites."""

    items: list[Site]


@v1_router.get("/sites")
async def get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    pagination_params: PaginationParams = Depends(pagination_params),
    filter_params: SiteFilterParams = Depends(site_filter_parameters),
    sort_params: list[SortParam] = Depends(site_sort_parameters),
) -> SitesGetResponse:
    """Return accepted sites."""
    total, results = await services.sites.get(
        sort_params=sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
        **filter_params._asdict(),
    )
    return SitesGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=results,
    )


@v1_router.get("/sites/coordinates")
async def get_coordinates(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
) -> Iterable[SiteCoordinates]:
    """Return coordinates for all accepted sites."""
    return await services.sites.get_coordinates()


@v1_router.get("/sites/{id}")
async def get_id(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    id: int,
) -> Site:
    """Return a specific site."""
    if site := await services.sites.get_by_id(id):
        return site
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": "Site does not exist."},
    )


class PendingSitesGetResponse(PaginatedResults):
    items: list[PendingSite]


@v1_router.get("/requests")
async def get_requests(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    pagination_params: PaginationParams = Depends(pagination_params),
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
        items=results,
    )


class PendingSitesPostRequest(BaseModel):
    """Request to accept/reject sites."""

    ids: list[int]
    accept: bool


@v1_router.post("/requests", status_code=204)
async def post_requests(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
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


@v1_router.delete("/sites/{id}", status_code=204)
async def delete(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[Site, Depends(authenticated_user)],
    id: int,
) -> None:
    """Delete a site from the database."""
    await services.sites.delete(id)
    return None
