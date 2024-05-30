from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.service import SettingsService
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.fixture
async def service(
    db_connection: AsyncConnection,
) -> AsyncIterator[SettingsService]:
    service = SettingsService(db_connection)
    await service.ensure()
    yield service


@pytest.mark.asyncio
async def test_settings_get(
    factory: Factory, admin_client: Client, service: SettingsService
) -> None:
    await service.update(
        {
            "service_url": "https://sitemanager.example.com/",
            "enrolment_url": "https://sitemanager.example.com/site/v1/enrol",
            "token_lifetime_minutes": 10,
            "token_rotation_interval_minutes": 100,
        }
    )
    response = await admin_client.get("/settings")
    assert response.status_code == 200
    assert response.json() == {
        "service_url": "https://sitemanager.example.com/",
        "enrolment_url": "https://sitemanager.example.com/site/v1/enrol",
        "token_lifetime_minutes": 10,
        "token_rotation_interval_minutes": 100,
    }


@pytest.mark.asyncio
async def test_settings_patch(
    factory: Factory, admin_client: Client, service: SettingsService
) -> None:
    response = await admin_client.patch(
        "/settings",
        json={
            "service_url": "https://sitemanager.example.com",
            "enrolment_url": "https://sitemanager.example.com/site/v1/enrol",
            "token_lifetime_minutes": 10,
            "token_rotation_interval_minutes": 100,
        },
    )
    assert response.status_code == 200

    response = await admin_client.get("/settings")
    assert response.status_code == 200
    assert response.json() == {
        "service_url": "https://sitemanager.example.com",
        "enrolment_url": "https://sitemanager.example.com/site/v1/enrol",
        "token_lifetime_minutes": 10,
        "token_rotation_interval_minutes": 100,
    }
