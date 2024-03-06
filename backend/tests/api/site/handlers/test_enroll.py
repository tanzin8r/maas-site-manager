from datetime import timedelta
from uuid import uuid4

import pytest

from msm.db.models import Config
from msm.jwt import (
    JWT,
    TokenAudience,
    TokenPurpose,
)
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory


@pytest.mark.asyncio
class TestEnrollPostHandler:
    async def test_post(self, factory: Factory, app_client: Client) -> None:
        auth_id = uuid4()
        await factory.make_Token(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLLMENT,
        )
        response = await app_client.post(
            "/site/v1/enroll",
            json={"name": "new-site", "url": "https://site.example.com"},
        )
        assert response.status_code == 202
        # the token is removed
        assert await factory.get("token") == []
        # a pending site is created
        [pending_site] = await factory.get("site")
        assert pending_site["auth_id"] == auth_id
        assert not pending_site["accepted"]

    async def test_no_token_match(
        self, factory: Factory, app_client: Client
    ) -> None:
        app_client.authenticate(
            uuid4(),
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLLMENT,
        )
        response = await app_client.post(
            "/site/v1/enroll",
            json={"name": "new-site", "url": "https://site.example.com"},
        )
        assert response.status_code == 401

    async def test_token_expired(
        self, factory: Factory, app_client: Client
    ) -> None:
        auth_id = uuid4()
        await factory.make_Token(auth_id=auth_id, lifetime=timedelta(hours=-1))
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLLMENT,
        )
        response = await app_client.post(
            "/site/v1/enroll",
            json={"name": "new-site", "url": "https://site.example.com"},
        )
        assert response.status_code == 401

    async def test_token_missing_enrollment_purpose(
        self, factory: Factory, app_client: Client
    ) -> None:
        auth_id = uuid4()
        await factory.make_Token(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
        )
        response = await app_client.post(
            "/site/v1/enroll",
            json={"name": "new-site", "url": "https://site.example.com"},
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestEnrollGetHandler:
    async def test_pending(
        self,
        factory: Factory,
        app_client: Client,
    ) -> None:
        auth_id = uuid4()
        await factory.make_PendingSite(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLLMENT,
        )

        response = await app_client.get("/site/v1/enroll")
        assert response.status_code == 204

    async def test_accepted(
        self,
        factory: Factory,
        api_config: Config,
        app_client: Client,
    ) -> None:
        auth_id = uuid4()
        await factory.make_Site(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLLMENT,
        )

        response = await app_client.get("/site/v1/enroll")
        assert response.status_code == 200
        payload = response.json()
        assert payload["token_type"] == "Bearer"
        token = JWT.decode(
            payload["access_token"],
            key=api_config.token_secret_key,
            issuer=api_config.service_identifier,
            audience=TokenAudience.SITE,
        )
        assert token.subject == str(auth_id)
