from uuid import uuid4

from fastapi import HTTPException
from httpx import Request
import pytest

from msm.api._auth import (
    auth_id_from_token,
    bearer_token,
    token_response,
)
from msm.db.models import Config
from msm.jwt import (
    JWT,
    TokenAudience,
)


def test_token_response(api_config: Config) -> None:
    auth_id = uuid4()
    response = token_response(api_config, auth_id, TokenAudience.API)
    assert response.token_type == "Bearer"
    token = JWT.decode(
        response.access_token,
        key=api_config.token_secret_key,
        issuer=api_config.service_identifier,
        audience=TokenAudience.API,
    )
    assert token.subject == str(auth_id)
    assert token.audience == [TokenAudience.API]


@pytest.mark.asyncio
class TestBearerToken:
    async def test_valid_token(self) -> None:
        request = Request(
            "GET", "/test", headers={"Authorization": "Bearer ABCD"}
        )
        assert await bearer_token(request) == "ABCD"  # type: ignore[arg-type]

    async def test_no_token(self) -> None:
        request = Request("GET", "/test")
        with pytest.raises(HTTPException) as error:
            await bearer_token(request)  # type: ignore[arg-type]
        assert error.value.status_code == 401
        assert error.value.headers == {"WWW-Authenticate": "Bearer"}


class TestAuthIDFromToken:
    def test_valid_token(self, api_config: Config) -> None:
        auth_id = uuid4()
        token = JWT.create(
            issuer=api_config.service_identifier,
            subject=str(auth_id),
            audience=TokenAudience.API,
            key=api_config.token_secret_key,
        )
        get_auth_id = auth_id_from_token(bearer_token, TokenAudience.API)
        assert get_auth_id(api_config, token.encoded) == auth_id

    def test_invalid_token(self, api_config: Config) -> None:
        get_auth_id = auth_id_from_token(bearer_token, TokenAudience.API)
        with pytest.raises(HTTPException) as error:
            get_auth_id(api_config, "invalid")
        assert error.value.status_code == 401
