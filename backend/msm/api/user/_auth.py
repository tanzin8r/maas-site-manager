from typing import Annotated
from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer

from ...db.models import (
    Config,
    User,
)
from ...jwt import (
    InvalidToken,
    JWT,
)
from ...service import (
    ServiceCollection,
    UserService,
)
from .._dependencies import (
    config,
    services,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")


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
    config: Annotated[Config, Depends(config)],
    services: Annotated[ServiceCollection, Depends(services)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_token = JWT.decode(token, key=config.token_secret_key)
        decoded_token.validate(config.service_identifier)
    except (InvalidToken, ValueError):
        raise auth_error
    auth_id = UUID(decoded_token.subject)
    if user := await services.users.get_by_auth_id(auth_id):
        return user
    raise auth_error


async def authenticated_admin(
    config: Annotated[Config, Depends(config)],
    services: Annotated[ServiceCollection, Depends(services)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    user = await authenticated_user(config, services, token)
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
