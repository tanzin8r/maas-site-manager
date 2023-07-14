from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel

from ...db.models import (
    PendingSite,
    Site,
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
from .._auth import get_authenticated_user
from .._dependencies import services
from .._forms import (
    site_filter_parameters,
    SiteFilterParams,
)

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
    items: list[Site]


async def get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
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
        items=list(results),
    )


async def get_id(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    site_id: int,
) -> Site:
    """
    Select a specific site by id
    """
    if site := await services.sites.get_by_id(site_id):
        return site
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": "Site does not exist."},
    )


class PendingSitesGetResponse(PaginatedResults):
    items: list[PendingSite]


async def pending_get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
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
        items=list(results),
    )


class PendingSitesPostRequest(BaseModel):
    """Request to accept/reject sites."""

    ids: list[int]
    accept: bool


async def pending_post(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
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
