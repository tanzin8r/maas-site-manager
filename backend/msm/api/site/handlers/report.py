from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    Response,
)
from pydantic import BaseModel

from msm.api._dependencies import services
from msm.api.site._auth import authenticated_site
from msm.db.models import (
    Site,
    SiteDataUpdate,
    SiteDetailsUpdate,
)
from msm.service import ServiceCollection
from msm.settings import Settings
from msm.time import now_utc

v1_router = APIRouter(prefix="/v1")


class MachineStatsByStatus(BaseModel):
    """Machine counts by status."""

    allocated: int
    deployed: int
    ready: int
    error: int
    other: int


class DetailsPostRequest(BaseModel):
    """Request to update site details."""

    name: str | None = None
    url: str | None = None
    machines_by_status: MachineStatsByStatus | None = None


class DetailsResponse(BaseModel):
    """Content for a response returning the heartbeat interval"""

    heartbeat_interval_seconds: int


def details_response(
    *args: Any, heartbeat_interval_seconds: int
) -> DetailsResponse:
    return DetailsResponse(
        heartbeat_interval_seconds=heartbeat_interval_seconds
    )


@v1_router.post("/details")
async def details(
    response: Response,
    services: Annotated[ServiceCollection, Depends(services)],
    site: Annotated[Site, Depends(authenticated_site)],
    post_request: DetailsPostRequest,
) -> DetailsResponse | None:
    """Update site details."""
    if post_request.name or post_request.url:
        await services.sites.update(
            site.id,
            SiteDetailsUpdate(name=post_request.name, url=post_request.url),
        )
    if post_request.machines_by_status:
        if site_data := post_request.machines_by_status.model_dump():
            await services.sites.update_data(
                site.id,
                SiteDataUpdate(
                    **{
                        f"machines_{key}": value
                        for key, value in site_data.items()
                    }
                ),
            )
    await services.sites.update_last_seen(site.id, now_utc())
    interval = await services.sites.get_heartbeat_interval()
    return details_response(heartbeat_interval_seconds=interval)
