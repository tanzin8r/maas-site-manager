from collections.abc import Iterable
from datetime import (
    datetime,
    timedelta,
)
from functools import reduce
from operator import or_
from typing import Any
from uuid import UUID

from sqlalchemy import (
    asc,
    case,
    ColumnOperators,
    delete,
    desc,
    func,
    select,
    String,
    Table,
    Text,
    UnaryExpression,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import FromClause

from ..schema import SortParam
from ._tables import (
    Site,
    SiteData,
    Token,
    User,
)
from .models import (
    PendingSite as PendingSiteSchema,
    Site as SiteSchema,
    Token as TokenSchema,
    UserWithPassword as UserWithPasswordSchema,
)


class InvalidPendingSites(Exception):
    """Raised when unknown pending site IDs are provided."""

    def __init__(self, ids: Iterable[int]):
        self.ids = sorted(ids)
        super().__init__("Unknown pending sites")


async def row_count(
    session: AsyncSession, what: FromClause, *filters: ColumnOperators
) -> int:
    """Count specified entries."""
    stmt = (
        select(func.count())
        .select_from(what)
        .where(*filters)  # type: ignore[arg-type]
    )
    return (await session.execute(stmt)).scalar() or 0


async def get_user(
    session: AsyncSession, email: str
) -> UserWithPasswordSchema | None:
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
            return UserWithPasswordSchema(**user._asdict())
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


def order_by_from_arguments(
    table: Table, sort_params: list[SortParam]
) -> list[UnaryExpression[Any]]:
    return [
        asc(table.c[param.field]) if param.asc else desc(table.c[param.field])
        for param in sort_params
    ]


async def get_sites(
    session: AsyncSession,
    sort_params: list[SortParam],
    offset: int = 0,
    limit: int | None = None,
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
    filters.append(Site.c.accepted == True)  # noqa
    order_by = order_by_from_arguments(table=Site, sort_params=sort_params)
    count = await row_count(session, Site, *filters)
    stmt = (
        select(
            Site.c.id,
            Site.c.name,
            Site.c.name_unique,
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
                        "total_machines",
                        (
                            SiteData.c.allocated_machines
                            + SiteData.c.deployed_machines
                            + SiteData.c.ready_machines
                            + SiteData.c.error_machines
                            + SiteData.c.other_machines
                        ).label("total_machines"),
                        "allocated_machines",
                        SiteData.c.allocated_machines,
                        "deployed_machines",
                        SiteData.c.deployed_machines,
                        "ready_machines",
                        SiteData.c.ready_machines,
                        "error_machines",
                        SiteData.c.error_machines,
                        "other_machines",
                        SiteData.c.other_machines,
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
        .order_by(*order_by)
        .offset(offset)
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return count, [SiteSchema(**row._asdict()) for row in result.all()]


async def get_pending_sites(
    session: AsyncSession,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[int, Iterable[PendingSiteSchema]]:
    filters = [Site.c.accepted == False]  # noqa
    count = await row_count(session, Site, *filters)
    stmt = (
        select(
            Site.c.id,
            Site.c.name,
            Site.c.url,
            Site.c.created,
        )
        .select_from(Site)
        .where(*filters)
        .order_by(Site.c.id)
        .offset(offset)
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return count, [PendingSiteSchema(**row._asdict()) for row in result.all()]


async def accept_reject_pending_sites(
    session: AsyncSession,
    ids: list[int],
    accept: bool,
) -> None:
    site_ids = set(ids)
    stmt = (
        select(Site.c.id)
        .select_from(Site)
        .where(
            Site.c.id.in_(site_ids),
            Site.c.accepted == False,  # noqa
        )
    )
    result = await session.execute(stmt)
    pending_ids = set(row[0] for row in result.all())
    if unknown_ids := site_ids - pending_ids:
        raise InvalidPendingSites(unknown_ids)

    if accept:
        await session.execute(
            update(Site).where(Site.c.id.in_(site_ids)).values(accepted=True)
        )
    else:
        await session.execute(delete(Site).where(Site.c.id.in_(site_ids)))
    return None


async def get_tokens(
    session: AsyncSession,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[int, Iterable[TokenSchema]]:
    count = await row_count(session, Token)
    stmt = (
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
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
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
