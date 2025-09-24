from uuid import UUID

from httpx import (
    AsyncClient,
    Response,
)

from msm.common.jwt import (
    JWT,
    TokenAudience,
    TokenPurpose,
)


class Client(AsyncClient):
    """Equivalent to AsyncClient, but has the ability to send
    requests from an authorized login"""

    service_identifier = ""
    token_key = ""
    _auth_token = ""

    def set_token_config(self, service_identifier: str, key: str) -> None:
        self.service_identifier = service_identifier
        self.token_key = key

    def authenticate(
        self,
        auth_id: UUID | None,
        token_audience: TokenAudience = TokenAudience.API,
        token_purpose: TokenPurpose | None = None,
    ) -> None:
        """Set or unset authentication token for a user ID."""
        if auth_id is None:
            self._auth_token = ""
        else:
            self._auth_token = JWT.create(
                issuer=self.service_identifier,
                subject=str(auth_id),
                audience=token_audience,
                purpose=token_purpose,
                key=self.token_key,
            ).encoded

    async def request(self, *args, **kwargs) -> Response:  # type: ignore
        """Generate a request, setting the auth token if set.

        All other request methods use this in the backend to construct their
        requests.
        """
        if self._auth_token:
            headers = kwargs.get("headers") or {}  # might be set to None
            headers["Authorization"] = f"Bearer {self._auth_token}"
            kwargs["headers"] = headers
        return await super().request(*args, **kwargs)
