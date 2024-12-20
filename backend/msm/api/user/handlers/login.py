from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm

from msm.api.auth import (
    AccessTokenResponse,
    token_response,
)
from msm.api.dependencies import (
    config,
    services,
)
from msm.api.exceptions.catalog import UnauthorizedException
from msm.api.exceptions.constants import ExceptionCode
from msm.api.exceptions.responses import (
    UnauthorizedErrorResponseModel,
    ValidationErrorResponseModel,
)
from msm.api.user.auth import authenticate_user
from msm.db.models import Config
from msm.jwt import TokenAudience
from msm.service import ServiceCollection

v1_router = APIRouter(prefix="/v1")


@v1_router.post(
    "/login",
    responses={
        422: {"model": ValidationErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
    },
)
async def post(
    config: Annotated[Config, Depends(config)],
    services: Annotated[ServiceCollection, Depends(services)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> AccessTokenResponse:
    user = await authenticate_user(
        services.users, form_data.username, form_data.password
    )
    if not user:
        # do not specify details here, as to not clue which parameter is wrong in case of an attack
        raise UnauthorizedException(
            code=ExceptionCode.INVALID_CREDENTIALS,
            message="Wrong username or password.",
        )
    return token_response(config, user.auth_id, TokenAudience.API)
