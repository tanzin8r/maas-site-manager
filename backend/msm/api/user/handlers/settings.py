from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from msm.api.dependencies import services
from msm.api.exceptions.responses import (
    ForbiddenErrorResponseModel,
    UnauthorizedErrorResponseModel,
    ValidationErrorResponseModel,
)
from msm.api.user.auth import authenticated_admin
from msm.db.models import (
    Settings,
    User,
)
from msm.db.models.settings import SettingsUpdate
from msm.service import ServiceCollection

v1_router = APIRouter(prefix="/v1")


@v1_router.get(
    "/settings",
    responses={
        403: {"model": ForbiddenErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
    },
)
async def get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[User, Depends(authenticated_admin)],
) -> Settings:
    """Return service settings."""
    return await services.settings.get()


@v1_router.patch(
    "/settings",
    responses={
        403: {"model": ForbiddenErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def patch(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[User, Depends(authenticated_admin)],
    request: SettingsUpdate,
) -> None:
    await services.settings.update(request.model_dump(exclude_none=True))
