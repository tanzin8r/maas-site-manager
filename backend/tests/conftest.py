import pytest

from .fixtures.app import (
    authenticated_user_app_client,
    user_app,
    user_app_client,
)
from .fixtures.db import (
    db,
    db_setup,
    fixture,
)

__all__ = [
    "db",
    "db_setup",
    "user_app",
    "authenticated_user_app_client",
    "user_app_client",
    "fixture",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--sqlalchemy-debug",
        help="print out SQLALchemy queries",
        action="store_true",
    )
