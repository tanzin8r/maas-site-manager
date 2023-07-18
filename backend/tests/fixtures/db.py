from dataclasses import dataclass
from typing import (
    AsyncIterator,
    Iterator,
)

import pytest
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import Database

TEST_DB_NAME = "msm"


@dataclass
class TestDSN:
    """Database DSN."""

    db: str
    user: str
    socketdir: str
    port: int

    @property
    def sync_dsn(self) -> str:
        return f"postgresql+psycopg://{self._base_dsn()}"

    @property
    def async_dsn(self) -> str:
        return f"postgresql+asyncpg://{self._base_dsn()}"

    def _base_dsn(self) -> str:
        return (
            f"/{self.db}?"
            f"user={self.user}&host={self.socketdir}&port={self.port}"
        )


@pytest.fixture(scope="session")
def db_setup(postgresql_proc: PostgreSQLExecutor) -> Iterator[TestDSN]:
    """Setup and teardown the database. Return the URL."""
    port = postgresql_proc.port
    user = postgresql_proc.user
    socketdir = postgresql_proc.unixsocketdir
    janitor = DatabaseJanitor(
        user, socketdir, port, TEST_DB_NAME, postgresql_proc.version
    )
    with janitor:
        yield TestDSN(TEST_DB_NAME, user, socketdir, port)


@pytest.fixture
async def db(
    request: pytest.FixtureRequest, db_setup: TestDSN
) -> AsyncIterator[Database]:
    """Set up the database schema."""
    echo = request.config.getoption("sqlalchemy_debug")
    db = Database(db_setup.async_dsn, echo=echo)
    await db.ensure_schema()
    yield db
    await db.drop_schema()


@pytest.fixture
async def db_connection(db: Database) -> AsyncIterator[AsyncConnection]:
    """The database connection."""
    async with db.engine.connect() as conn:
        conn.begin()
        yield conn
        await conn.rollback()
