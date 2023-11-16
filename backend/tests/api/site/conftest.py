from typing import (
    AsyncIterator,
    Iterator,
)
import uuid

import pytest

from msm.db.models import Site

from ...fixtures.factory import Factory


@pytest.fixture
def api_site_auth_id() -> Iterator[uuid.UUID]:
    yield uuid.uuid4()


@pytest.fixture
async def api_site(
    factory: Factory, api_site_auth_id: uuid.UUID
) -> AsyncIterator[Site]:
    """An site that accesses the API."""
    yield await factory.make_Site(auth_id=api_site_auth_id)
