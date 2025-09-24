from collections.abc import AsyncIterator, Iterator
import uuid

from fastapi import FastAPI
import pytest

from msm.apiserver.db.models import (
    Config,
    Site,
)
from msm.common.jwt import (
    TokenAudience,
    TokenPurpose,
)
from tests.apiserver.conftest import make_api_client
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.fixture
def api_site_auth_id() -> Iterator[uuid.UUID]:
    yield uuid.uuid4()


@pytest.fixture
async def api_site(
    factory: Factory, api_site_auth_id: uuid.UUID
) -> AsyncIterator[Site]:
    """An site that accesses the API."""
    yield await factory.make_Site(auth_id=api_site_auth_id)


@pytest.fixture
async def site_client(
    api_app: FastAPI,
    api_config: Config,
    api_site_auth_id: uuid.UUID,
    api_site: Site,
) -> AsyncIterator[Client]:
    """Authenticated client for a site, under the /site/v1 prefix."""
    async with make_api_client(
        api_app, api_config, prefix="/site/v1"
    ) as client:
        client.authenticate(
            api_site_auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ACCESS,
        )
        yield client
