from collections.abc import Sequence
from typing import Annotated, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field, conint

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

M = TypeVar("M", bound=BaseModel)


class PaginatedResults(BaseModel, Generic[M]):
    """
    Base class to wrap objects in a pagination.
    Derived classes should overwrite the items property
    """

    total: Annotated[int, conint(ge=0)]
    page: Annotated[int, conint(ge=0)]
    size: Annotated[int, conint(ge=0, le=MAX_PAGE_SIZE)]
    items: Sequence[M]


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(Query(default=1, ge=1))
    size: int = Field(Query(default=DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE, ge=1))

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size
