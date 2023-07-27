from typing import (
    Annotated,
    NamedTuple,
    Sequence,
)

from fastapi import Query
from pydantic import (
    BaseModel,
    conint,
)

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PaginatedResults(BaseModel):
    """
    Base class to wrap objects in a pagination.
    Derived classes should overwrite the items property
    """

    total: Annotated[int, conint(ge=0)]
    page: Annotated[int, conint(ge=0)]
    size: Annotated[int, conint(ge=0, le=MAX_PAGE_SIZE)]
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
