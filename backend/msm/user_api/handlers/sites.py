from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import queries
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
from .._dependencies import db_session
from .._forms import (
    site_filter_parameters,
    SiteFilterParams,
)
from .._jwt import get_authenticated_user

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
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    pagination_params: PaginationParams = Depends(pagination_params),
    filter_params: SiteFilterParams = Depends(site_filter_parameters),
    sort_params: list[SortParam] = Depends(site_sort_parameters),
) -> SitesGetResponse:
    """Return accepted sites."""
    total, results = await queries.get_sites(
        session,
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


class PendingSitesGetResponse(PaginatedResults):
    items: list[PendingSite]


async def pending_get(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    pagination_params: PaginationParams = Depends(pagination_params),
) -> PendingSitesGetResponse:
    """Return pending sites."""
    total, results = await queries.get_pending_sites(
        session,
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
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    action: PendingSitesPostRequest,
) -> None:
    """Accept or reject pending sites."""
    try:
        await queries.accept_reject_pending_sites(
            session,
            action.ids,
            action.accept,
        )
    except queries.InvalidPendingSites as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(error), "ids": error.ids},
        )

    return None
