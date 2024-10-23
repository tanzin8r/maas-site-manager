from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from msm.api._auth import auth_id_from_token
from msm.api._dependencies import services
from msm.api.exceptions.catalog import (
    ForbiddenException,
    UnauthorizedException,
)
from msm.api.exceptions.constants import ExceptionCode
from msm.db.models import User
from msm.jwt import TokenAudience
from msm.service import (
    ServiceCollection,
    UserService,
)

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="v1/login")


async def authenticate_user(
    service: UserService,
    email: str,
    password: str,
) -> User | None:
    if user := await service.get_by_email(email):
        if await service.password_matches(user.id, password):
            return user
    return None


async def authenticated_user(
    services: Annotated[ServiceCollection, Depends(services)],
    auth_id: Annotated[
        UUID, Depends(auth_id_from_token(OAUTH2_SCHEME, TokenAudience.API))
    ],
) -> User:
    if user := await services.users.get_by_auth_id(auth_id):
        return user
    raise UnauthorizedException(
        code=ExceptionCode.INVALID_TOKEN,
        message="The token is not valid.",
    )


def authenticated_admin(
    user: Annotated[User, Depends(authenticated_user)],
) -> User:
    if not user.is_admin:
        raise ForbiddenException(
            code=ExceptionCode.MISSING_PERMISSIONS,
            message="Unauthorized credentials.",
        )
    return user
