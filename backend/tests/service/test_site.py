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
        site_details = {
            "name": "LondonHQ",
            "name_unique": True,
            "url": "https://londoncalling.example.com",
            "accepted": True,
        }
        [site] = await factory.create("site", [site_details])
        site |= {"connection_status": "unknown"}
        service = SiteService(db_connection)
        assert await service.get_by_id(id) == (
            Site(**site) if exists else None
        )
