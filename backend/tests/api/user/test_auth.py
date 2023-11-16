import uuid

from fastapi import HTTPException
import pytest

from msm.api.user._auth import (
    authenticated_admin,
    authenticated_user,
)
from msm.db.models import User
from msm.service import ServiceCollection


@pytest.mark.asyncio
class TestAuthenticatedUser:
    async def test_valid_token(
        self,
        api_services: ServiceCollection,
        api_user: User,
    ) -> None:
        user = await authenticated_user(api_services, api_user.auth_id)
        assert user == api_user

    async def test_invalid_auth_id(
        self, api_services: ServiceCollection
    ) -> None:
        with pytest.raises(HTTPException) as error:
            await authenticated_user(api_services, uuid.uuid4())
        assert error.value.status_code == 401
        assert error.value.headers == {"WWW-Authenticate": "Bearer"}


class TestAuthenticatedAdmin:
    def test_admin(
        self,
        api_admin: User,
    ) -> None:
        admin = authenticated_admin(api_admin)
        assert admin == api_admin

    def test_not_admin(self, api_user: User) -> None:
        with pytest.raises(HTTPException) as error:
            authenticated_admin(api_user)
        assert error.value.status_code == 403
        assert error.value.headers == {"WWW-Authenticate": "Bearer"}
