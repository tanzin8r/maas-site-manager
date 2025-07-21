from httpx import AsyncClient

__version__ = "0.1"


class BaseActivity:
    def __init__(self, user_agent: str | None = None) -> None:
        self.client = self._create_client(user_agent)

    def _create_client(self, user_agent: str | None = None) -> AsyncClient:
        user_agent = user_agent or f"maas-site-manager/{__version__}"
        return AsyncClient(trust_env=True, headers={"User-Agent": user_agent})

    def _get_header(self, jwt: str) -> dict[str, str]:
        return {"Authorization": f"bearer {jwt}"}
