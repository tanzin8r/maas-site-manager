from collections.abc import AsyncIterator
from typing import cast
from uuid import (
    uuid4,
)

from fastapi import FastAPI
import pytest
from pytest_mock import MockerFixture, MockType

from msm.apiserver.db.models import (
    Config,
    User,
    Worker,
)
from msm.apiserver.service import BootSourceWorkflowService
from msm.common.jwt import TokenAudience, TokenPurpose
from tests.apiserver.conftest import make_api_client
from tests.fixtures.client import Client
from tests.fixtures.factory import Factory

API_USER_NAME = "user"
API_ADMIN_NAME = "admin"


@pytest.fixture(autouse=True)
def patch_index_service(mocker: MockerFixture) -> None:
    # disable refreshing the index view, not required in these tests
    mocker.patch("msm.apiserver.service.IndexService.refresh")


@pytest.fixture
async def api_user(factory: Factory) -> AsyncIterator[User]:
    """An API user (without admin rights)."""
    yield await factory.make_User(username=API_USER_NAME, is_admin=False)


@pytest.fixture
async def api_admin(factory: Factory) -> AsyncIterator[User]:
    """An API administrator."""
    yield await factory.make_User(username=API_ADMIN_NAME, is_admin=True)


@pytest.fixture
async def api_worker(factory: Factory) -> AsyncIterator[Worker]:
    """An API administrator."""
    auth_id = uuid4()
    await factory.make_Token(
        auth_id=auth_id,
        audience=TokenAudience.WORKER,
        purpose=TokenPurpose.ACCESS,
    )
    yield Worker(auth_id=auth_id)


@pytest.fixture
async def user_client(
    api_app: FastAPI, api_config: Config, api_user: User
) -> AsyncIterator[Client]:
    """Authenticated client for the API user, under the /api/v1 prefix."""
    async with make_api_client(
        api_app, api_config, prefix="/api/v1"
    ) as client:
        client.authenticate(api_user.auth_id)
        yield client


@pytest.fixture
async def admin_client(
    api_app: FastAPI, api_config: Config, api_admin: User
) -> AsyncIterator[Client]:
    """Authenticated client for the API admin, under the /api/v1 prefix."""
    async with make_api_client(
        api_app, api_config, prefix="/api/v1"
    ) as client:
        client.authenticate(api_admin.auth_id)
        yield client


@pytest.fixture
def mock_workflow_service(mocker: MockerFixture) -> MockType:
    mock_workflows = mocker.patch(
        "msm.apiserver.service.BootSourceWorkflowService",
        spec=BootSourceWorkflowService,
    )
    mock = mock_workflows.return_value
    return cast(MockType, mock)
