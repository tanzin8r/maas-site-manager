import pytest

from msm import __version__

from ...fixtures.client import Client


@pytest.mark.asyncio
async def test_get(user_client: Client) -> None:
    response = await user_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}
