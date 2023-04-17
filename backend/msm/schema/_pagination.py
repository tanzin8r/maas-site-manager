from collections.abc import Sequence
from typing import NamedTuple

from fastapi import Query
from pydantic import (
    BaseModel,
    Field,
)

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PaginatedResults(BaseModel):
    """
    Base class to wrap objects in a pagination.
    Derived classes should overwrite the items property
    """

    total: int = Field(min=0)
    page: int = Field(min=0)
    size: int = Field(min=0, max=MAX_PAGE_SIZE)
    items: Sequence[BaseModel]


class PaginationParams(NamedTuple):
    """Pagination parameters."""

    page: int
    size: int
    offset: int


async def pagination_params(
    page: int = Query(default=1, gte=1),
    size: int = Query(default=DEFAULT_PAGE_SIZE, lte=MAX_PAGE_SIZE, gte=1),
) -> PaginationParams:
    """Return pagination parameters."""
    return PaginationParams(page=page, size=size, offset=(page - 1) * size)
