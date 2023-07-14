from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from ..db.models import UserWithPassword
from ..jwt import (
    InvalidToken,
    validate_token,
)
from ..service import (
    ServiceCollection,
    UserService,
)
from ._dependencies import services

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str) -> str:
    """
    Get a hash for a password
    """
    return str(pwd_context.hash(password))


async def authenticate_user(
    service: UserService,
    email: str,
    password: str,
) -> UserWithPassword | None:
    if user := await service.get_by_email(email):
        if _verify_password(password, user.password.get_secret_value()):
            return user
    return None


async def get_authenticated_user(
    services: Annotated[ServiceCollection, Depends(services)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserWithPassword | None:
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = validate_token(token)
        if user := await services.users.get_by_id(int(user_id)):
            return user
    except (InvalidToken, ValueError):
        raise auth_error
    raise auth_error


async def get_authenticated_admin(
    services: Annotated[ServiceCollection, Depends(services)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserWithPassword | None:
    if user := await get_authenticated_user(services, token):
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return user


def _verify_password(plain_password: str, hashed_password: str | None) -> bool:
    """Verify a plain password against a password hash created by passlib."""
    return pwd_context.verify(plain_password, hashed_password)
