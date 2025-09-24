from httpx import AsyncClient

from msm.temporal.activities.base import BaseActivity


class TestBaseActivity:
    def test_create_client_default_user_agent(self) -> None:
        activity = BaseActivity()
        assert isinstance(activity.client, AsyncClient)
        assert "User-Agent" in activity.client.headers
        assert activity.client.headers["User-Agent"].startswith(
            "maas-site-manager/"
        )

    def test_create_client_custom_user_agent(self) -> None:
        custom_agent = "custom-agent/1.0"
        activity = BaseActivity(user_agent=custom_agent)
        assert activity.client.headers["User-Agent"] == custom_agent

    def test_get_header(self) -> None:
        activity = BaseActivity()
        jwt = "test-jwt"
        headers = activity._get_header(jwt)
        assert headers == {"Authorization": f"bearer {jwt}"}
