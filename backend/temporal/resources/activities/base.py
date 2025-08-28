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


def compose_url(prefix: str, path: str) -> str:
    return "/".join(
        [
            prefix.rstrip("/"),
            path,
        ]
    )


def get_selection_key(os: str, release: str, arch: str) -> str:
    return f"{os}---{release}---{arch}"
