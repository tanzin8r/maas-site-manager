from uuid import UUID

from fastapi import Depends

from ...db.models import Site
from ...service import ServiceCollection
from .._auth import (
    auth_id_from_token,
    bearer_token,
)
from .._dependencies import services
from .._utils import INVALID_TOKEN_ERROR


async def authenticated_site(
    services: ServiceCollection = Depends(services),
    auth_id: UUID = Depends(auth_id_from_token(bearer_token)),
) -> Site:
    if site := await services.sites.get_by_auth_id(auth_id):
        return site
    raise INVALID_TOKEN_ERROR
