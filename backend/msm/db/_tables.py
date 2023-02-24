from uuid import uuid4

from sqlalchemy import (
    Column,
    DECIMAL,
    ForeignKey,
    Integer,
    MetaData,
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
    Column("identifier", String(250), unique=True),
    Column("city", String(250)),
    Column("id", Integer, primary_key=True, index=True),
    # Decimal(8/6)/(9/6) = 16cm precision
    Column("latitude", DECIMAL(precision=8, scale=6)),
    Column("longitude", DECIMAL(precision=9, scale=6)),
    Column("name", String(250)),
    Column("note", Text),
    Column("region", String(250)),
    Column("street", String(250)),
    Column("timezone", String(3)),
    Column("url", String(2048)),
)


Token = Table(
    "token",
    METADATA,
    Column("id", Integer, primary_key=True, index=True),
    Column("site_id", Integer, ForeignKey("site.id"), index=True),
    Column(
        "value", UUID(as_uuid=True), nullable=False, index=True, default=uuid4
    ),
    Column("expiration", DateTime, nullable=False),
)

SiteData = Table(
    "site_data",
    METADATA,
    Column("id", Integer, primary_key=True, index=True),
    Column(
        "site_id", Integer, ForeignKey("site.id"), index=True, nullable=False
    ),
    Column("total_machines", Integer),
    Column("occupied_machines", Integer),
    Column("ready_machines", Integer),
    Column("error_machines", Integer),
    Column("last_seen", DateTime),
)
