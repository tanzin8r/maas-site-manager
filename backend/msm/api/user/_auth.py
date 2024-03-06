from typing import Annotated
from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer

from msm.api._auth import auth_id_from_token
from msm.api._dependencies import services
from msm.api._utils import INVALID_TOKEN_ERROR
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
    raise INVALID_TOKEN_ERROR


def authenticated_admin(
    user: Annotated[User, Depends(authenticated_user)],
) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
