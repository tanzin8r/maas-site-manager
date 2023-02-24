from dataclasses import dataclass
from typing import (
    Any,
    Iterator,
)

import pytest
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import create_engine

from ..db import (
    Database,
    METADATA,
)

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
def db(db_setup: TestDSN) -> Iterator[Database]:
    """Set up the database schema."""
    engine = create_engine(db_setup.sync_dsn)
    with engine.connect() as conn:
        with conn.begin():
            METADATA.create_all(conn)
        yield Database(db_setup.async_dsn)
        with conn.begin():
            METADATA.drop_all(conn)


class Fixture:
    """Helper for creating test fixtures."""

    def __init__(self, db: Database):
        self.db = db

    async def create(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        async with self.db.session() as session:
            result = await session.execute(
                METADATA.tables[table].insert().returning("*"), data
            )
            await session.commit()
            return [row._asdict() for row in result]


@pytest.fixture
def fixture(db: Database) -> Iterator[Fixture]:
    yield Fixture(db)
