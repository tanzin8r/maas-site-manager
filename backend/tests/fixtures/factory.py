from datetime import (
    datetime,
    timedelta,
)
from typing import (
    Any,
    cast,
    Iterator,
)
from uuid import (
    UUID,
    uuid4,
)

import pytest
from sqlalchemy import (
    ColumnOperators,
    Sequence,
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
from msm.password import hash_password
from msm.schema import TimeZone


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
        result = await self.conn.execute(
            METADATA.tables[table]
            .select()
            .where(*filters)  # type: ignore[arg-type]
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
        value: UUID | None = None,
        site_id: int | None = None,
        lifetime: timedelta = timedelta(minutes=5),
    ) -> Token:
        """Create a Token."""
        id = await self.next_id("token")
        if value is None:
            value = uuid4()
        now = datetime.utcnow()
        [row] = await self.create(
            "token",
            [
                {
                    "id": id,
                    "site_id": site_id,
                    "value": value,
                    "created": now,
                    "expired": now + lifetime,
                }
            ],
        )
        return Token(**row)

    async def make_Site(
        self,
        name: str | None = None,
        city: str | None = None,
        country: str | None = None,
        url: str | None = None,
        timezone: str | None = None,
        latitude: str | None = None,
        longitude: str | None = None,
        connection_status: ConnectionStatus = ConnectionStatus.UNKNOWN,
    ) -> Site:
        """Create a Site."""
        id = await self.next_id("site")
        if name is None:
            name = f"site{id}"
        if url is None:
            url = f"https://{name}.example.com/"
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
                        getattr(TimeZone, timezone) if timezone else None
                    ),
                    "latitude": latitude,
                    "longitude": longitude,
                    "name_unique": True,
                    "accepted": True,
                    "created": datetime.utcnow(),
                }
            ],
        )
        return Site(connection_status=connection_status, **row)

    async def make_PendingSite(
        self,
        name: str | None = None,
        url: str | None = None,
    ) -> PendingSite:
        """Create a PendingSite."""
        id = await self.next_id("site")
        if name is None:
            name = f"site{id}"
        if url is None:
            url = f"https://{name}.example.com/"
        [row] = await self.create(
            "site",
            {
                "id": id,
                "name": name,
                "url": url,
                "accepted": False,
                "created": datetime.utcnow(),
            },
        )
        return PendingSite(**row)

    async def make_SiteData(
        self,
        site_id: int,
        allocated_machines: int = 0,
        deployed_machines: int = 0,
        ready_machines: int = 0,
        error_machines: int = 0,
        other_machines: int = 0,
        last_seen: datetime | None = None,
    ) -> SiteData:
        """Create SiteData for a Site."""
        [row] = await self.create(
            "site_data",
            [
                {
                    "site_id": site_id,
                    "allocated_machines": allocated_machines,
                    "deployed_machines": deployed_machines,
                    "ready_machines": ready_machines,
                    "error_machines": error_machines,
                    "other_machines": other_machines,
                    "last_seen": last_seen,
                }
            ],
        )
        total_machines = (
            allocated_machines
            + deployed_machines
            + ready_machines
            + error_machines
            + other_machines
        )
        return SiteData(total_machines=total_machines, **row)

    async def make_Config(self, name: str, value: Any = None) -> None:
        """Create an entry in the global configuration."""
        await self.create("config", {"name": name, "value": value})


@pytest.fixture
def factory(db_connection: AsyncConnection) -> Iterator[Factory]:
    yield Factory(db_connection)
