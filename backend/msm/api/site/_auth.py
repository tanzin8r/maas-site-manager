from typing import Annotated
from uuid import UUID

from fastapi import Depends

from ...db.models import Site
from ...jwt import (
    TokenAudience,
    TokenPurpose,
)
from ...service import ServiceCollection
from ...time import now_utc
from .._auth import (
    auth_id_from_token,
    bearer_token,
)
from .._dependencies import services
from .._utils import INVALID_TOKEN_ERROR


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
        raise INVALID_TOKEN_ERROR

    await services.sites.update_last_seen(site.id, now_utc())
    return site
