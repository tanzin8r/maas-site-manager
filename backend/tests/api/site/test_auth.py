import uuid

from fastapi import HTTPException
import pytest

from msm.api.site._auth import authenticated_site
from msm.db.models import Site
from msm.service import ServiceCollection


@pytest.mark.asyncio
class TestAuthenticatedSite:
    async def test_valid_token(
        self,
        api_services: ServiceCollection,
        api_site: Site,
        api_site_auth_id: uuid.UUID,
    ) -> None:
        site = await authenticated_site(api_services, api_site_auth_id)
        assert site == api_site

    async def test_invalid_auth_id(
        self, api_services: ServiceCollection
    ) -> None:
        with pytest.raises(HTTPException) as error:
            await authenticated_site(api_services, uuid.uuid4())
        assert error.value.status_code == 401
        assert error.value.headers == {"WWW-Authenticate": "Bearer"}
