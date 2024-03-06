import pytest

from tests.fixtures.db import (
    db,
    db_connection,
    db_setup,
    transaction_middleware_class,
)
from tests.fixtures.env import (
    settings_environ,
    unset_settings_environ,
)
from tests.fixtures.factory import factory

__all__ = [
    "db",
    "db_connection",
    "db_setup",
    "factory",
    "settings_environ",
    "transaction_middleware_class",
    "unset_settings_environ",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--sqlalchemy-debug",
        help="print out SQLALchemy queries",
        action="store_true",
    )
