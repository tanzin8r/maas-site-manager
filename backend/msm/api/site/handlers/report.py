from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
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


@v1_router.post("/details")
async def details(
    services: Annotated[ServiceCollection, Depends(services)],
    site: Annotated[Site, Depends(authenticated_site)],
    post_request: DetailsPostRequest,
) -> None:
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
