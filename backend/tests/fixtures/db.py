from dataclasses import dataclass
from typing import (
    Any,
    AsyncGenerator,
    Iterator,
)

import pytest
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import (
    ColumnOperators,
    create_engine,
)
from sqlalchemy.ext.asyncio.session import AsyncSession

from msm.db import (
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
def db(
    request: pytest.FixtureRequest, db_setup: TestDSN
) -> Iterator[Database]:
    """Set up the database schema."""
    echo = request.config.getoption("sqlalchemy_debug")
    engine = create_engine(db_setup.sync_dsn, echo=echo)
    with engine.connect() as conn:
        with conn.begin():
            METADATA.create_all(conn)
        yield Database(db_setup.async_dsn)
        with conn.begin():
            METADATA.drop_all(conn)


@pytest.fixture
async def session(db: Database) -> AsyncGenerator[AsyncSession, None]:
    """A database session."""
    async with db.session() as session:
        yield session
        await session.rollback()


class Fixture:
    """Helper for creating test fixtures."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def create(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]] | None = None,
        commit: bool = False,
    ) -> list[dict[str, Any]]:
        result = await self.session.execute(
            METADATA.tables[table].insert().returning("*"), data
        )
        if commit:
            await self.session.commit()
        return [row._asdict() for row in result]

    async def get(
        self,
        table: str,
        *filters: ColumnOperators,
    ) -> list[dict[str, Any]]:
        """Take a peak what is in there"""
        result = await self.session.execute(
            METADATA.tables[table]
            .select()
            .where(*filters)  # type: ignore[arg-type]
        )
        return [row._asdict() for row in result]


@pytest.fixture
def fixture(session: AsyncSession) -> Iterator[Fixture]:
    yield Fixture(session)
