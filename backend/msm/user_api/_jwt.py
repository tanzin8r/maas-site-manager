from datetime import (
    datetime,
    timedelta,
)
from typing import (
    Annotated,
    Any,
)

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer
from jose import (
    jwt,
    JWTError,
)
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import db_session
from ..db.models import UserWithPassword
from ..db.queries import get_user
from ..settings import SETTINGS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    """
    Verify a plain password against a password hash created by passlib
    """
    return bool(pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    """
    Get a hash for a password
    """
    return str(pwd_context.hash(password))


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if not expires_delta:
        expires_delta = timedelta(minutes=15)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, SETTINGS.secret_key, algorithm=SETTINGS.algorithm
    )
    return str(encoded_jwt)


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> UserWithPassword | None:
    if user := await get_user(session, email):
        if verify_password(password, user.password.get_secret_value()):
            return user
    return None


async def get_authenticated_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(db_session),
) -> UserWithPassword | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, SETTINGS.secret_key, algorithms=[SETTINGS.algorithm]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(session, email=email)
    if user is None:
        raise credentials_exception
    return user
