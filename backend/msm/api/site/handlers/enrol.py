from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from pydantic import BaseModel

from msm.api._auth import (
    AccessTokenResponse,
    auth_id_from_token,
    bearer_token,
    token_response,
)
from msm.api._dependencies import (
    config,
    services,
)
from msm.api._utils import INVALID_TOKEN_ERROR
from msm.db.models import (
    Config,
    PendingSiteCreate,
)
from msm.jwt import (
    TokenAudience,
    TokenPurpose,
)
from msm.service import ServiceCollection

v1_router = APIRouter(prefix="/v1")


class EnrolPostRequest(BaseModel):
    """Request to enrol a site."""

    name: str
    url: str


@v1_router.post("/enrol")
async def post(
    response: Response,
    services: Annotated[ServiceCollection, Depends(services)],
    auth_id: Annotated[
        UUID,
        Depends(
            auth_id_from_token(
                bearer_token,
                TokenAudience.SITE,
                token_purpose=TokenPurpose.ENROLMENT,
            )
        ),
    ],
    post_request: EnrolPostRequest,
) -> None:
    """Request to enrol a new site."""
    db_token = await services.tokens.get_by_auth_id(auth_id)
    if db_token is None or db_token.is_expired():
        raise INVALID_TOKEN_ERROR

    await services.sites.create_pending(
        PendingSiteCreate(
            name=post_request.name, url=post_request.url, auth_id=auth_id
        )
    )
    await services.tokens.delete(db_token.id)
    response.status_code = status.HTTP_202_ACCEPTED


@v1_router.get("/enrol")
async def get(
    response: Response,
    config: Annotated[Config, Depends(config)],
    services: Annotated[ServiceCollection, Depends(services)],
    auth_id: Annotated[
        UUID,
        Depends(
            auth_id_from_token(
                bearer_token,
                TokenAudience.SITE,
                token_purpose=TokenPurpose.ENROLMENT,
            )
        ),
    ],
) -> AccessTokenResponse | None:
    """Check the site enrolment status.

    If the site is pending, a `204 No Content` response is returned.

    If the site has been accepted, a new authentication token is returned to be
    used for turther interaction with the API.

    """
    site = await services.sites.get_enroling(auth_id)
    if not site:
        raise INVALID_TOKEN_ERROR
    if not site.accepted:
        response.status_code = status.HTTP_204_NO_CONTENT
        return None
    return token_response(
        config, auth_id, TokenAudience.SITE, purpose=TokenPurpose.ACCESS
    )
