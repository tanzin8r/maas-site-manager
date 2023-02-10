from fastapi.testclient import TestClient
import pytest

from ...testing.db import Fixture


def test_root(user_app_client: TestClient) -> None:
    response = user_app_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"version": "0.0.1"}


@pytest.mark.asyncio
async def test_list_sites(
    user_app_client: TestClient, fixture: Fixture
) -> None:
    sites = await fixture.create(
        "site", [{"name": "site1"}, {"name": "site2"}]
    )
    response = user_app_client.get("/sites")
    assert response.status_code == 200
    assert response.json() == sites
