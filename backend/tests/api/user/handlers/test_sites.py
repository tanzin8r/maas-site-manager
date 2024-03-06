from datetime import timedelta
from typing import Any

import pytest

from msm.db.models import (
    ConnectionStatus,
    PendingSite,
    Site,
    SiteData,
)
from msm.service._site import LOST_CONNECTION_THRESHOLD
from msm.time import now_utc
from tests.api import api_timestamp
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


def site_details(site: Site, stats: SiteData | None = None) -> dict[str, Any]:
    data = site.model_dump()
    data["connection_status"] = data["connection_status"].value
    if stats is None:
        data["stats"] = None
    else:
        data["stats"] = stats.model_dump()
        data["stats"]["last_seen"] = api_timestamp(
            data["stats"]["last_seen"], astimezone=True
        )
    return data


def pending_site_details(site: PendingSite) -> dict[str, Any]:
    data = site.model_dump()
    data["created"] = api_timestamp(data["created"])
    return data


@pytest.mark.asyncio
class TestSitesGetHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        details = [
            site_details(
                await factory.make_Site(name="LondonHQ", city="London")
            ),
            site_details(
                await factory.make_Site(name="BerlinHQ", city="Berlin")
            ),
        ]
        page1 = await user_client.get("/sites")
        assert page1.status_code == 200
        assert page1.json() == {
            "page": 1,
            "size": 20,
            "total": 2,
            "items": details,
        }
        filtered = await user_client.get("/sites?city=onDo")  # vs London
        assert filtered.status_code == 200
        assert filtered.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": details[:1],
        }
        paginated = await user_client.get("/sites?page=2&size=1")
        assert paginated.status_code == 200
        assert paginated.json() == {
            "page": 2,
            "size": 1,
            "total": 2,
            "items": details[1:],
        }

    @pytest.mark.parametrize(
        "page,size", [(1, 0), (0, 1), (-1, -1), (1, 1001)]
    )
    async def test_get_422(
        self, user_client: Client, page: int, size: int, factory: Factory
    ) -> None:
        paginated = await user_client.get(f"/sites?page={page}&size={size}")
        assert paginated.status_code == 422

    async def test_only_accepted(
        self, user_client: Client, factory: Factory
    ) -> None:
        site = await factory.make_Site()
        await factory.make_PendingSite()

        page1 = await user_client.get("/sites")
        assert page1.status_code == 200
        assert page1.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [site_details(site)],
        }

    async def test_filter_timezone(
        self, user_client: Client, factory: Factory
    ) -> None:
        await factory.make_Site(timezone="Europe/Berlin")
        site = await factory.make_Site(timezone="Europe/London")

        page1 = await user_client.get("/sites?timezone=Europe/London")
        assert page1.status_code == 200
        assert page1.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [site_details(site)],
        }

    async def test_with_stats(
        self, user_client: Client, factory: Factory
    ) -> None:
        site = await factory.make_Site(
            connection_status=ConnectionStatus.STABLE
        )
        site_data = await factory.make_SiteData(
            site.id,
            machines_allocated=10,
            machines_deployed=20,
            machines_ready=30,
            machines_error=40,
            machines_other=5,
        )

        page = await user_client.get("/sites")
        assert page.status_code == 200
        assert page.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [site_details(site, stats=site_data)],
        }

    async def test_connection_status(
        self, user_client: Client, factory: Factory
    ) -> None:
        site = await factory.make_Site(
            connection_status=ConnectionStatus.STABLE
        )
        # Set last_seen to 1 second after the
        # lost_connection_threshold setting in order to test
        # that the connection is marked as lost
        await factory.make_SiteData(
            site.id,
            last_seen=(
                now_utc() - LOST_CONNECTION_THRESHOLD - timedelta(seconds=1)
            ),
        )

        page = await user_client.get("/sites")
        assert page.status_code == 200
        assert (
            page.json()["items"][0]["connection_status"]
            == ConnectionStatus.LOST
        )

    @pytest.mark.parametrize(
        "query_params, expected_result",
        [
            ("sort_by=city-asc", ["London", "Milan", "Paris", "Rome"]),
            (
                "sort_by=city,postal_code,name,name_unique,country,state,"
                "address,timezone,connection_status",
                ["London", "Milan", "Paris", "Rome"],
            ),
            ("sort_by=city-asc", ["London", "Milan", "Paris", "Rome"]),
            ("sort_by=city-desc", ["Rome", "Paris", "Milan", "London"]),
            (
                "sort_by=country,city-desc",
                ["Paris", "London", "Rome", "Milan"],
            ),
            ("sort_by=country,city-asc", ["Paris", "London", "Milan", "Rome"]),
            ("page=2&size=2&sort_by=country,city-asc", ["Milan", "Rome"]),
        ],
    )
    async def test_with_sorting(
        self,
        user_client: Client,
        factory: Factory,
        query_params: str,
        expected_result: list[str],
    ) -> None:
        await factory.make_Site(city="Milan", country="IT")
        await factory.make_Site(city="Paris", country="FR")
        await factory.make_Site(city="Rome", country="IT")
        await factory.make_Site(city="London", country="GB")

        response = await user_client.get("/sites", params=query_params)
        assert [
            site["city"] for site in response.json()["items"]
        ] == expected_result

    @pytest.mark.parametrize(
        "query_params",
        ["sort_by=id-asc", "sort_by=city,city", "sort_by=doesnotexist"],
    )
    async def test_with_invalid_sorting(
        self,
        user_client: Client,
        query_params: str,
    ) -> None:
        response = await user_client.get("/sites", params=query_params)
        assert response.status_code == 400


@pytest.mark.asyncio
class TestGetCoordinatesHandler:
    async def test_coordinates(
        self,
        user_client: Client,
        factory: Factory,
    ) -> None:
        site1 = await factory.make_Site(coordinates=(10, -1))
        site2 = await factory.make_Site(coordinates=(20, -2))
        response = await user_client.get("/sites/coordinates")
        assert response.status_code == 200
        assert response.json() == [
            {"id": site1.id, "coordinates": [10, -1]},
            {"id": site2.id, "coordinates": [20, -2]},
        ]


@pytest.mark.asyncio
class TestSitesGetByIDHandler:
    async def test_by_id(self, user_client: Client, factory: Factory) -> None:
        site = await factory.make_Site()

        site_id = -1
        response = await user_client.get(f"/sites/{site_id}")
        assert response.status_code == 404
        assert response.json()["detail"]["message"] == "Site does not exist."

        site_id = 2
        response = await user_client.get(f"/sites/{site.id}")
        assert response.status_code == 200
        assert response.json() == site_details(site)


@pytest.mark.asyncio
class TestSitesPatchHandler:
    async def test_patch(self, user_client: Client, factory: Factory) -> None:
        site = await factory.make_Site(coordinates=(0, 0))
        update: dict[str, Any] = {
            "country": "ES",
            "coordinates": [180, 90],
        }

        # update a site
        response = await user_client.patch(f"/sites/{site.id}", json=update)
        assert response.status_code == 200
        updated = Site(**site.model_dump()).model_dump() | update
        assert response.json() == updated

    async def test_nonexistent(
        self, user_client: Client, factory: Factory
    ) -> None:
        response = await user_client.patch("/sites/42", json={"country": "IT"})
        assert response.status_code == 404


@pytest.mark.asyncio
class TestSitesDeleteHandler:
    async def test_delete(self, user_client: Client, factory: Factory) -> None:
        site = await factory.make_Site()
        response = await user_client.delete(f"/sites/{site.id}")
        assert response.status_code == 204
        response = await user_client.get(f"/sites/{site.id}")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestPendingSitesGetHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        await factory.make_Site()
        site = await factory.make_PendingSite()

        response = await user_client.get("/sites/pending")
        assert response.status_code == 200
        assert response.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [pending_site_details(site)],
        }


@pytest.mark.asyncio
class TestPendingSitesPostHandler:
    async def test_accept(self, user_client: Client, factory: Factory) -> None:
        site = await factory.make_PendingSite()

        response = await user_client.post(
            "/sites/pending",
            json={"ids": [site.id], "accept": True},
        )
        assert response.status_code == 204
        [created_site] = await factory.get("site")
        assert created_site["accepted"]

    async def test_reject(self, user_client: Client, factory: Factory) -> None:
        site = await factory.make_PendingSite()

        response = await user_client.post(
            "/sites/pending",
            json={"ids": [site.id], "accept": False},
        )
        assert response.status_code == 204
        assert await factory.get("site") == []

    async def test_invalid_ids(
        self, user_client: Client, factory: Factory
    ) -> None:
        site = await factory.make_Site()

        # unknown IDs and IDs for non-pending sites are invalid
        ids = [site.id, 10000]
        response = await user_client.post(
            "/sites/pending",
            json={"ids": ids, "accept": True},
        )
        assert response.status_code == 400
        assert response.json() == {
            "detail": {"message": "Unknown pending sites", "ids": ids}
        }
