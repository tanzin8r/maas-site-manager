from typing import (
    Any,
    Iterable,
    TypeVar,
)

from pydantic import BaseModel
from sqlalchemy import CursorResult
from sqlalchemy.ext.asyncio import AsyncConnection

Model = TypeVar("Model", bound=BaseModel)


class Service:
    """Base class for services."""

    def __init__(self, connection: AsyncConnection):
        self.conn = connection

    def objects_from_result(
        self, model: type[Model], result: CursorResult[Any]
    ) -> Iterable[Model]:
        """Return an iterable of model instances from a query result."""
        return (model(**row._asdict()) for row in result.all())
