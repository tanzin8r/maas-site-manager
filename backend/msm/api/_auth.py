from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import (
    Annotated,
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

from msm.api._dependencies import config
from msm.api._utils import INVALID_TOKEN_ERROR
from msm.db.models import Config
from msm.jwt import (
    DEFAULT_TOKEN_DURATION,
    JWT,
    InvalidToken,
    TokenAudience,
    TokenPurpose,
)

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
    token_audience: TokenAudience,
    token_purpose: TokenPurpose | None = None,
) -> Callable[[Config, str], UUID]:
    """Return a dependency callable to get the auth ID from the token."""

    def auth_id_dep(
        config: Annotated[Config, Depends(config)],
        token: Annotated[str, Depends(bearer_token)],
    ) -> UUID:
        try:
            decoded_token = JWT.decode(
                token,
                key=config.token_secret_key,
                issuer=config.service_identifier,
                audience=token_audience,
                purpose=token_purpose,
            )
        except (ValueError, InvalidToken):
            raise INVALID_TOKEN_ERROR
        return UUID(decoded_token.subject)

    return auth_id_dep


class AccessTokenResponse(BaseModel):
    """Content for a response returning a JWT."""

    token_type: str
    access_token: str
    rotation_interval_minutes: int


def token_response(
    config: Config,
    auth_id: UUID,
    audience: TokenAudience,
    purpose: TokenPurpose | None = None,
    duration: timedelta = DEFAULT_TOKEN_DURATION,
    rotation_interval_minutes: int = (
        int(DEFAULT_TOKEN_DURATION.total_seconds()) // 60
    )
    // 2,
) -> AccessTokenResponse:
    """Return an AccessTokenResponse, generating a token."""
    token = JWT.create(
        issuer=config.service_identifier,
        subject=str(auth_id),
        audience=audience,
        purpose=purpose,
        key=config.token_secret_key,
        duration=duration,
    )
    return AccessTokenResponse(
        token_type="Bearer",
        access_token=token.encoded,
        rotation_interval_minutes=rotation_interval_minutes,
    )
