from uuid import uuid4

from sqlalchemy import (
    Column,
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
    Column("id", Integer, primary_key=True, index=True),
    Column("name", Text, nullable=False, unique=True),
    Column("last_checkin", DateTime),
)

Token = Table(
    "token",
    METADATA,
    Column("id", Integer, primary_key=True, index=True),
    Column(
        "value", UUID(as_uuid=True), nullable=False, index=True, default=uuid4
    ),
    Column("expiration", DateTime, nullable=False),
)
