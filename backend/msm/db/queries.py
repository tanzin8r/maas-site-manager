from collections.abc import Iterable
from datetime import (
    datetime,
    timedelta,
)
from functools import reduce
from operator import or_
from typing import Any
from uuid import UUID

# from passlib.context import CryptContext
from sqlalchemy import (
    case,
    ColumnOperators,
    func,
    select,
    String,
    Table,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..schema import (
    MAX_PAGE_SIZE,
    Site as SiteSchema,
    Token as TokenSchema,
    UserWithPassword as UserPWSchema,
)
from ._tables import (
    Site,
    SiteData,
    Token,
    User,
)


async def get_user(session: AsyncSession, email: str) -> UserPWSchema | None:
    """
    Gets a user by its unique identifier: their email
    """
    stmt = (
        select(
            User.c.id,
            User.c.email,
            User.c.full_name,
            User.c.password,
        )
        .select_from(User)
        .where(User.c.email == email)
    )
    if result := await session.execute(stmt):
        if user := result.one_or_none():
            return UserPWSchema(**user._asdict())
    return None


def filters_from_arguments(
    table: Table,
    **filter_args: list[Any] | None,
) -> list[ColumnOperators]:
    """Return clauses to join with AND and all entries for a single arg by OR.
    This enables to convert query params such as

      ?name=name1&name=name2&city=city

    to a where clause such as

      (name ilike %name1% OR name ilike %name2%) AND city ilike %city%

    :param table: the table to create the WHERE clause for
    :param filter_args: the parameters matching the table's column name
                        as keys and lists of strings that will be matched
    :returns: a list with clauses to filter table values, which are meant to be
              used in AND. Clauses for each column are joined with OR.

    Matching is performed using `ilike` for text-based fields, exact match
    otherwise.

    """

    def compare_expr(name: str, value: Any) -> ColumnOperators:
        column = table.c[name]
        if isinstance(column.type, (Text, String)):
            return column.icontains(value, autoescape=True)
        else:
            return column.__eq__(value)

    return [
        reduce(
            or_,
            (compare_expr(name, value) for value in values),
        )
        for name, values in filter_args.items()
        if values
    ]


async def get_filtered_sites(
    session: AsyncSession,
    offset: int = 0,
    limit: int = MAX_PAGE_SIZE,
    city: list[str] | None = None,
    country: list[str] | None = None,
    name: list[str] | None = None,
    note: list[str] | None = None,
    region: list[str] | None = None,
    street: list[str] | None = None,
    timezone: list[str] | None = None,
    url: list[str] | None = None,
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
    count = (
        await session.execute(
            select(func.count())
            .select_from(Site)
            .where(*filters)  # type: ignore[arg-type]
        )
    ).scalar() or 0
    stmt = (
        select(
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
            case(
                (
                    SiteData.c.site_id != None,  # noqa: E711
                    func.json_build_object(
                        "allocated_machines",
                        SiteData.c.allocated_machines,
                        "deployed_machines",
                        SiteData.c.deployed_machines,
                        "ready_machines",
                        SiteData.c.ready_machines,
                        "error_machines",
                        SiteData.c.error_machines,
                        "last_seen",
                        SiteData.c.last_seen,
                    ),
                ),
                else_=None,
            ).label("stats"),
        )
        .select_from(
            Site.join(SiteData, SiteData.c.site_id == Site.c.id, isouter=True)
        )
        .where(*filters)  # type: ignore[arg-type]
        .order_by(Site.c.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return count, [SiteSchema(**row._asdict()) for row in result.all()]


async def get_tokens(
    session: AsyncSession,
    offset: int = 0,
    limit: int = MAX_PAGE_SIZE,
) -> tuple[int, Iterable[TokenSchema]]:
    count = (
        await session.execute(select(func.count()).select_from(Token))
    ).scalar() or 0
    result = await session.execute(
        select(
            Token.c.id,
            Token.c.site_id,
            Token.c.value,
            Token.c.expired,
            Token.c.created,
        )
        .select_from(Token)
        .order_by(Token.c.id)
        .offset(offset)
        .limit(limit)
    )
    return count, [TokenSchema(**row._asdict()) for row in result.all()]


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
