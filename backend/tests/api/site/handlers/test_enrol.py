from collections.abc import AsyncIterator
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import Config
from msm.jwt import (
    JWT,
    TokenAudience,
    TokenPurpose,
)
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
class TestEnrolPostHandler:
    async def test_post(self, factory: Factory, app_client: Client) -> None:
        auth_id = uuid4()
        await factory.make_Token(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLMENT,
        )
        cluster_uuid = str(uuid4())
        body = {
            "name": "new-site",
            "url": "https://site.example.com",
            "cluster_uuid": cluster_uuid,
            "metadata": {
                "city": "Los Angeles",
                "country": "US",
                "longitude": 40.05275079137782,
                "latitude": -107.17401328725524,
                "note": "this is a test site",
                "state": "CA",
                "address": "4242 Way St.",
                "postal_code": "80210",
                "timezone": "US/Pacific",
            },
        }
        response = await app_client.post(
            "/site/v1/enrol",
            json=body,
        )
        assert response.status_code == 202
        # a pending site is created
        [pending_site] = await factory.get("site")
        assert pending_site["name"] == body["name"]
        assert pending_site["url"] == body["url"]
        assert pending_site["cluster_uuid"] == body["cluster_uuid"]
        for k, v in body["metadata"].items():  # type: ignore[attr-defined]
            if k in ["latitude", "longitude"]:
                continue
            assert pending_site[k] == v
        assert pending_site["coordinates"] == (
            body["metadata"]["latitude"],  # type: ignore[index]
            body["metadata"]["longitude"],  # type: ignore[index]
        )
        assert not pending_site["accepted"]
        # the token is claimed
        [token] = await factory.get("token")
        assert token["site_id"] == pending_site["id"]

    async def test_post_partial_config(
        self,
        factory: Factory,
        app_client: Client,
    ) -> None:
        auth_id = uuid4()
        cluster_uuid = str(uuid4())
        await factory.make_Token(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLMENT,
        )
        body = {
            "name": "new-site",
            "url": "https://site.example.com",
            "cluster_uuid": cluster_uuid,
            "metadata": {
                "note": "this is a test site",
                "state": "CA",
                "address": "4242 Way St.",
                "postal_code": "80210",
                "timezone": "US/Pacific",
            },
        }
        response = await app_client.post(
            "/site/v1/enrol",
            json=body,
        )
        assert response.status_code == 202
        # a pending site is created
        [pending_site] = await factory.get("site")
        assert pending_site["name"] == body["name"]
        assert pending_site["url"] == body["url"]
        assert pending_site["cluster_uuid"] == body["cluster_uuid"]
        for k, v in body["metadata"].items():  # type: ignore[attr-defined]
            assert pending_site[k] == v
        assert pending_site["coordinates"] == None
        assert pending_site["country"] == ""
        assert pending_site["city"] == ""
        assert not pending_site["accepted"]
        # the token is claimed
        [token] = await factory.get("token")
        assert token["site_id"] == pending_site["id"]

    async def test_post_no_config(
        self, factory: Factory, app_client: Client
    ) -> None:
        auth_id = uuid4()
        cluster_uuid = str(uuid4())
        await factory.make_Token(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLMENT,
        )
        body = {
            "name": "new-site",
            "url": "https://site.example.com",
            "cluster_uuid": cluster_uuid,
        }
        response = await app_client.post(
            "/site/v1/enrol",
            json=body,
        )
        assert response.status_code == 202
        # a pending site is created
        [pending_site] = await factory.get("site")
        assert pending_site["cluster_uuid"] == body["cluster_uuid"]
        assert not pending_site["accepted"]
        # the token is claimed
        [token] = await factory.get("token")
        assert token["site_id"] == pending_site["id"]

    async def test_post_dont_allow_reuse(
        self, factory: Factory, app_client: Client
    ) -> None:
        auth_id = uuid4()
        await factory.make_Token(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLMENT,
        )
        body = {
            "name": "new-site",
            "url": "https://site.example.com",
            "cluster_uuid": str(uuid4()),
        }
        response = await app_client.post(
            "/site/v1/enrol",
            json=body,
        )
        assert response.status_code == 202
        # a pending site is created
        body = {
            "name": "new-site-dup",
            "url": "https://site.example.com",
            "cluster_uuid": str(uuid4()),
        }
        response = await app_client.post(
            "/site/v1/enrol",
            json=body,
        )
        assert response.status_code == 401

    async def test_no_token_match(
        self, factory: Factory, app_client: Client
    ) -> None:
        app_client.authenticate(
            uuid4(),
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLMENT,
        )
        response = await app_client.post(
            "/site/v1/enrol",
            json={
                "name": "new-site",
                "url": "https://site.example.com",
                "cluster_uuid": str(uuid4()),
            },
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
            token_purpose=TokenPurpose.ENROLMENT,
        )
        response = await app_client.post(
            "/site/v1/enrol",
            json={
                "name": "new-site",
                "url": "https://site.example.com",
                "cluster_uuid": str(uuid4()),
            },
        )
        assert response.status_code == 401

    async def test_token_missing_enrolment_purpose(
        self, factory: Factory, app_client: Client
    ) -> None:
        auth_id = uuid4()
        await factory.make_Token(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
        )
        response = await app_client.post(
            "/site/v1/enrol",
            json={
                "name": "new-site",
                "url": "https://site.example.com",
                "cluster_uuid": str(uuid4()),
            },
        )
        assert response.status_code == 401

    async def test_enrol_no_cluster_uuid(
        self, factory: Factory, app_client: Client
    ) -> None:
        auth_id = uuid4()
        await factory.make_Token(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLMENT,
        )
        body = {
            "name": "new-site",
            "url": "https://site.example.com",
        }
        response = await app_client.post(
            "/site/v1/enrol",
            json=body,
        )
        assert response.status_code == 422

    async def test_enrol_site_exists(
        self,
        factory: Factory,
        api_config: Config,
        app_client: Client,
    ) -> None:
        cluster_uuid = str(uuid4())
        await factory.make_Site(
            name="test1",
            auth_id=uuid4(),
            cluster_uuid=cluster_uuid,
            url="https://fake.url.com",
        )
        auth_id = uuid4()
        await factory.make_Token(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLMENT,
        )
        body = {
            "name": "test2",
            "cluster_uuid": cluster_uuid,
            "url": "https://site.example.com",
        }
        response = await app_client.post(
            "/site/v1/enrol",
            json=body,
        )
        assert response.status_code == 202
        sites = await factory.get("site")
        assert len(sites) == 1
        assert sites[0]["cluster_uuid"] == cluster_uuid
        assert sites[0]["name"] == body["name"]
        assert sites[0]["url"] == body["url"]
        assert sites[0]["accepted"] == False


@pytest.mark.asyncio
class TestEnrolGetHandler:
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
            token_purpose=TokenPurpose.ENROLMENT,
        )

        response = await app_client.get("/site/v1/enrol")
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
            token_purpose=TokenPurpose.ENROLMENT,
        )

        response = await app_client.get("/site/v1/enrol")
        assert response.status_code == 200
        payload = response.json()
        assert payload["token_type"] == "Bearer"
        # check if token is valid
        JWT.decode(
            payload["access_token"],
            key=api_config.token_secret_key,
            issuer=api_config.service_identifier,
            audience=TokenAudience.SITE,
            purpose=TokenPurpose.ACCESS,
        )


@pytest.mark.asyncio
class TestEnrolRefreshGetHandler:
    async def test_refresh(
        self,
        factory: Factory,
        api_config: Config,
        app_client: Client,
        service: SettingsService,
    ) -> None:
        auth_id = uuid4()
        await factory.make_Site(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ACCESS,
        )
        response = await app_client.get("/site/v1/enrol/refresh")
        assert response.status_code == 200
        payload = response.json()
        assert payload["token_type"] == "Bearer"
        token = JWT.decode(
            payload["access_token"],
            key=api_config.token_secret_key,
            issuer=api_config.service_identifier,
            audience=TokenAudience.SITE,
            purpose=TokenPurpose.ACCESS,
        )
        assert token.subject != str(auth_id)  # it's a new token
        settings = await service.get()
        assert (
            payload["rotation_interval_minutes"]
            == settings.token_rotation_interval_minutes
        )
        token_duration = token.expiration - token.issued
        assert (
            int(token_duration.total_seconds())
            == settings.token_lifetime_minutes * 60
        )

    async def test_refresh_unauthorized(
        self,
        factory: Factory,
        app_client: Client,
    ) -> None:
        auth_id = uuid4()
        await factory.make_Site(auth_id=auth_id)
        response = await app_client.get("site/v1/enrol/refresh")
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    async def test_refresh_invalid_token_purpose(
        self,
        factory: Factory,
        app_client: Client,
    ) -> None:
        auth_id = uuid4()
        await factory.make_Site(auth_id=auth_id)
        app_client.authenticate(
            auth_id,
            token_audience=TokenAudience.SITE,
            token_purpose=TokenPurpose.ENROLMENT,
        )
        response = await app_client.get("/site/v1/enrol/refresh")
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid token"}
