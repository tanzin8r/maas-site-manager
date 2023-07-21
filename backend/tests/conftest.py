import pytest

from .fixtures.db import (
    db,
    db_connection,
    db_setup,
    transaction_middleware_class,
)
from .fixtures.factory import factory

__all__ = [
    "db",
    "db_connection",
    "db_setup",
    "factory",
    "transaction_middleware_class",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--sqlalchemy-debug",
        help="print out SQLALchemy queries",
        action="store_true",
    )
