from datetime import (
    datetime,
    timedelta,
)
from uuid import UUID

from pydantic import BaseModel


class Site(BaseModel):
    id: int
    name: str
    last_checkin: datetime | None


class CreateTokensRequest(BaseModel):
    count: int = 1
    duration: timedelta


class CreateTokensResponse(BaseModel):
    expiration: datetime
    tokens: list[UUID]
