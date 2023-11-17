from typing import (
    Awaitable,
    Callable,
)
from uuid import UUID

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel

from ..db.models import Config
from ..jwt import (
    InvalidToken,
    JWT,
)
from ._dependencies import config
from ._utils import INVALID_TOKEN_ERROR

# a dependency callable that returns the token
BearerToken = Callable[[Request], Awaitable[str | None]]


async def bearer_token(request: Request) -> str:
    """Returns the authentication token from the request header."""
    authorization = request.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


def auth_id_from_token(
    bearer_token: BearerToken,
) -> Callable[[Config, str], UUID]:
    """Return a dependency callable to get the auth ID from the token."""

    def auth_id_dep(
        config: Config = Depends(config),
        token: str = Depends(bearer_token),
    ) -> UUID:
        try:
            decoded_token = JWT.decode(
                token,
                key=config.token_secret_key,
                issuer=config.service_identifier,
            )
        except (ValueError, InvalidToken):
            raise INVALID_TOKEN_ERROR
        return UUID(decoded_token.subject)

    return auth_id_dep


class AccessTokenResponse(BaseModel):
    """Content for a response returning a JWT."""

    token_type: str
    access_token: str


def token_response(config: Config, auth_id: UUID) -> AccessTokenResponse:
    """Retrun an AccessTokenResponse, generating a token."""
    token = JWT.create(
        issuer=config.service_identifier,
        subject=str(auth_id),
        key=config.token_secret_key,
    )
    return AccessTokenResponse(token_type="Bearer", access_token=token.encoded)
