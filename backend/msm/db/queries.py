from __future__ import annotations

from collections.abc import Iterable
from datetime import (
    datetime,
    timedelta,
)
from typing import (
    Any,
    Sequence,
    Type,
    TYPE_CHECKING,
    TypeVar,
)
from uuid import UUID

from sqlalchemy import (
    func,
    Row,
    select,
    Table,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .. import MAX_PAGE_SIZE
from ..schema import (
    Site as SiteSchema,
    Token as TokenSchema,
)
from ._tables import (
    Site,
    Token,
)

if TYPE_CHECKING:
    from sqlalchemy import Operators


def filters_from_arguments(
    table: Table,
    **kwargs: list[str] | None,
) -> Iterable[Operators]:
    """
    Yields clauses to join with AND and all entries for a single arg by OR.
    This enables to convert query params such as

      ?name=name1&name=name2&city=city

    to a where clause such as

      (name ilike %name1% OR name ilike %name2%) AND city ilike %city%

    :param table: the table to create the WHERE clause for
    :param kwargs: the parameters matching the table's column name
                   as keys and lists of strings that will be matched
                   via ilike
    :returns: a generator yielding where clause that joins all queries
              per column with OR and all columns with AND
    """
    for dimension, needles in kwargs.items():
        column = table.c[dimension]

        match needles:
            case [needle]:
                # If there's only one we don't need any ORs
                yield column.icontains(needle, autoescape=True)
            case [needle, *other_needles]:
                # More than one thing to match against, join them with OR
                clause = column.icontains(needle, autoescape=True) | False
                for needle in other_needles:
                    clause |= column.icontains(needle, autoescape=True)
                yield clause


DerivedSchema = TypeVar("DerivedSchema", SiteSchema, TokenSchema)


def extract_count_and_results(
    schema: Type[DerivedSchema],
    db_results: Sequence[Row[tuple[Any, Any, Any, Any, Any, Any]]],
) -> tuple[int, Iterable[DerivedSchema]]:
    """
    Extract the count and result from a paginated query using a window function
    """
    schema_objects = (schema(**row._asdict()) for row in db_results)
    count: int = 0
    try:
        count = db_results[0][0]
    except IndexError:
        count = 0
    return count, list(schema_objects)


async def get_filtered_sites(
    session: AsyncSession,
    offset: int = 0,
    limit: int = MAX_PAGE_SIZE,
    city: list[str] | None = [],
    country: list[str] | None = [],
    name: list[str] | None = [],
    note: list[str] | None = [],
    region: list[str] | None = [],
    street: list[str] | None = [],
    timezone: list[str] | None = [],
    url: list[str] | None = [],
) -> tuple[int, Iterable[SiteSchema]]:
    filters = filters_from_arguments(
        Site,
        city=city,
        country=country,
        name=name,
        note=note,
        region=region,
        street=street,
        timezone=timezone,
        url=url,
    )
    stmt = (
        select(
            # use a window function to get the count before limit
            # will be added as the first item of every results
            func.count().over(),  # type: ignore[no-untyped-call]
            Site.c.id,
            Site.c.name,
            Site.c.city,
            Site.c.country,
            Site.c.latitude,
            Site.c.longitude,
            Site.c.note,
            Site.c.region,
            Site.c.street,
            Site.c.timezone,
            Site.c.url,
        )
        .select_from(Site)
        .limit(limit)
        .offset(offset)
    )
    for clause in filters:
        stmt = stmt.where(clause)  # type: ignore[arg-type]

    result = await session.execute(stmt)
    return extract_count_and_results(SiteSchema, result.all())


async def get_tokens(
    session: AsyncSession,
    offset: int = 0,
    limit: int = MAX_PAGE_SIZE,
) -> tuple[int, Iterable[TokenSchema]]:
    result = await session.execute(
        select(
            func.count().over(),  # type: ignore[no-untyped-call]
            Token.c.id,
            Token.c.site_id,
            Token.c.value,
            Token.c.expired,
            Token.c.created,
        )
        .select_from(Token)
        .offset(offset)
        .limit(limit)
    )
    return extract_count_and_results(TokenSchema, result.all())


async def create_tokens(
    session: AsyncSession, duration: timedelta, count: int = 1
) -> tuple[datetime, list[UUID]]:
    created = datetime.utcnow()
    expired = created + duration
    result = await session.execute(
        Token.insert().returning(Token.c.value),
        [
            {
                "expired": expired,
                "created": created,
            }
            for _ in range(count)
        ],
    )
    return expired, [row[0] for row in result]
