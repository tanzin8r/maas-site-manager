from datetime import (
    datetime,
    timedelta,
)
from typing import Iterable

from sqlalchemy import (
    case,
    delete,
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models
from ...schema import SortParam
from ...settings import SETTINGS
from .._tables import (
    Site,
    SiteData,
)
from ._count import row_count
from ._search import (
    filters_from_arguments,
    order_by_from_arguments,
)


class InvalidPendingSites(Exception):
    """Raised when unknown pending site IDs are provided."""

    def __init__(self, ids: Iterable[int]):
        self.ids = sorted(ids)
        super().__init__("Unknown pending sites")


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
) -> tuple[int, list[models.Site]]:
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
    order_by = order_by_from_arguments(sort_params=sort_params)
    count = await row_count(session, Site, *filters)
    connection_lost_timedelta = datetime.utcnow() - timedelta(
        seconds=SETTINGS.lost_connection_threshold_seconds
    )
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
                    SiteData.c.site_id == None,  # noqa: E711
                    models.ConnectionStatus.UNKNOWN,
                ),
                (
                    SiteData.c.last_seen > connection_lost_timedelta,
                    models.ConnectionStatus.STABLE,
                ),
                else_=models.ConnectionStatus.LOST,
            ).label("connection_status"),
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
    return count, [models.Site(**row._asdict()) for row in result.all()]


async def get_pending_sites(
    session: AsyncSession,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[int, list[models.PendingSite]]:
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
    return count, [models.PendingSite(**row._asdict()) for row in result.all()]


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
