from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm

from msm.apiserver.auth import (
    AccessTokenResponse,
    token_response,
)
from msm.apiserver.db.models import Config
from msm.apiserver.dependencies import (
    config,
    services,
)
from msm.apiserver.exceptions.catalog import UnauthorizedException
from msm.apiserver.exceptions.constants import ExceptionCode
from msm.apiserver.exceptions.responses import (
    UnauthorizedErrorResponseModel,
    ValidationErrorResponseModel,
)
from msm.apiserver.service import ServiceCollection
from msm.apiserver.user.auth import authenticate_user
from msm.common.jwt import TokenAudience

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
