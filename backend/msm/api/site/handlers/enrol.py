from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from pydantic import BaseModel, Field

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
from msm.api.site._auth import authenticated_site
from msm.db.models import (
    Config,
    PendingSiteCreate,
    Site,
)
from msm.jwt import (
    TokenAudience,
    TokenPurpose,
)
from msm.schema import TimeZone
from msm.service import ServiceCollection

v1_router = APIRouter(prefix="/v1")


class SiteMetadata(BaseModel):
    """Metadata given by a site when enroling"""

    city: str | None = None
    country: str | None = Field(default=None, min_length=2, max_length=2)
    latitude: float | None = None
    longitude: float | None = None
    note: str | None = None
    state: str | None = None
    address: str | None = None
    postal_code: str | None = None
    # XXX: mypy can't grok that this is an str/enum with lots of members
    timezone: TimeZone | None = None  # type: ignore[valid-type]


class EnrolPostRequest(BaseModel):
    """Request to enrol a site."""

    name: str
    url: str
    cluster_uuid: str
    metadata: SiteMetadata | None = None


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
    metadata = (
        post_request.metadata.model_dump(
            exclude=(set(["longitude", "latitude"]))
        )
        if post_request.metadata is not None
        else {}
    )
    if post_request.metadata is not None:
        metadata["coordinates"] = (
            (
                post_request.metadata.latitude,
                post_request.metadata.longitude,
            )
            if (
                post_request.metadata.latitude is not None
                and post_request.metadata.longitude is not None
            )
            else None
        )
    await services.sites.create_or_update_pending(
        PendingSiteCreate(
            name=post_request.name,
            url=post_request.url,
            cluster_uuid=post_request.cluster_uuid,
            auth_id=auth_id,
            **metadata,
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
    settings = await services.settings.get()
    return token_response(
        config,
        auth_id,
        TokenAudience.SITE,
        purpose=TokenPurpose.ACCESS,
        duration=timedelta(minutes=settings.token_lifetime_minutes),
        rotation_interval_minutes=settings.token_rotation_interval_minutes,
    )


@v1_router.get("/enrol/refresh")
async def refresh(
    config: Annotated[Config, Depends(config)],
    services: Annotated[ServiceCollection, Depends(services)],
    site: Annotated[Site, Depends(authenticated_site)],
    auth_id: Annotated[
        UUID,
        Depends(
            auth_id_from_token(
                bearer_token,
                TokenAudience.SITE,
                token_purpose=TokenPurpose.ACCESS,
            )
        ),
    ],
) -> AccessTokenResponse | None:
    """Return a new token for site heartbeats"""
    settings = await services.settings.get()
    return token_response(
        config,
        auth_id,
        TokenAudience.SITE,
        purpose=TokenPurpose.ACCESS,
        duration=timedelta(minutes=settings.token_lifetime_minutes),
        rotation_interval_minutes=settings.token_rotation_interval_minutes,
    )
