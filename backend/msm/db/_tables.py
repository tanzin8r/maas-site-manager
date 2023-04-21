from uuid import uuid4

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import DateTime

METADATA = MetaData()

Site = Table(
    "site",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("city", Text),
    Column("country", Text),  # ISO 3166 Alpha2
    Column("latitude", Text),
    Column("longitude", Text),
    Column("name", Text, unique=True),
    Column("note", Text),
    Column("region", Text),
    Column("street", Text),
    Column("timezone", Text),
    Column("url", Text),
)


User = Table(
    "user",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("email", Text, unique=True, index=True),
    Column("full_name", Text),
    Column("password", Text),  # this is the hashed password
)


Token = Table(
    "token",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("site_id", Integer, ForeignKey("site.id"), index=True),
    Column(
        "value", UUID(as_uuid=True), nullable=False, index=True, default=uuid4
    ),
    Column("expired", DateTime, nullable=False),
    Column("created", DateTime, nullable=False),
)


SiteData = Table(
    "site_data",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column(
        "site_id", Integer, ForeignKey("site.id"), unique=True, nullable=False
    ),
    Column("allocated_machines", Integer),
    Column("deployed_machines", Integer),
    Column("ready_machines", Integer),
    Column("error_machines", Integer),
    Column("last_seen", DateTime),
)
