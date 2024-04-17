from collections.abc import Iterable
from datetime import (
    datetime,
    timedelta,
)
from typing import (
    Any,
)
from uuid import UUID

from sqlalchemy import (
    Select,
    case,
    delete,
    exists,
    func,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert

from msm.db import (
    models,
    queries,
)
from msm.db.tables import (
    Site,
    SiteData,
)
from msm.schema import SortParam
from msm.service._base import Service
from msm.settings import Settings
from msm.time import now_utc

LOST_CONNECTION_THRESHOLD = timedelta(seconds=60)


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
        state: list[str] | None = None,
        postal_code: list[str] | None = None,
        address: list[str] | None = None,
        timezone: list[str] | None = None,
        url: list[str] | None = None,
    ) -> tuple[int, Iterable[models.Site]]:
        """Return accepted sites, with optional filtering."""
        filters = queries.filters_from_arguments(
            Site,
            address=address,
            city=city,
            country=country,
            name=name,
            note=note,
            postal_code=postal_code,
            state=state,
            timezone=timezone,
            url=url,
        )
        filters.append(Site.c.accepted == True)
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
        """Get a site by id."""
        stmt = self._select_statement().where(Site.c.id == id)
        result = await self.conn.execute(stmt)
        if row := result.one_or_none():
            return models.Site(**row._asdict())
        return None

    async def get_by_auth_id(self, auth_id: UUID) -> models.Site | None:
        """Get a site by authentication ID."""
        stmt = self._select_statement().where(Site.c.auth_id == auth_id)
        result = await self.conn.execute(stmt)
        if row := result.one_or_none():
            return models.Site(**row._asdict())
        return None

    async def id_exists(self, id: int) -> bool:
        """Check if the given site exists"""
        stmt = select(exists(Site).where(Site.c.id == id))
        result = await self.conn.execute(stmt)
        return result.scalar() is True

    async def update(
        self, id: int, details: models.SiteUpdate | models.SiteDetailsUpdate
    ) -> None:
        """Update details about a site."""
        stmt = (
            update(Site)
            .where(Site.c.id == id)
            .values(details.model_dump(exclude_none=True))
        )
        await self.conn.execute(stmt)

    async def update_last_seen(self, id: int, last_seen: datetime) -> None:
        """Update when a site has been last seen."""
        stmt = (
            insert(SiteData)
            .values(site_id=id, last_seen=last_seen)
            .on_conflict_do_update(
                index_elements=[SiteData.c.site_id],
                set_={"last_seen": last_seen},
            )
        )
        await self.conn.execute(stmt)

    async def update_data(
        self, id: int, details: models.SiteDataUpdate
    ) -> None:
        """Update stats data for a site."""
        stmt = (
            update(SiteData)
            .where(SiteData.c.site_id == id)
            .values(details.model_dump())
        )
        await self.conn.execute(stmt)

    async def delete(self, id: int) -> None:
        """Deletes a site by ID."""
        stmt = delete(Site).where(Site.c.id == id)
        await self.conn.execute(stmt)

    async def create_pending(
        self, details: models.PendingSiteCreate
    ) -> models.PendingSite:
        """Create a pending site."""
        data = details.model_dump()
        stmt = insert(Site).returning(
            Site.c.id,
            Site.c.name,
            Site.c.url,
            Site.c.created,
            Site.c.auth_id,
        )
        result = await self.conn.execute(stmt, [data])
        pending_site = result.one()
        return models.PendingSite(**pending_site._asdict())

    async def get_pending(
        self,
        offset: int = 0,
        limit: int | None = None,
    ) -> tuple[int, Iterable[models.PendingSite]]:
        """Return pending sites."""
        filters = [Site.c.accepted == False]
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

    async def get_coordinates(
        self,
        city: list[str] | None = None,
        country: list[str] | None = None,
        name: list[str] | None = None,
        note: list[str] | None = None,
        state: list[str] | None = None,
        postal_code: list[str] | None = None,
        address: list[str] | None = None,
        timezone: list[str] | None = None,
        url: list[str] | None = None,
    ) -> Iterable[models.SiteCoordinates]:
        """Return coordinates for all sites, with optional filtering."""
        filters = queries.filters_from_arguments(
            Site,
            address=address,
            city=city,
            country=country,
            name=name,
            note=note,
            postal_code=postal_code,
            state=state,
            timezone=timezone,
            url=url,
        )
        filters.append(Site.c.accepted == True)
        stmt = (
            select(
                Site.c.id,
                Site.c.coordinates,
            )
            .select_from(Site)
            .where(*filters)  # type: ignore[arg-type]
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
                Site.c.accepted == False,
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

    async def get_enroling(self, auth_id: UUID) -> models.EnrolingSite | None:
        """Return details for a site in enrolment process, if found."""
        stmt = (
            select(
                Site.c.id,
                Site.c.accepted,
            )
            .select_from(Site)
            .where(Site.c.auth_id == auth_id)
        )
        result = await self.conn.execute(stmt)
        if row := result.one_or_none():
            return models.EnrolingSite(**row._asdict())
        return None

    async def get_heartbeat_interval(self) -> int:
        """The heartbeat interval, for sites to report to site manager"""
        return Settings().heartbeat_interval_seconds

    def _select_statement(self) -> Select[Any]:
        connection_lost_limit = now_utc() - LOST_CONNECTION_THRESHOLD
        return select(
            Site.c.id,
            Site.c.address,
            Site.c.city,
            Site.c.country,
            Site.c.coordinates,
            Site.c.name,
            Site.c.name.notin_(
                select(Site.c.name)
                .select_from(Site)
                .group_by(Site.c.name)
                .having(func.count(Site.c.name) > 1)
            ).label("name_unique"),
            Site.c.note,
            Site.c.postal_code,
            Site.c.state,
            Site.c.timezone,
            Site.c.url,
            case(
                (
                    SiteData.c.site_id == None,
                    models.ConnectionStatus.UNKNOWN,
                ),
                (
                    SiteData.c.last_seen > connection_lost_limit,
                    models.ConnectionStatus.STABLE,
                ),
                else_=models.ConnectionStatus.LOST,
            ).label("connection_status"),
            case(
                (
                    SiteData.c.site_id != None,
                    func.json_build_object(
                        "machines_total",
                        (
                            SiteData.c.machines_allocated
                            + SiteData.c.machines_deployed
                            + SiteData.c.machines_ready
                            + SiteData.c.machines_error
                            + SiteData.c.machines_other
                        ).label("machines_total"),
                        "machines_allocated",
                        SiteData.c.machines_allocated,
                        "machines_deployed",
                        SiteData.c.machines_deployed,
                        "machines_ready",
                        SiteData.c.machines_ready,
                        "machines_error",
                        SiteData.c.machines_error,
                        "machines_other",
                        SiteData.c.machines_other,
                        "last_seen",
                        SiteData.c.last_seen,
                    ),
                ),
                else_=None,
            ).label("stats"),
        ).select_from(
            Site.join(SiteData, SiteData.c.site_id == Site.c.id, isouter=True)
        )
