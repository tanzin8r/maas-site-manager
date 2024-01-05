from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import pytest
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db import Database
from msm.middleware import TransactionMiddleware

TEST_DB_NAME = "msm"


@dataclass
class DBConfig:
    """Database configuration."""

    db: str
    user: str
    socketdir: str
    port: int

    @property
    def dsn(self) -> URL:
        """DSN URL for the test database."""
        return URL.create(
            "postgresql+asyncpg",
            host=self.socketdir,
            port=self.port,
            database=self.db,
            username=self.user,
        )

    @property
    def settings_environ(self) -> dict[str, str]:
        """Return environment settings for the test database."""
        return {
            "MSM_DB_HOST": self.socketdir,
            "MSM_DB_NAME": self.db,
            "MSM_DB_USER": self.user,
            "MSM_DB_PORT": str(self.port),
        }


@pytest.fixture(scope="session")
def db_setup(postgresql_proc: PostgreSQLExecutor) -> Iterator[DBConfig]:
    """Setup and teardown the database. Return the URL."""
    port = postgresql_proc.port
    user = postgresql_proc.user
    socketdir = postgresql_proc.unixsocketdir
    janitor = DatabaseJanitor(
        user, socketdir, port, TEST_DB_NAME, postgresql_proc.version
    )
    with janitor:
        yield DBConfig(TEST_DB_NAME, user, socketdir, port)


@pytest.fixture
async def db(
    request: pytest.FixtureRequest,
    db_setup: DBConfig,
) -> AsyncIterator[Database]:
    """Set up the database schema."""
    echo = request.config.getoption("sqlalchemy_debug")
    db = Database(db_setup.dsn, echo=echo)
    # don't go through migration, just apply schema, since the DB is empty
    await db.ensure_schema(migrate=False)
    yield db
    await db.drop_schema()


@pytest.fixture
async def db_connection(db: Database) -> AsyncIterator[AsyncConnection]:
    """The database connection."""
    async with db.engine.connect() as conn:
        conn.begin()
        yield conn
        await conn.rollback()


@pytest.fixture
def transaction_middleware_class(
    db_connection: AsyncConnection,
) -> Iterator[type]:
    class ConnectionReusingTransactionMiddleware(TransactionMiddleware):
        @asynccontextmanager
        async def get_connection(self) -> AsyncIterator[AsyncConnection]:
            yield db_connection

    yield ConnectionReusingTransactionMiddleware
