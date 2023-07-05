from httpx import AsyncClient
import pytest

from msm import __version__

from ...fixtures.app import AuthAsyncClient


@pytest.mark.asyncio
async def test_get(user_app_client: AsyncClient) -> None:
    response = await user_app_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}


@pytest.mark.asyncio
async def test_get_authenticated(
    authenticated_user_app_client: AuthAsyncClient,
) -> None:
    response = await authenticated_user_app_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}
