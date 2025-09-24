from typing import Annotated
from uuid import UUID

from fastapi import Depends

from msm.apiserver.auth import (
    auth_id_from_token,
    bearer_token,
)
from msm.apiserver.db.models import Site
from msm.apiserver.dependencies import services
from msm.apiserver.exceptions.catalog import (
    BaseExceptionDetail,
    UnauthorizedException,
)
from msm.apiserver.exceptions.constants import ExceptionCode
from msm.apiserver.service import ServiceCollection
from msm.common.jwt import (
    TokenAudience,
    TokenPurpose,
)
from msm.common.time import now_utc


async def authenticated_site(
    services: Annotated[ServiceCollection, Depends(services)],
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
) -> Site:
    """Dependency to return the authenticated site.

    This also updates the `last_seen` timestamp for the site.
    """
    site = await services.sites.get_by_auth_id(auth_id)
    if not site:
        raise UnauthorizedException(
            code=ExceptionCode.INVALID_TOKEN,
            message="The token is not valid.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.INVALID_TOKEN,
                    messages=[
                        "The provided token does not correspond with a site."
                    ],
                    field="Authorization",
                    location="header",
                )
            ],
        )

    await services.sites.update_last_seen(site.id, now_utc())
    return site
