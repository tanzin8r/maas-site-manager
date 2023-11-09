from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel

from ....db.models import Config
from ....service import ServiceCollection
from ..._auth import (
    AccessTokenResponse,
    token_response,
)
from ..._dependencies import (
    config,
    services,
)
from .._auth import authenticate_user

v1_router = APIRouter(prefix="/v1")


class LoginPostRequest(BaseModel):
    """User login request schema."""

    email: str
    password: str


@v1_router.post("/login")
async def post(
    config: Annotated[Config, Depends(config)],
    services: Annotated[ServiceCollection, Depends(services)],
    user_login: LoginPostRequest,
) -> AccessTokenResponse:
    user = await authenticate_user(
        services.users, user_login.email, user_login.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_response(config, user.auth_id)
