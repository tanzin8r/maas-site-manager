from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel

from ...jwt import create_token
from ...service import ServiceCollection
from .._auth import authenticate_user
from .._dependencies import services


class LoginPostRequest(BaseModel):
    """User login request schema."""

    email: str
    password: str


class LoginPostResponse(BaseModel):
    """User login response with JSON Web Token."""

    access_token: str
    token_type: str


async def post(
    services: Annotated[ServiceCollection, Depends(services)],
    user_login: LoginPostRequest,
) -> LoginPostResponse:
    user = await authenticate_user(
        services.users, user_login.email, user_login.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_token(user.email)
    return LoginPostResponse(access_token=access_token, token_type="bearer")
