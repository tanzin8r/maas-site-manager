import pytest

from msm.db.models import Site
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestDetailsPostHandler:
    async def test_update_details(
        self, factory: Factory, site_client: Client
    ) -> None:
        details = {
            "name": "new-name",
            "url": "https://new-url.example.com",
        }
        response = await site_client.post("/details", json=details)
        assert response.status_code == 200
        [site] = await factory.get("site")
        assert site["name"] == "new-name"
        assert site["url"] == "https://new-url.example.com"

    async def test_creates_stats(
        self, factory: Factory, site_client: Client
    ) -> None:
        machine_counts = {
            "allocated": 10,
            "deployed": 20,
            "ready": 30,
            "error": 40,
            "other": 50,
        }
        assert await factory.get("site_data") == []
        response = await site_client.post(
            "/details", json={"machines_by_status": machine_counts}
        )
        assert response.status_code == 200
        [site_data] = await factory.get("site_data")
        assert site_data["machines_allocated"] == 10
        assert site_data["machines_deployed"] == 20
        assert site_data["machines_ready"] == 30
        assert site_data["machines_error"] == 40
        assert site_data["machines_other"] == 50

    async def test_update_stats(
        self, factory: Factory, api_site: Site, site_client: Client
    ) -> None:
        machine_counts = {
            "allocated": 10,
            "deployed": 20,
            "ready": 30,
            "error": 40,
            "other": 50,
        }
        await factory.make_SiteData(api_site.id)
        response = await site_client.post(
            "/details", json={"machines_by_status": machine_counts}
        )
        assert response.status_code == 200
        [site_data] = await factory.get("site_data")
        assert site_data["machines_allocated"] == 10
        assert site_data["machines_deployed"] == 20
        assert site_data["machines_ready"] == 30
        assert site_data["machines_error"] == 40
        assert site_data["machines_other"] == 50

    async def test_update_empty(
        self, factory: Factory, api_site: Site, site_client: Client
    ) -> None:
        response = await site_client.post("/details", json={})
        assert response.status_code == 200
        [site] = await factory.get("site")
        assert site["name"] == api_site.name
        assert site["url"] == api_site.url
        [site_data] = await factory.get("site_data")
        assert site_data["machines_allocated"] == 0
        assert site_data["machines_deployed"] == 0
        assert site_data["machines_ready"] == 0
        assert site_data["machines_error"] == 0
        assert site_data["machines_other"] == 0
