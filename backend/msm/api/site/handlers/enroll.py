from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from pydantic import BaseModel

from ....db.models import (
    Config,
    PendingSiteCreate,
)
from ....service import ServiceCollection
from ..._auth import (
    AccessTokenResponse,
    auth_id_from_token,
    bearer_token,
    token_response,
)
from ..._dependencies import (
    config,
    services,
)
from ..._utils import INVALID_TOKEN_ERROR

v1_router = APIRouter(prefix="/v1")


class EnrollPostRequest(BaseModel):
    """Request to enroll a site."""

    name: str
    url: str


@v1_router.post("/enroll")
async def post(
    request: EnrollPostRequest,
    response: Response,
    services: ServiceCollection = Depends(services),
    auth_id: UUID = Depends(auth_id_from_token(bearer_token)),
) -> None:
    """Request to enroll a new site."""
    db_token = await services.tokens.get_by_auth_id(auth_id)
    if db_token is None or db_token.is_expired():
        raise INVALID_TOKEN_ERROR

    await services.sites.create_pending(
        PendingSiteCreate(name=request.name, url=request.url, auth_id=auth_id)
    )
    await services.tokens.delete(db_token.id)
    response.status_code = status.HTTP_202_ACCEPTED


@v1_router.get("/enroll")
async def get(
    response: Response,
    config: Config = Depends(config),
    services: ServiceCollection = Depends(services),
    auth_id: UUID = Depends(auth_id_from_token(bearer_token)),
) -> AccessTokenResponse | None:
    """Check the site enrollment status.

    If the site is pending, a `204 No Content` response is returned.

    If the site has been accepted, a new authentication token is returned to be
    used for turther interaction with the API.

    """
    site = await services.sites.get_enrolling(auth_id)
    if not site:
        raise INVALID_TOKEN_ERROR
    if not site.accepted:
        response.status_code = status.HTTP_204_NO_CONTENT
        return None
    return token_response(config, auth_id)
