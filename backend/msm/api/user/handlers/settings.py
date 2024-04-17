from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)
from pydantic import BaseModel

from msm.api._dependencies import services
from msm.api.user._auth import authenticated_admin
from msm.db.models import (
    Settings,
    User,
)
from msm.service import ServiceCollection

v1_router = APIRouter(prefix="/v1")


@v1_router.get("/settings")
async def get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[User, Depends(authenticated_admin)],
) -> Settings:
    """Return service settings."""
    return await services.settings.get()


class SettingsPatchRequest(BaseModel):
    """Change application settings."""

    service_url: str | None = None
    enrolment_url: str | None = None


@v1_router.patch("/settings")
async def patch(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[User, Depends(authenticated_admin)],
    request: SettingsPatchRequest,
) -> None:
    await services.settings.update(request.model_dump(exclude_none=True))
