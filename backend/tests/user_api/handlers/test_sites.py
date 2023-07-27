from datetime import (
    datetime,
    timedelta,
)
from typing import Any

import pytest

from msm.db.models import (
    ConnectionStatus,
    PendingSite,
    Site,
    SiteData,
)
from msm.service._site import LOST_CONNECTION_THRESHOLD_SECONDS

from ...fixtures.client import Client
from ...fixtures.factory import Factory


def site_details(site: Site, stats: SiteData | None = None) -> dict[str, Any]:
    data = site.model_dump()
    data["connection_status"] = data["connection_status"].value
    if stats is None:
        data["stats"] = None
    else:
        data["stats"] = stats.model_dump()
        data["stats"]["last_seen"] = data["stats"]["last_seen"].isoformat()
    return data


def pending_site_details(site: PendingSite) -> dict[str, Any]:
    data = site.model_dump()
    data["created"] = data["created"].isoformat()
    return data


@pytest.mark.asyncio
class TestSitesHandler:
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

    async def test_get_only_accepted(
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

    async def test_get_filter_timezone(
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

    async def test_get_with_stats(
        self, user_client: Client, factory: Factory
    ) -> None:
        site = await factory.make_Site(
            connection_status=ConnectionStatus.STABLE
        )
        site_data = await factory.make_SiteData(
            site.id,
            allocated_machines=10,
            deployed_machines=20,
            ready_machines=30,
            error_machines=40,
            other_machines=5,
            last_seen=datetime.utcnow(),
        )

        page = await user_client.get("/sites")
        assert page.status_code == 200
        assert page.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [site_details(site, stats=site_data)],
        }

    async def test_get_connection_status(
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
                datetime.utcnow()
                - timedelta(seconds=LOST_CONNECTION_THRESHOLD_SECONDS + 1)
            ),
        )

        page = await user_client.get("/sites")
        assert page.status_code == 200
        assert (
            page.json()["items"][0]["connection_status"]
            == ConnectionStatus.LOST
        )

    async def test_get_by_id(
        self, user_client: Client, factory: Factory
    ) -> None:
        site = await factory.make_Site()

        site_id = -1
        response = await user_client.get(f"/sites/{site_id}")
        assert response.status_code == 404
        assert response.json()["detail"]["message"] == "Site does not exist."

        site_id = 2
        response = await user_client.get(f"/sites/{site.id}")
        assert response.status_code == 200
        assert response.json() == site_details(site)

    @pytest.mark.parametrize(
        "query_params, expected_result",
        [
            ("sort_by=city-asc", ["London", "Milan", "Paris", "Rome"]),
            (
                "sort_by=city,name,name_unique,country,region,street,"
                "timezone,connection_status",
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
    async def test_get_with_sorting(
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
    async def test_get_with_invalid_sorting(
        self,
        user_client: Client,
        factory: Factory,
        query_params: str,
    ) -> None:
        response = await user_client.get("/sites", params=query_params)
        assert response.status_code == 400


@pytest.mark.asyncio
class TestPendingSitesHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        await factory.make_Site()
        site = await factory.make_PendingSite()

        response = await user_client.get("/requests")
        assert response.status_code == 200
        assert response.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [pending_site_details(site)],
        }

    async def test_post_accept(
        self, user_client: Client, factory: Factory
    ) -> None:
        site = await factory.make_PendingSite()

        response = await user_client.post(
            "/requests",
            json={"ids": [site.id], "accept": True},
        )
        assert response.status_code == 204
        [created_site] = await factory.get("site")
        assert created_site["accepted"]

    async def test_post_reject(
        self, user_client: Client, factory: Factory
    ) -> None:
        site = await factory.make_PendingSite()

        response = await user_client.post(
            "/requests",
            json={"ids": [site.id], "accept": False},
        )
        assert response.status_code == 204
        assert await factory.get("site") == []

    async def test_post_invalid_ids(
        self, user_client: Client, factory: Factory
    ) -> None:
        site = await factory.make_Site()

        # unknown IDs and IDs for non-pending sites are invalid
        ids = [site.id, 10000]
        response = await user_client.post(
            "/requests",
            json={"ids": ids, "accept": True},
        )
        assert response.status_code == 400
        assert response.json() == {
            "detail": {"message": "Unknown pending sites", "ids": ids}
        }
