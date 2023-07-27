import datetime as datetime_module
from typing import Iterator

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


# XXX Pydantic v2 removes trailing zeroes from ISO timestamps, which sometimes
# causes comparisons to fail since datetime.isoformat() includes them.
#
# This overrides isoformat() to strip them, and fromisoformat() to accept a
# timestamp with less than 6 decimal points.
#
# See https://github.com/pydantic/pydantic/issues/6761 for the Pydantic bug.
#


@pytest.fixture(autouse=True)
def override_datetime_isoformat(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[None]:
    class datetime(datetime_module.datetime):
        def isoformat(self) -> str:  # type: ignore
            return super().isoformat().rstrip("0")

        def fromisoformat(self, datestring: str):  # type: ignore
            if "." in datestring:
                _, decimal = datestring.rsplit(".", 1)
                missing_digits = 6 - len(decimal)
                if missing_digits > 0:
                    datestring += "0" * missing_digits
            return super().fromisoformat(datestring)

    monkeypatch.setattr(
        datetime_module,
        "datetime",
        datetime,
    )
    yield


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--sqlalchemy-debug",
        help="print out SQLALchemy queries",
        action="store_true",
    )
