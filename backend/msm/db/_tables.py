from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
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
    Column("city", String(250)),
    # ISO 3166 Alpha2
    Column("country", String(2)),
    # Decimal(8/6)/(9/6) = 16cm precision
    Column("latitude", Numeric(precision=8, scale=6)),
    Column("longitude", Numeric(precision=9, scale=6)),
    Column("name", String(250), unique=True),
    Column("note", Text),
    Column("region", String(250)),
    Column("street", String(250)),
    # Timezones need be up to x.25 accuracy
    Column("timezone", Numeric(precision=3, scale=2)),
    Column("url", String(2048)),
)


User = Table(
    "user",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("email", String(250), unique=True, index=True),
    Column("full_name", String(250)),
    # this is the hashed password
    Column("password", String(100)),
    Column("disabled", Boolean),
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
