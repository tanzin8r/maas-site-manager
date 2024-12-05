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

from msm.api.auth import (
    AccessTokenResponse,
    auth_id_from_token,
    bearer_token,
    token_response_from_token,
)
from msm.api.dependencies import (
    config,
    services,
)
from msm.api.exceptions.catalog import (
    BaseExceptionDetail,
    UnauthorizedException,
)
from msm.api.exceptions.constants import ExceptionCode
from msm.api.exceptions.responses import (
    ErrorResponseModel,
)
from msm.api.site.auth import authenticated_site
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


@v1_router.post(
    "/enrol",
    responses={
        401: {"model": ErrorResponseModel},
        422: {"model": ErrorResponseModel},
    },
)
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
    if (
        db_token is None
        or db_token.is_expired()
        or db_token.site_id is not None
    ):
        raise UnauthorizedException(
            code=ExceptionCode.INVALID_TOKEN,
            message="The token is not valid.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.INVALID_TOKEN,
                    messages=[
                        "The token either does not exist, is expired, or is not correlated with a site."
                    ],
                    field="Authorization",
                    location="header",
                )
            ],
        )
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
    response.status_code = status.HTTP_202_ACCEPTED


@v1_router.get(
    "/enrol",
    responses={
        401: {"model": ErrorResponseModel},
    },
)
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
        raise UnauthorizedException(
            code=ExceptionCode.INVALID_TOKEN,
            message="The token is not valid.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.INVALID_TOKEN,
                    messages=[
                        "The token does not represent an enrolling site."
                    ],
                    field="Authorization",
                    location="header",
                )
            ],
        )
    if not site.accepted:
        response.status_code = status.HTTP_204_NO_CONTENT
        return None
    settings = await services.settings.get()
    [token] = await services.tokens.create(
        count=1,
        issuer=config.service_identifier,
        secret_key=config.token_secret_key,
        duration=timedelta(minutes=settings.token_lifetime_minutes),
        purpose=TokenPurpose.ACCESS,
        audience=TokenAudience.SITE,
        site_id=site.id,
    )
    return token_response_from_token(
        token,
        rotation_interval_minutes=settings.token_rotation_interval_minutes,
    )


@v1_router.get(
    "/enrol/refresh",
    responses={
        401: {"model": ErrorResponseModel},
    },
)
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
    [token] = await services.tokens.create(
        count=1,
        issuer=config.service_identifier,
        secret_key=config.token_secret_key,
        duration=timedelta(minutes=settings.token_lifetime_minutes),
        purpose=TokenPurpose.ACCESS,
        audience=TokenAudience.SITE,
        site_id=site.id,
    )
    return token_response_from_token(
        token,
        rotation_interval_minutes=settings.token_rotation_interval_minutes,
    )


@v1_router.get(
    "/enrol/verify",
    responses={
        401: {"model": ErrorResponseModel},
    },
)
async def verify(
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
) -> None:
    """Verify that the new token was successfully installed.

    All other existing Access tokens for this Site are revoked after this call."""
    await services.sites.remove_old_tokens(
        site_id=site.id, cur_auth_id=auth_id
    )
