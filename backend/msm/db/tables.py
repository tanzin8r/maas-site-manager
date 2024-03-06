from collections.abc import Callable
from typing import (
    Any,
)
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
from sqlalchemy.types import DateTime

from msm.db.types import Point
from msm.time import now_utc

METADATA = MetaData()


# Internal configuration options that are shared by units of the service
# installation
Config = Table(
    "config",
    METADATA,
    Column("name", Text, primary_key=True),
    Column("value", JSONB, nullable=False),
)

# Global application settings that can be configured through the API
Setting = Table(
    "setting",
    METADATA,
    Column("name", Text, primary_key=True),
    Column("value", JSONB, nullable=False),
)


Site = Table(
    "site",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("name", Text, nullable=False, index=True, default=""),
    Column("address", Text, nullable=False, default=""),
    Column("city", Text, nullable=False, default=""),
    Column("country", Text, nullable=False, default=""),  # ISO 3166 Alpha2
    Column("coordinates", Point),
    Column("note", Text, nullable=False, default=""),
    Column("postal_code", Text, nullable=False, default=""),
    Column("state", Text, nullable=False, default=""),
    Column("timezone", Text, nullable=False, default=""),
    Column("url", Text, nullable=False, default=""),
    Column("accepted", Boolean, nullable=False, default=False, index=True),
    Column(
        "created", DateTime(timezone=True), nullable=False, default=now_utc
    ),
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
    Column("expired", DateTime(timezone=True), nullable=False),
    Column(
        "created", DateTime(timezone=True), nullable=False, default=now_utc
    ),
)


SiteData = Table(
    "site_data",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column(
        "site_id",
        Integer,
        ForeignKey("site.id", onupdate="CASCADE", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    ),
    Column("machines_allocated", Integer, nullable=False, default=0),
    Column("machines_deployed", Integer, nullable=False, default=0),
    Column("machines_ready", Integer, nullable=False, default=0),
    Column("machines_error", Integer, nullable=False, default=0),
    Column("machines_other", Integer, nullable=False, default=0),
    Column("last_seen", DateTime(timezone=True)),
)
