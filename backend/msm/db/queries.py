from __future__ import annotations

from collections.abc import Iterable
from datetime import (
    datetime,
    timedelta,
)
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    select,
    Table,
)
from sqlalchemy.ext.asyncio import AsyncSession

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


async def get_filtered_sites(
    session: AsyncSession,
    city: list[str] | None = [],
    name: list[str] | None = [],
    note: list[str] | None = [],
    region: list[str] | None = [],
    street: list[str] | None = [],
    timezone: list[str] | None = [],
    url: list[str] | None = [],
) -> Iterable[SiteSchema]:
    filters = filters_from_arguments(
        Site,
        city=city,
        name=name,
        note=note,
        region=region,
        street=street,
        timezone=timezone,
        url=url,
    )
    stmt = select(
        Site.c.id,
        Site.c.name,
        Site.c.identifier,
        Site.c.city,
        Site.c.latitude,
        Site.c.longitude,
        Site.c.note,
        Site.c.region,
        Site.c.street,
        Site.c.timezone,
        Site.c.url,
    )
    for clause in filters:
        stmt = stmt.where(clause)  # type: ignore
    result = await session.execute(stmt)
    return (SiteSchema(**row._asdict()) for row in result.all())


async def get_sites(session: AsyncSession) -> Iterable[SiteSchema]:
    stmt = select(
        Site.c.id,
        Site.c.name,
        Site.c.identifier,
        Site.c.city,
        Site.c.latitude,
        Site.c.longitude,
        Site.c.note,
        Site.c.region,
        Site.c.street,
        Site.c.timezone,
        Site.c.url,
    )
    result = await session.execute(stmt)
    return (SiteSchema(**row._asdict()) for row in result.all())


async def get_tokens(session: AsyncSession) -> Iterable[TokenSchema]:
    result = await session.execute(
        select(Token.c.id, Token.c.site_id, Token.c.value, Token.c.expiration)
    )
    return (TokenSchema(**row._asdict()) for row in result.all())


async def create_tokens(
    session: AsyncSession, duration: timedelta, count: int = 1
) -> tuple[datetime, list[UUID]]:
    expiration = datetime.utcnow() + duration
    result = await session.execute(
        Token.insert().returning(Token.c.value),
        [
            {
                "expiration": expiration,
            }
            for _ in range(count)
        ],
    )
    return expiration, [row[0] for row in result]
