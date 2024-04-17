from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import (
    EnrolingSite,
    PendingSiteCreate,
    Site,
    SiteCoordinates,
    SiteDetailsUpdate,
    SiteUpdate,
)
from msm.service._site import SiteService
from tests.fixtures.factory import Factory


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

    async def test_get_by_auth_id(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        auth_id = uuid4()
        site = await factory.make_Site(auth_id=auth_id)
        details = site.model_dump() | {"connection_status": "unknown"}
        service = SiteService(db_connection)
        assert await service.get_by_auth_id(auth_id) == Site(**details)
        assert await service.get_by_auth_id(uuid4()) is None

    async def test_get_coordinates(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        site1 = await factory.make_Site(coordinates=(10, -1))
        site2 = await factory.make_Site(coordinates=(20, -2))
        # pending site is not included
        await factory.make_PendingSite()
        service = SiteService(db_connection)
        assert list(await service.get_coordinates()) == [
            SiteCoordinates(id=site1.id, coordinates=[10, -1]),
            SiteCoordinates(id=site2.id, coordinates=[20, -2]),
        ]

    async def test_get_coordinates_filter(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        await factory.make_Site(coordinates=(10, -1), city="Los Angeles")
        site2 = await factory.make_Site(coordinates=(20, -2), city="Atlantis")
        service = SiteService(db_connection)
        assert list(await service.get_coordinates(city=["Atlantis"])) == [
            SiteCoordinates(id=site2.id, coordinates=[20, -2]),
        ]

    async def test_create_pending(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        service = SiteService(db_connection)
        pending_site = await service.create_pending(
            PendingSiteCreate(
                name="site",
                url="https://site.example.com",
                auth_id=uuid4(),
            )
        )
        assert pending_site.name == "site"
        assert pending_site.url == "https://site.example.com"

    async def test_get_enroling_accepted(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        auth_id = uuid4()
        site = await factory.make_Site(auth_id=auth_id)

        service = SiteService(db_connection)
        enroling_site = cast(EnrolingSite, await service.get_enroling(auth_id))
        assert enroling_site.id == site.id
        assert enroling_site.accepted

    async def test_get_enroling_pending(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        auth_id = uuid4()
        pending_site = await factory.make_PendingSite(auth_id=auth_id)

        service = SiteService(db_connection)
        enroling_site = cast(EnrolingSite, await service.get_enroling(auth_id))
        assert enroling_site.id == pending_site.id
        assert not enroling_site.accepted

    async def test_get_enroling_not_found(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        service = SiteService(db_connection)
        assert await service.get_enroling(uuid4()) is None

    async def test_update_details(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        service = SiteService(db_connection)
        site = await factory.make_Site()
        await service.update(
            site.id,
            SiteDetailsUpdate(
                name="new-name", url="https://new-site.example.com"
            ),
        )
        [db_site] = await factory.get("site")
        assert db_site["name"] == "new-name"
        assert db_site["url"] == "https://new-site.example.com"

    async def test_update(
        self,
        factory: Factory,
        db_connection: AsyncConnection,
    ) -> None:
        service = SiteService(db_connection)
        site = await factory.make_Site()
        await service.update(
            site.id, SiteUpdate(city="New York", country="US")
        )
        [db_site] = await factory.get("site")
        assert db_site["city"] == "New York"
        assert db_site["country"] == "US"
