import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import (
    Site,
    SiteCoordinates,
)
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
        details = site.model_dump() | {"connection_status": "unknown"}
        service = SiteService(db_connection)
        assert await service.get_by_id(id) == (
            Site(**details) if exists else None
        )

    async def test_get_coordinates(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        site1 = await factory.make_Site(latitude="10", longitude="-1")
        site2 = await factory.make_Site(latitude="20", longitude="-2")
        # pending site is not included
        await factory.make_PendingSite()
        service = SiteService(db_connection)
        assert list(await service.get_coordinates()) == [
            SiteCoordinates(id=site1.id, latitude="10", longitude="-1"),
            SiteCoordinates(id=site2.id, latitude="20", longitude="-2"),
        ]
