from uuid import UUID

from pydantic import BaseModel

from ..db.models import Config
from ..jwt import JWT


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
