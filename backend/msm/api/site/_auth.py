from typing import Annotated
from uuid import UUID

from fastapi import Depends

from msm.api._auth import (
    auth_id_from_token,
    bearer_token,
)
from msm.api._dependencies import services
from msm.api.exceptions.catalog import UnauthorizedException
from msm.api.exceptions.constants import ExceptionCode
from msm.db.models import Site
from msm.jwt import (
    TokenAudience,
    TokenPurpose,
)
from msm.service import ServiceCollection
from msm.time import now_utc


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
        )

    await services.sites.update_last_seen(site.id, now_utc())
    return site
