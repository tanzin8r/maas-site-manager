import pytest

from .fixtures.app import (
    authenticated_admin_app_client,
    authenticated_user_app_client,
    user_app,
    user_app_client,
)
from .fixtures.db import (
    db,
    db_connection,
    db_setup,
    fixture,
)

__all__ = [
    "authenticated_admin_app_client",
    "authenticated_user_app_client",
    "db",
    "db_connection",
    "db_setup",
    "fixture",
    "user_app",
    "user_app_client",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--sqlalchemy-debug",
        help="print out SQLALchemy queries",
        action="store_true",
    )
