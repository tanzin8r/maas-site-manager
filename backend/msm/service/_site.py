from datetime import (
    datetime,
    timedelta,
)
from typing import (
    Any,
    Iterable,
)

from sqlalchemy import (
    case,
    delete,
    func,
    select,
    Select,
    update,
)

from ..db import (
    models,
    queries,
)
from ..db.tables import (
    Site,
    SiteData,
)
from ..schema import SortParam
from ._base import Service

LOST_CONNECTION_THRESHOLD_SECONDS = 60


class InvalidPendingSites(Exception):
    """Raised when unknown pending site IDs are provided."""

    def __init__(self, ids: Iterable[int]):
        self.ids = sorted(ids)
        super().__init__("Unknown pending sites")


class SiteService(Service):
    async def get(
        self,
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
    ) -> tuple[int, Iterable[models.Site]]:
        """Return accepted sites, with optional filtering."""
        filters = queries.filters_from_arguments(
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
        order_by = queries.order_by_from_arguments(sort_params=sort_params)
        count = await queries.row_count(self.conn, Site, *filters)
        stmt = (
            self._select_statement()
            .where(*filters)  # type: ignore[arg-type]
            .order_by(*order_by)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.conn.execute(stmt)
        return count, self.objects_from_result(models.Site, result)

    async def get_by_id(self, id: int) -> models.Site | None:
        """Gets a Site by id."""
        stmt = self._select_statement().where(Site.c.id == id)
        if result := await self.conn.execute(stmt):
            if site := result.one_or_none():
                return models.Site(**site._asdict())
        return None

    async def get_pending(
        self,
        offset: int = 0,
        limit: int | None = None,
    ) -> tuple[int, Iterable[models.PendingSite]]:
        """Return pending sites."""
        filters = [Site.c.accepted == False]  # noqa
        count = await queries.row_count(self.conn, Site, *filters)
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
        result = await self.conn.execute(stmt)
        return count, self.objects_from_result(models.PendingSite, result)

    async def get_coordinates(self) -> Iterable[models.SiteCoordinates]:
        """Return coordinates for all sites."""
        stmt = (
            select(
                Site.c.id,
                Site.c.latitude,
                Site.c.longitude,
            )
            .select_from(Site)
            .where(Site.c.accepted == True)  # noqa
        )
        result = await self.conn.execute(stmt)
        return self.objects_from_result(models.SiteCoordinates, result)

    async def accept_reject_pending(
        self,
        ids: list[int],
        accept: bool,
    ) -> None:
        """Accept or reject pending sites."""
        site_ids = set(ids)
        stmt = (
            select(Site.c.id)
            .select_from(Site)
            .where(
                Site.c.id.in_(site_ids),
                Site.c.accepted == False,  # noqa
            )
        )
        result = await self.conn.execute(stmt)
        pending_ids = set(row[0] for row in result.all())
        if unknown_ids := site_ids - pending_ids:
            raise InvalidPendingSites(unknown_ids)

        if accept:
            await self.conn.execute(
                update(Site)
                .where(Site.c.id.in_(site_ids))
                .values(accepted=True)
            )
        else:
            await self.conn.execute(
                delete(Site).where(Site.c.id.in_(site_ids))
            )
        return None

    def _select_statement(self) -> Select[Any]:
        connection_lost_timedelta = datetime.utcnow() - timedelta(
            seconds=LOST_CONNECTION_THRESHOLD_SECONDS
        )
        return select(
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
        ).select_from(
            Site.join(SiteData, SiteData.c.site_id == Site.c.id, isouter=True)
        )
