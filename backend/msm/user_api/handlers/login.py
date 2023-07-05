from datetime import timedelta
from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import db_session
from ...settings import SETTINGS
from .._jwt import (
    authenticate_user,
    create_access_token,
)


class LoginPostRequest(BaseModel):
    """User login request schema."""

    email: str
    password: str


class LoginPostResponse(BaseModel):
    """User login response with JSON Web Token."""

    access_token: str
    token_type: str


async def post(
    session: Annotated[AsyncSession, Depends(db_session)],
    user_login: LoginPostRequest,
) -> LoginPostResponse:
    user = await authenticate_user(
        session, user_login.email, user_login.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=SETTINGS.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return LoginPostResponse(access_token=access_token, token_type="bearer")
