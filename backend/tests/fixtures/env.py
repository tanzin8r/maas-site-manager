from collections.abc import Iterator
import os

import pytest

from tests.fixtures.db import DBConfig


@pytest.fixture(autouse=True)
def unset_settings_environ(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Ensure environment variables related to settings are not set."""
    for var in os.environ:
        if var.startswith("MSM_"):
            monkeypatch.delenv(var)
    yield


@pytest.fixture
def settings_environ(
    monkeypatch: pytest.MonkeyPatch, db_setup: DBConfig
) -> Iterator[dict[str, str]]:
    """Set and return environment variables for application settings."""
    environ = db_setup.settings_environ
    for key, value in environ.items():
        monkeypatch.setenv(key, value)
    yield environ
