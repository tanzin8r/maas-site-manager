from collections.abc import Iterator
from datetime import (
    datetime,
    timedelta,
)
from typing import (
    Any,
    cast,
)
from uuid import (
    UUID,
    uuid4,
)

import pytest
from sqlalchemy import (
    ColumnOperators,
    Sequence,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.db.models import (
    ConnectionStatus,
    PendingSite,
    Site,
    SiteData,
    Token,
    User,
)
from msm.db.tables import METADATA
from msm.jwt import (
    JWT,
    TokenAudience,
    TokenPurpose,
)
from msm.password import hash_password
from msm.schema import TimeZone
from msm.time import now_utc


class Factory:
    """Helper for creating test fixtures."""

    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def next_id(self, table: str, pk_field: str = "id") -> int:
        """Return next ID for a table primary key."""
        # this assumes default PostgreSQL naming
        sequence = Sequence(f"{table}_{pk_field}_seq")
        result = await self.conn.execute(sequence.next_value())
        return cast(int, result.scalar())

    async def create(
        self,
        table: str,
        data: dict[str, Any] | list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Insert one or more entries in a table."""
        result = await self.conn.execute(
            METADATA.tables[table].insert().returning("*"), data
        )
        return [row._asdict() for row in result]

    async def get(
        self,
        table: str,
        *filters: ColumnOperators,
    ) -> list[dict[str, Any]]:
        """Get ore on more entries from a table."""
        tbl = METADATA.tables[table]
        result = await self.conn.execute(
            tbl.select()
            .where(*filters)  # type: ignore[arg-type]
            .order_by(*tbl.primary_key.columns)  # predictable order
        )
        return [row._asdict() for row in result]

    async def make_User(
        self,
        username: str | None = None,
        password: str | None = None,
        email: str | None = None,
        full_name: str | None = None,
        is_admin: bool = False,
    ) -> User:
        """Create a User."""
        id = await self.next_id("user")
        if username is None:
            username = f"user{id}"
        if password is None:
            password = username
        if email is None:
            email = f"{username}@example.com"
        if full_name is None:
            full_name = username.capitalize()
        [row] = await self.create(
            "user",
            [
                {
                    "id": id,
                    "username": username,
                    "email": email,
                    "full_name": full_name,
                    "is_admin": is_admin,
                    "password": hash_password(password),
                }
            ],
        )
        return User(**row)

    async def make_Token(
        self,
        issuer: str = "issuer",
        auth_id: UUID | None = None,
        lifetime: timedelta = timedelta(minutes=5),
        key: str = "",
    ) -> Token:
        """Create a Token."""
        id = await self.next_id("token")
        if auth_id is None:
            auth_id = uuid4()
        token = JWT.create(
            issuer=issuer,
            subject=str(auth_id),
            audience=TokenAudience.SITE,
            purpose=TokenPurpose.ENROLLMENT,
            key=key,
            duration=lifetime,
        )
        now = now_utc()
        [row] = await self.create(
            "token",
            [
                {
                    "id": id,
                    "auth_id": auth_id,
                    "value": token.encoded,
                    "created": now,
                    "expired": token.expiration,
                }
            ],
        )
        return Token(**row)

    async def make_Site(
        self,
        name: str | None = None,
        city: str = "",
        country: str = "",
        url: str | None = None,
        timezone: str | None = None,
        coordinates: tuple[float, float] | None = None,
        connection_status: ConnectionStatus = ConnectionStatus.UNKNOWN,
        auth_id: UUID | None = None,
    ) -> Site:
        """Create a Site."""
        id = await self.next_id("site")
        if name is None:
            name = f"site{id}"
        if url is None:
            url = f"https://{name}.example.com/"
        if auth_id is None:
            auth_id = uuid4()
        [row] = await self.create(
            "site",
            [
                {
                    "id": id,
                    "name": name,
                    "url": url,
                    "city": city,
                    "country": country,
                    "timezone": (
                        getattr(TimeZone, timezone) if timezone else ""
                    ),
                    "coordinates": coordinates,
                    "accepted": True,
                    "created": now_utc(),
                    "auth_id": auth_id,
                }
            ],
        )
        # compute the name_unique attribute
        site_table = METADATA.tables["site"]
        result = await self.conn.execute(
            select(func.count() == 1)
            .select_from(site_table)
            .filter(site_table.c.name == name)
        )
        row["name_unique"] = result.one()[0]
        return Site(connection_status=connection_status, **row)

    async def make_PendingSite(
        self,
        name: str | None = None,
        url: str | None = None,
        auth_id: UUID | None = None,
    ) -> PendingSite:
        """Create a PendingSite."""
        id = await self.next_id("site")
        if name is None:
            name = f"site{id}"
        if url is None:
            url = f"https://{name}.example.com/"
        if auth_id is None:
            auth_id = uuid4()
        [row] = await self.create(
            "site",
            {
                "id": id,
                "name": name,
                "url": url,
                "accepted": False,
                "created": now_utc(),
                "auth_id": auth_id,
            },
        )
        return PendingSite(**row)

    async def make_SiteData(
        self,
        site_id: int,
        machines_allocated: int = 0,
        machines_deployed: int = 0,
        machines_ready: int = 0,
        machines_error: int = 0,
        machines_other: int = 0,
        last_seen: datetime | None = None,
    ) -> SiteData:
        """Create SiteData for a Site."""
        if last_seen is None:
            last_seen = now_utc()
        [row] = await self.create(
            "site_data",
            [
                {
                    "site_id": site_id,
                    "machines_allocated": machines_allocated,
                    "machines_deployed": machines_deployed,
                    "machines_ready": machines_ready,
                    "machines_error": machines_error,
                    "machines_other": machines_other,
                    "last_seen": last_seen,
                }
            ],
        )
        machines_total = (
            machines_allocated
            + machines_deployed
            + machines_ready
            + machines_error
            + machines_other
        )
        return SiteData(machines_total=machines_total, **row)

    async def make_Config(self, name: str, value: Any = None) -> None:
        """Create an entry in the global configuration."""
        await self.create("config", {"name": name, "value": value})

    async def make_Setting(self, name: str, value: Any = None) -> None:
        """Create an entry in the global settings."""
        await self.create("setting", {"name": name, "value": value})


@pytest.fixture
def factory(db_connection: AsyncConnection) -> Iterator[Factory]:
    yield Factory(db_connection)
