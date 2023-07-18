from datetime import (
    datetime,
    timedelta,
)
from typing import Any

from httpx import Response
import pytest

from msm.db.models import ConnectionStatus
from msm.settings import SETTINGS

from ...fixtures.client import Client
from ...fixtures.factory import Factory


def site_details(**extra_details: Any) -> dict[str, Any]:
    """Return sample details for creating a site."""
    details = {
        "name": "LondonHQ",
        "name_unique": True,
        "url": "https://londoncalling.example.com",
        "accepted": True,
    }
    details.update(extra_details)
    return details


@pytest.mark.asyncio
class TestSitesHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        sites = await factory.create(
            "site",
            [
                site_details(city="London"),
                site_details(name="BerlinHQ", city="Berlin"),
            ],
        )
        for site in sites:
            site["connection_status"] = ConnectionStatus.UNKNOWN
            site["stats"] = None
            del site["created"]
            del site["accepted"]
        page1 = await user_client.get("/sites")
        assert page1.status_code == 200
        assert page1.json() == {
            "page": 1,
            "size": 20,
            "total": 2,
            "items": sites,
        }
        filtered = await user_client.get("/sites?city=onDo")  # vs London
        assert filtered.status_code == 200
        assert filtered.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [sites[0]],
        }
        paginated = await user_client.get("/sites?page=2&size=1")
        assert paginated.status_code == 200
        assert paginated.json() == {
            "page": 2,
            "size": 1,
            "total": 2,
            "items": [sites[1]],
        }

    async def test_get_only_accepted(
        self, user_client: Client, factory: Factory
    ) -> None:
        created_site, _ = await factory.create(
            "site",
            [
                site_details(),
                site_details(name="BerlinHQ", accepted=False),
            ],
        )
        created_site["stats"] = None
        created_site["connection_status"] = ConnectionStatus.UNKNOWN
        del created_site["created"]
        del created_site["accepted"]

        page1 = await user_client.get("/sites")
        assert page1.status_code == 200
        assert page1.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [created_site],
        }

    async def test_get_filter_timezone(
        self, user_client: Client, factory: Factory
    ) -> None:
        [created_site, _] = await factory.create(
            "site",
            [
                site_details(timezone="Europe/London"),
                site_details(name="BerlinHQ", timezone="Europe/Berlin"),
            ],
        )
        created_site["stats"] = None
        created_site["connection_status"] = ConnectionStatus.UNKNOWN
        del created_site["created"]
        del created_site["accepted"]
        page1 = await user_client.get("/sites?timezone=Europe/London")
        assert page1.status_code == 200
        assert page1.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [created_site],
        }

    async def test_get_with_stats(
        self, user_client: Client, factory: Factory
    ) -> None:
        [site] = await factory.create("site", [site_details()])
        [site_data] = await factory.create(
            "site_data",
            [
                {
                    "site_id": site["id"],
                    "allocated_machines": 10,
                    "deployed_machines": 20,
                    "ready_machines": 30,
                    "error_machines": 40,
                    "other_machines": 5,
                    "last_seen": datetime.utcnow(),
                }
            ],
        )
        del site_data["id"]
        del site_data["site_id"]
        site_data["last_seen"] = site_data["last_seen"].isoformat()
        site_data["total_machines"] = 105
        site["stats"] = site_data
        site["connection_status"] = ConnectionStatus.STABLE
        del site["created"]
        del site["accepted"]

        page = await user_client.get("/sites")
        assert page.status_code == 200
        assert page.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [site],
        }

    async def test_get_connection_status(
        self, user_client: Client, factory: Factory
    ) -> None:
        [site] = await factory.create("site", [site_details()])
        await factory.create(
            "site_data",
            [
                {
                    "site_id": site["id"],
                    "allocated_machines": 10,
                    "deployed_machines": 20,
                    "ready_machines": 30,
                    "error_machines": 40,
                    "other_machines": 5,
                    # Set last_seen to 1 second after the
                    # lost_connection_threshold setting in order to test
                    # that the connection is marked as lost
                    "last_seen": datetime.utcnow()
                    - timedelta(
                        seconds=SETTINGS.lost_connection_threshold_seconds + 1
                    ),
                },
            ],
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
        await factory.create(
            "site",
            [site_details(city="Milan", country="IT")],
        )
        await factory.create(
            "site",
            [site_details(city="Paris", country="FR")],
        )
        await factory.create("site", [site_details(city="Rome", country="IT")])
        await factory.create(
            "site", [site_details(city="London", country="GB")]
        )

        site_id = -1
        response = await user_client.get(f"/sites/{site_id}")
        assert response.status_code == 404
        assert response.json()["detail"]["message"] == "Site does not exist."

        site_id = 2
        response = await user_client.get(f"/sites/{site_id}")
        assert response.status_code == 200
        assert response.json()["city"] == "Paris"
        assert response.json()["country"] == "FR"

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
        def extract_cities(resp: Response) -> list[str]:
            return [site["city"] for site in resp.json()["items"]]

        await factory.create(
            "site",
            [site_details(city="Milan", country="IT")],
        )
        await factory.create(
            "site",
            [site_details(city="Paris", country="FR")],
        )
        await factory.create("site", [site_details(city="Rome", country="IT")])
        await factory.create(
            "site", [site_details(city="London", country="GB")]
        )

        response = await user_client.get("/sites", params=query_params)
        assert extract_cities(response) == expected_result

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
        await factory.create(
            "site", [site_details(city="Milan", country="IT")]
        )

        # not sortable
        response = await user_client.get("/sites", params=query_params)
        assert response.status_code == 400


@pytest.mark.asyncio
class TestPendingSitesHandler:
    async def test_get(self, user_client: Client, factory: Factory) -> None:
        _, pending_site = await factory.create(
            "site",
            [
                site_details(),
                site_details(name="BerlinHQ", accepted=False),
            ],
        )

        response = await user_client.get("/requests")
        assert response.status_code == 200
        assert response.json() == {
            "page": 1,
            "size": 20,
            "total": 1,
            "items": [
                {
                    "id": pending_site["id"],
                    "name": pending_site["name"],
                    "url": pending_site["url"],
                    "created": pending_site["created"].isoformat(),
                },
            ],
        }

    async def test_post_accept(
        self, user_client: Client, factory: Factory
    ) -> None:
        [pending_site] = await factory.create(
            "site", [site_details(accepted=False)]
        )

        response = await user_client.post(
            "/requests",
            json={"ids": [pending_site["id"]], "accept": True},
        )
        assert response.status_code == 204
        [created_site] = await factory.get("site")
        assert created_site["accepted"]

    async def test_post_reject(
        self, user_client: Client, factory: Factory
    ) -> None:
        [pending_site] = await factory.create(
            "site", [site_details(accepted=False)]
        )

        response = await user_client.post(
            "/requests",
            json={"ids": [pending_site["id"]], "accept": False},
        )
        assert response.status_code == 204
        assert await factory.get("site") == []

    async def test_post_invalid_ids(
        self, user_client: Client, factory: Factory
    ) -> None:
        [site] = await factory.create("site", [site_details()])
        # unknown IDs and IDs for non-pending sites are invalid
        ids = [site["id"], 10000]
        response = await user_client.post(
            "/requests",
            json={"ids": ids, "accept": True},
        )
        assert response.status_code == 400
        assert response.json() == {
            "detail": {"message": "Unknown pending sites", "ids": ids}
        }
