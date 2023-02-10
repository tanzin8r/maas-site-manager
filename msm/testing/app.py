from typing import Iterable

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from ..db import Database
from ..user_api import create_app


@pytest.fixture
def user_app(db: Database) -> Iterable[FastAPI]:
    """The API for users."""
    yield create_app(db.dsn)


@pytest.fixture
def user_app_client(user_app: FastAPI) -> Iterable[TestClient]:
    """Client for the user API."""
    yield TestClient(user_app)
