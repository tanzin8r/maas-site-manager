from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID,
)
from sqlalchemy.types import (
    DateTime,
    UserDefinedType,
)

METADATA = MetaData()


class Point(UserDefinedType):  # type: ignore
    """
    The postgresql POINT
    https://www.postgresql.org/docs/current/datatype-geometric.html#DATATYPE-GEOMETRIC-POINTS
    """

    cache_ok = True

    def get_col_spec(self, **kw: Any) -> str:
        return "POINT"


Config = Table(
    "config",
    METADATA,
    Column("name", Text, primary_key=True),
    Column("value", JSONB, nullable=False),
)

Site = Table(
    "site",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("address", Text, nullable=False, default=""),
    Column("city", Text, nullable=False, default=""),
    Column("country", Text, nullable=False, default=""),  # ISO 3166 Alpha2
    Column("coordinates", Point),
    Column("name", Text, nullable=False, default=""),
    Column("name_unique", Boolean, nullable=False, default=True),
    Column("note", Text, nullable=False, default=""),
    Column("postal_code", Text, nullable=False, default=""),
    Column("state", Text, nullable=False, default=""),
    Column("timezone", Text, nullable=False, default=""),
    Column("url", Text, nullable=False, default=""),
    Column("accepted", Boolean, nullable=False, default=False, index=True),
    Column("created", DateTime, nullable=False, default=datetime.utcnow),
    Column(
        "auth_id",
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
    ),
)


User = Table(
    "user",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("email", Text, nullable=False, unique=True, index=True),
    Column("username", Text, nullable=False, unique=True, index=True),
    Column("full_name", Text, nullable=False, default=""),
    Column("password", Text, nullable=False),  # this is the hashed password
    Column("is_admin", Boolean, nullable=False, default=False),
    Column(
        "auth_id",
        UUID(as_uuid=True),
        nullable=False,
        default=uuid4,
        unique=True,
        index=True,
    ),
)


Token = Table(
    "token",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("value", Text, nullable=False),
    Column(
        "auth_id",
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
    ),
    Column("expired", DateTime, nullable=False),
    Column("created", DateTime, nullable=False, default=datetime.utcnow),
)


SiteData = Table(
    "site_data",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column(
        "site_id", Integer, ForeignKey("site.id"), unique=True, nullable=False
    ),
    Column("allocated_machines", Integer, nullable=False, default=0),
    Column("deployed_machines", Integer, nullable=False, default=0),
    Column("ready_machines", Integer, nullable=False, default=0),
    Column("error_machines", Integer, nullable=False, default=0),
    Column("other_machines", Integer, nullable=False, default=0),
    Column("last_seen", DateTime),
)
