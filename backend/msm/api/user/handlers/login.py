from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

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


@v1_router.post("/login")
async def post(
    config: Annotated[Config, Depends(config)],
    services: Annotated[ServiceCollection, Depends(services)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> AccessTokenResponse:
    user = await authenticate_user(
        services.users, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_response(config, user.auth_id)
