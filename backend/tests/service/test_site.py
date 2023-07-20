import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import Site
from msm.service._site import SiteService

from ..fixtures.factory import Factory


@pytest.mark.asyncio
class TestSiteService:
    @pytest.mark.parametrize(
        "id,exists",
        [
            (1, True),
            (-1, False),
        ],
    )
    async def test_get_by_id(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
        id: int,
        exists: bool,
    ) -> None:
        site = await factory.make_Site()
        details = site.dict() | {"connection_status": "unknown"}
        service = SiteService(db_connection)
        assert await service.get_by_id(id) == (
            Site(**details) if exists else None
        )
