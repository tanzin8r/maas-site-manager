from collections.abc import Iterable
from datetime import datetime
from typing import Any

from sqlalchemy import Select, and_, delete, insert, select, text, update
from sqlalchemy.exc import ProgrammingError

from msm.db import (
    models,
    queries,
)
from msm.db.tables import (
    BootAsset,
    BootAssetItem,
    BootAssetVersion,
    BootSource,
    BootSourceSelection,
)
from msm.schema import SortParam
from msm.service.base import Service
from msm.time import now_utc


class BootSourceService(Service):
    async def get(
        self,
        sort_params: list[SortParam],
        offset: int = 0,
        limit: int | None = None,
    ) -> tuple[int, Iterable[models.BootSource]]:
        order_by = queries.order_by_from_arguments(sort_params=sort_params)
        stmt = (
            self._select_statement(
                BootSource.c.id,
                BootSource.c.url,
                BootSource.c.keyring,
                BootSource.c.sync_interval,
                BootSource.c.priority,
                BootSource.c.name,
            )
            .order_by(*order_by)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.conn.execute(stmt)
        return result.rowcount, self.objects_from_result(
            models.BootSource, result
        )

    async def get_by_id(self, id: int) -> models.BootSource | None:
        stmt = self._select_statement(
            BootSource.c.id,
            BootSource.c.url,
            BootSource.c.keyring,
            BootSource.c.sync_interval,
            BootSource.c.priority,
            BootSource.c.name,
        ).where(BootSource.c.id == id)
        result = await self.conn.execute(stmt)
        if row := result.one_or_none():
            return models.BootSource(**row._asdict())
        return None

    async def update(
        self, boot_source_id: int, details: models.BootSourceUpdate
    ) -> models.BootSource:
        data = details.model_dump(exclude_none=True)
        stmt = (
            update(BootSource)
            .where(BootSource.c.id == boot_source_id)
            .values(data)
            .returning(
                BootSource.c.id,
                BootSource.c.url,
                BootSource.c.keyring,
                BootSource.c.sync_interval,
                BootSource.c.priority,
                BootSource.c.name,
            )
        )
        result = await self.conn.execute(stmt)
        return models.BootSource(**result.one()._asdict())

    async def create(
        self, details: models.BootSourceCreate
    ) -> models.BootSource:
        data = details.model_dump()
        stmt = insert(BootSource).returning(
            BootSource.c.id,
            BootSource.c.url,
            BootSource.c.keyring,
            BootSource.c.sync_interval,
            BootSource.c.priority,
            BootSource.c.name,
        )
        result = await self.conn.execute(
            stmt,
            [data],
        )
        boot_source = result.one()
        return models.BootSource(**boot_source._asdict())

    async def delete(self, boot_source_id: int) -> None:
        stmt = delete(BootSource).where(BootSource.c.id == boot_source_id)
        await self.conn.execute(stmt)

    def _select_statement(self, *columns: Any) -> Select[Any]:
        return select(*columns).select_from(BootSource)

    async def ensure_custom_boot_source(self, service_url: str) -> None:
        """
        Ensure that the custom image boot source is present in the database.
        """
        stmt = self._select_statement(
            BootSource.c.id,
            BootSource.c.url,
        ).where(BootSource.c.id == 1)
        result = await self.conn.execute(stmt)
        if result.one_or_none():
            # update the custom source url in case the MSM url has changed
            await self.update(1, models.BootSourceUpdate(url=service_url))
            return
        data = {
            "id": 1,
            "url": service_url,
            "keyring": "",
            "name": "MSM Custom Images",
            "sync_interval": 0,
            "priority": 1,
        }
        await self.conn.execute(insert(BootSource), [data])


class BootSourceSelectionService(Service):
    async def get(
        self,
        boot_source_id: int,
        sort_params: list[SortParam],
        offset: int = 0,
        limit: int | None = None,
    ) -> tuple[int, Iterable[models.BootSourceSelection]]:
        order_by = queries.order_by_from_arguments(sort_params=sort_params)
        stmt = (
            self._select_statement(
                BootSourceSelection.c.id,
                BootSourceSelection.c.boot_source_id,
                BootSourceSelection.c.label,
                BootSourceSelection.c.os,
                BootSourceSelection.c.release,
                BootSourceSelection.c.available,
                BootSourceSelection.c.selected,
            )
            .where(BootSourceSelection.c.boot_source_id == boot_source_id)
            .order_by(*order_by)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.conn.execute(stmt)
        return result.rowcount, self.objects_from_result(
            models.BootSourceSelection, result
        )

    async def update(
        self,
        boot_source_id: int,
        selection_id: int,
        details: models.BootSourceSelectionUpdate,
    ) -> models.BootSourceSelection:
        data = details.model_dump(exclude_none=True)
        stmt = (
            update(BootSourceSelection)
            .where(
                and_(
                    BootSourceSelection.c.id == selection_id,
                    BootSourceSelection.c.boot_source_id == boot_source_id,
                )
            )
            .values(data)
            .returning(
                BootSourceSelection.c.id,
                BootSourceSelection.c.boot_source_id,
                BootSourceSelection.c.label,
                BootSourceSelection.c.os,
                BootSourceSelection.c.release,
                BootSourceSelection.c.available,
                BootSourceSelection.c.selected,
            )
        )
        result = await self.conn.execute(stmt)
        return models.BootSourceSelection(**result.one()._asdict())

    async def create(
        self, details: models.BootSourceSelectionCreate
    ) -> models.BootSourceSelection:
        data = details.model_dump()
        stmt = insert(BootSourceSelection).returning(
            BootSourceSelection.c.id,
            BootSourceSelection.c.boot_source_id,
            BootSourceSelection.c.label,
            BootSourceSelection.c.os,
            BootSourceSelection.c.release,
            BootSourceSelection.c.available,
            BootSourceSelection.c.selected,
        )
        result = await self.conn.execute(
            stmt,
            [data],
        )
        return models.BootSourceSelection(**result.one()._asdict())

    async def delete(self, boot_source_id: int, selection_id: int) -> None:
        stmt = delete(BootSourceSelection).where(
            and_(
                BootSourceSelection.c.id == selection_id,
                BootSourceSelection.c.boot_source_id == boot_source_id,
            )
        )
        await self.conn.execute(stmt)

    def _select_statement(self, *columns: Any) -> Select[Any]:
        return select(*columns).select_from(BootSourceSelection)


class BootAssetService(Service):
    async def get(
        self,
        sort_params: list[SortParam],
        offset: int = 0,
        limit: int | None = None,
        boot_source_id: list[int] | None = None,
        kind: list[models.BootAssetKind] | None = None,
        label: list[models.BootAssetLabel] | None = None,
        os: list[str] | None = None,
        arch: list[str] | None = None,
        release: list[str | None] | None = None,
        bootloader_type: list[str | None] | None = None,
    ) -> tuple[int, Iterable[models.BootAsset]]:
        filters = queries.filters_from_arguments(
            BootAsset,
            boot_source_id=boot_source_id,
            kind=kind,
            label=label,
            os=os,
            arch=arch,
            release=release,
            bootloader_type=bootloader_type,
        )
        order_by = queries.order_by_from_arguments(sort_params=sort_params)
        count = await queries.row_count(self.conn, BootAsset, *filters)
        stmt = (
            self._select_statement(
                BootAsset.c.id,
                BootAsset.c.boot_source_id,
                BootAsset.c.kind,
                BootAsset.c.label,
                BootAsset.c.os,
                BootAsset.c.release,
                BootAsset.c.codename,
                BootAsset.c.title,
                BootAsset.c.arch,
                BootAsset.c.subarch,
                BootAsset.c.compatibility,
                BootAsset.c.flavor,
                BootAsset.c.base_image,
                BootAsset.c.bootloader_type,
                BootAsset.c.eol,
                BootAsset.c.esm_eol,
                BootAsset.c.signed,
            )
            .where(*filters)
            .order_by(*order_by)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.conn.execute(stmt)
        return count, self.objects_from_result(models.BootAsset, result)

    async def get_by_id(self, id: int) -> models.BootAsset | None:
        stmt = self._select_statement(
            BootAsset.c.id,
            BootAsset.c.boot_source_id,
            BootAsset.c.kind,
            BootAsset.c.label,
            BootAsset.c.os,
            BootAsset.c.release,
            BootAsset.c.codename,
            BootAsset.c.title,
            BootAsset.c.arch,
            BootAsset.c.subarch,
            BootAsset.c.compatibility,
            BootAsset.c.flavor,
            BootAsset.c.base_image,
            BootAsset.c.bootloader_type,
            BootAsset.c.eol,
            BootAsset.c.esm_eol,
            BootAsset.c.signed,
        ).where(BootAsset.c.id == id)
        result = await self.conn.execute(stmt)
        if row := result.one_or_none():
            return models.BootAsset(**row._asdict())
        return None

    async def create(
        self,
        details: models.BootAssetCreate,
    ) -> models.BootAsset:
        data = details.model_dump()
        stmt = insert(BootAsset).returning(
            BootAsset.c.id,
            BootAsset.c.boot_source_id,
            BootAsset.c.kind,
            BootAsset.c.label,
            BootAsset.c.os,
            BootAsset.c.release,
            BootAsset.c.codename,
            BootAsset.c.title,
            BootAsset.c.arch,
            BootAsset.c.subarch,
            BootAsset.c.compatibility,
            BootAsset.c.flavor,
            BootAsset.c.base_image,
            BootAsset.c.bootloader_type,
            BootAsset.c.eol,
            BootAsset.c.esm_eol,
            BootAsset.c.signed,
        )
        result = await self.conn.execute(stmt, [data])
        return models.BootAsset(**result.one()._asdict())

    async def update(
        self, id: int, details: models.BootAssetUpdate
    ) -> models.BootAsset:
        data = details.model_dump(exclude_none=True)
        stmt = (
            update(BootAsset)
            .where(BootAsset.c.id == id)
            .values(data)
            .returning(
                BootAsset.c.id,
                BootAsset.c.boot_source_id,
                BootAsset.c.kind,
                BootAsset.c.label,
                BootAsset.c.os,
                BootAsset.c.release,
                BootAsset.c.codename,
                BootAsset.c.title,
                BootAsset.c.arch,
                BootAsset.c.subarch,
                BootAsset.c.compatibility,
                BootAsset.c.flavor,
                BootAsset.c.base_image,
                BootAsset.c.bootloader_type,
                BootAsset.c.eol,
                BootAsset.c.esm_eol,
                BootAsset.c.signed,
            )
        )
        result = await self.conn.execute(stmt)
        return models.BootAsset(**result.one()._asdict())

    async def delete(self, boot_asset_id: int) -> None:
        stmt = delete(BootAsset).where(BootAsset.c.id == boot_asset_id)
        await self.conn.execute(stmt)

    async def get_or_create(
        self, asset: models.BootAssetCreate
    ) -> models.BootAsset:
        count, assets = await self.get(
            [],
            boot_source_id=[asset.boot_source_id],
            kind=[asset.kind],
            label=[asset.label],
            os=[asset.os],
            arch=[asset.arch],
            release=[asset.release],
        )
        if count == 0:
            return await self.create(asset)
        return next(assets)  # type: ignore

    def _select_statement(self, *columns: Any) -> Select[Any]:
        return select(*columns).select_from(BootAsset)


class BootAssetVersionService(Service):
    async def get(
        self,
        sort_params: list[SortParam],
        offset: int = 0,
        limit: int | None = None,
        boot_asset_id: list[int] | None = None,
        version: list[str] | None = None,
    ) -> tuple[int, Iterable[models.BootAssetVersion]]:
        filters = queries.filters_from_arguments(
            BootAssetVersion,
            boot_asset_id=boot_asset_id,
            version=version,
        )
        order_by = queries.order_by_from_arguments(sort_params=sort_params)
        count = await queries.row_count(self.conn, BootAssetVersion, *filters)
        stmt = (
            self._select_statement(
                BootAssetVersion.c.id,
                BootAssetVersion.c.boot_asset_id,
                BootAssetVersion.c.version,
            )
            .where(*filters)
            .order_by(*order_by)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.conn.execute(stmt)
        return count, self.objects_from_result(models.BootAssetVersion, result)

    async def get_by_id(self, id: int) -> models.BootAssetVersion | None:
        stmt = self._select_statement(
            BootAssetVersion.c.id,
            BootAssetVersion.c.boot_asset_id,
            BootAssetVersion.c.version,
        ).where(BootAssetVersion.c.id == id)
        result = await self.conn.execute(stmt)
        if row := result.one_or_none():
            return models.BootAssetVersion(**row._asdict())
        return None

    async def create(
        self,
        details: models.BootAssetVersionCreate,
    ) -> models.BootAssetVersion:
        data = details.model_dump()
        stmt = insert(BootAssetVersion).returning(
            BootAssetVersion.c.id,
            BootAssetVersion.c.boot_asset_id,
            BootAssetVersion.c.version,
        )
        result = await self.conn.execute(stmt, [data])
        return models.BootAssetVersion(**result.one()._asdict())

    async def create_next_revision(
        self, asset_id: int, date: datetime
    ) -> models.BootAssetVersion:
        date_str = date.strftime("%Y%m%d") + "."
        count, versions = await self.get(
            [],
            boot_asset_id=[asset_id],
            version=[date_str],
        )
        if count > 0:
            latest_rev = max([int(v.version.split(".")[1]) for v in versions])
            new_rev = latest_rev + 1
            return await self.create(
                models.BootAssetVersionCreate(
                    boot_asset_id=asset_id, version=f"{date_str}{new_rev}"
                )
            )
        return await self.create(
            models.BootAssetVersionCreate(
                boot_asset_id=asset_id, version=f"{date_str}1"
            )
        )

    async def delete(self, boot_asset_version_id: int) -> None:
        stmt = delete(BootAssetVersion).where(
            BootAssetVersion.c.id == boot_asset_version_id
        )
        await self.conn.execute(stmt)

    def _select_statement(self, *columns: Any) -> Select[Any]:
        return select(*columns).select_from(BootAssetVersion)


class BootAssetItemService(Service):
    async def get(
        self,
        sort_params: list[SortParam],
        offset: int = 0,
        limit: int | None = None,
        boot_asset_version_id: list[int] | None = None,
        ftype: list[models.ItemFileType] | None = None,
        sha256: list[str] | None = None,
        path: list[str] | None = None,
        file_size: list[int] | None = None,
    ) -> tuple[int, Iterable[models.BootAssetItem]]:
        filters = queries.filters_from_arguments(
            BootAssetItem,
            boot_asset_version_id=boot_asset_version_id,
            ftype=ftype,
            sha256=sha256,
            path=path,
            file_size=file_size,
        )
        order_by = queries.order_by_from_arguments(sort_params=sort_params)
        count = await queries.row_count(self.conn, BootAssetItem, *filters)
        stmt = (
            self._select_statement(
                BootAssetItem.c.id,
                BootAssetItem.c.boot_asset_version_id,
                BootAssetItem.c.ftype,
                BootAssetItem.c.sha256,
                BootAssetItem.c.path,
                BootAssetItem.c.file_size,
                BootAssetItem.c.source_package,
                BootAssetItem.c.source_version,
                BootAssetItem.c.source_release,
                BootAssetItem.c.bytes_synced,
            )
            .where(*filters)
            .order_by(*order_by)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.conn.execute(stmt)
        return count, self.objects_from_result(models.BootAssetItem, result)

    async def get_by_id(self, id: int) -> models.BootAssetItem | None:
        stmt = self._select_statement(
            BootAssetItem.c.id,
            BootAssetItem.c.boot_asset_version_id,
            BootAssetItem.c.ftype,
            BootAssetItem.c.sha256,
            BootAssetItem.c.path,
            BootAssetItem.c.file_size,
            BootAssetItem.c.source_package,
            BootAssetItem.c.source_version,
            BootAssetItem.c.source_release,
            BootAssetItem.c.bytes_synced,
        ).where(BootAssetItem.c.id == id)
        result = await self.conn.execute(stmt)
        if row := result.one_or_none():
            return models.BootAssetItem(**row._asdict())
        return None

    async def get_by_path(self, path: str) -> models.BootAssetItem | None:
        stmt = self._select_statement(
            BootAssetItem.c.id,
            BootAssetItem.c.boot_asset_version_id,
            BootAssetItem.c.ftype,
            BootAssetItem.c.sha256,
            BootAssetItem.c.path,
            BootAssetItem.c.file_size,
            BootAssetItem.c.source_package,
            BootAssetItem.c.source_version,
            BootAssetItem.c.source_release,
            BootAssetItem.c.bytes_synced,
        ).where(BootAssetItem.c.path == path)
        result = await self.conn.execute(stmt)
        if row := result.one_or_none():
            return models.BootAssetItem(**row._asdict())
        return None

    async def create(
        self,
        details: models.BootAssetItemCreate,
    ) -> models.BootAssetItem:
        data = details.model_dump()
        stmt = insert(BootAssetItem).returning(
            BootAssetItem.c.id,
            BootAssetItem.c.boot_asset_version_id,
            BootAssetItem.c.ftype,
            BootAssetItem.c.sha256,
            BootAssetItem.c.path,
            BootAssetItem.c.file_size,
            BootAssetItem.c.source_package,
            BootAssetItem.c.source_version,
            BootAssetItem.c.source_release,
            BootAssetItem.c.bytes_synced,
        )
        result = await self.conn.execute(stmt, [data])
        return models.BootAssetItem(**result.one()._asdict())

    async def create_temporary(
        self, boot_asset_version_id: int | None = None
    ) -> models.BootAssetItem:
        """Create a temporary BootAssetItem that is meant to be overwritten."""
        details = models.BootAssetItemCreate(
            boot_asset_version_id=boot_asset_version_id,
            ftype=models.ItemFileType.ROOT_TGZ,
            sha256="",
            path="",
            file_size=0,
        )
        return await self.create(details)

    async def update_bytes_synced(
        self,
        id: int,
        bytes_synced: int,
    ) -> None:
        stmt = (
            update(BootAssetItem)
            .where(BootAssetItem.c.id == id)
            .values({"bytes_synced": bytes_synced})
        )
        await self.conn.execute(stmt)

    async def update(
        self, id: int, details: models.BootAssetItemUpdate
    ) -> models.BootAssetItem:
        data = details.model_dump(exclude_none=True)
        stmt = (
            update(BootAssetItem)
            .where(BootAssetItem.c.id == id)
            .values(data)
            .returning(
                BootAssetItem.c.id,
                BootAssetItem.c.boot_asset_version_id,
                BootAssetItem.c.ftype,
                BootAssetItem.c.sha256,
                BootAssetItem.c.path,
                BootAssetItem.c.file_size,
                BootAssetItem.c.source_package,
                BootAssetItem.c.source_version,
                BootAssetItem.c.source_release,
                BootAssetItem.c.bytes_synced,
            )
        )
        result = await self.conn.execute(stmt)
        return models.BootAssetItem(**result.one()._asdict())

    async def delete(self, boot_asset_item_id: int) -> None:
        stmt = delete(BootAssetItem).where(
            BootAssetItem.c.id == boot_asset_item_id
        )
        await self.conn.execute(stmt)

    def _select_statement(self, *columns: Any) -> Select[Any]:
        return select(*columns).select_from(BootAssetItem)


class IndexNotFound(Exception):
    """Raised when a refresh or select was made on the index, but it doesn't exist."""


def reverse_fqdn(fqdn: str) -> str:
    sp = fqdn.split(".")
    sp.reverse()
    return ".".join(sp)


class IndexService(Service):
    _MATERIALIZED_VIEW = """CREATE MATERIALIZED VIEW IF NOT EXISTS images_index AS
SELECT DISTINCT ON (asset.boot_source_id, ver_item.ftype, ver_item.path)
    asset.id,
    asset.boot_source_id,
    asset.kind,
    asset.label,
    asset.os,
    asset.arch,
    asset.release,
    asset.codename,
    asset.title,
    asset.subarch,
    asset.compatibility,
    asset.flavor,
    asset.base_image,
    asset.bootloader_type,
    asset.eol,
    asset.esm_eol,
    asset.signed,
    ver_item.version,
    ver_item.ftype,
    ver_item.sha256,
    ver_item.path,
    ver_item.file_size,
    ver_item.bytes_synced,
    ver_item.source_package,
    ver_item.source_version,
    ver_item.source_release
FROM
    (
        SELECT DISTINCT ON (boot_asset.os, boot_asset.release, boot_asset.arch)
            source.priority,
            boot_asset.id,
            boot_asset.boot_source_id,
            boot_asset.kind,
            boot_asset.label,
            boot_asset.os,
            boot_asset.arch,
            boot_asset.release,
            boot_asset.codename,
            boot_asset.title,
            boot_asset.subarch,
            boot_asset.compatibility,
            boot_asset.flavor,
            boot_asset.base_image,
            boot_asset.bootloader_type,
            boot_asset.eol,
            boot_asset.esm_eol,
            boot_asset.signed
        FROM
            (
                boot_asset
                JOIN
                (
                    SELECT bs.id, bs.priority
                    FROM boot_source bs
                ) AS source
                ON boot_asset.boot_source_id = source.id
            )
        ORDER BY boot_asset.os, boot_asset.release, boot_asset.arch, source.priority DESC
    ) as asset
JOIN
    (
        (
            SELECT DISTINCT ON (v.boot_asset_id) v.id, v.version, v.boot_asset_id
            FROM boot_asset_version v
            ORDER BY v.boot_asset_id, v.version DESC
        ) AS ver
        JOIN boot_asset_item item
        ON ver.id = item.boot_asset_version_id
    ) as ver_item
ON ver_item.boot_asset_id = asset.id;"""

    _UNIQUE_INDEX = "CREATE UNIQUE INDEX IF NOT EXISTS image_item ON images_index (os, release, arch, path);"

    async def create(self) -> None:
        """
        Create the images_index materialized view if it doesn't already exist.
        """
        await self.conn.execute(text(self._MATERIALIZED_VIEW))
        await self.conn.execute(text(self._UNIQUE_INDEX))

    async def refresh(self) -> None:
        """
        Refresh the images_index materialized view.
        """
        stmt = text("REFRESH MATERIALIZED VIEW CONCURRENTLY images_index;")
        try:
            await self.conn.execute(stmt)
        except ProgrammingError:
            raise IndexNotFound()

    async def drop(self) -> None:
        """
        Remove the images_index materialized view.
        """
        stmt = text("DROP MATERIALIZED VIEW images_index;")
        try:
            await self.conn.execute(stmt)
        except ProgrammingError:
            raise IndexNotFound()

    async def get(
        self, index_type: models.IndexType, fqdn: str
    ) -> dict[str, Any]:
        """
        Get the specified index type.
        """
        stmt = text("SELECT * FROM images_index;")
        try:
            result = await self.conn.execute(stmt)
        except ProgrammingError:
            raise IndexNotFound()
        products = [models.IndexProduct(**x._asdict()) for x in result.all()]
        self._filter_for_fully_downloaded(products)
        if index_type == models.IndexType.INDEX:
            return self.generate_index_json(products, fqdn)
        return self.generate_download_json(products, fqdn)

    def _filter_for_fully_downloaded(
        self, products: list[models.IndexProduct]
    ) -> None:
        """
        Remove items from the list that are not part of a fully downloaded set.
        """
        download_status: dict[int, dict[str, Any]] = {}
        for i, p in enumerate(products):
            if download_status.get(p.id) is None:
                download_status[p.id] = {
                    "indeces": [i],
                    "downloaded": p.bytes_synced == p.file_size,
                }
            else:
                download_status[p.id]["downloaded"] &= (
                    p.bytes_synced == p.file_size
                )
                download_status[p.id]["indeces"].append(i)

        indeces_to_remove = []
        for dl in download_status.values():
            if not dl["downloaded"]:
                indeces_to_remove += dl["indeces"]
        indeces_to_remove.sort(reverse=True)
        for i in indeces_to_remove:
            products.pop(i)

    def generate_index_json(
        self, products: list[models.IndexProduct], fqdn: str
    ) -> dict[str, Any]:
        """
        Create the index json from the list of products in the materialized view.
        """
        reversed_fqdn = reverse_fqdn(fqdn)
        index_json: dict[str, Any] = {
            "format": "index:1.0",
            "index": {
                f"{reversed_fqdn}:stream:v1:download": {
                    "datatype": "image-ids",
                    "format": "products:1.0",
                    "path": f"streams/v1/{reversed_fqdn}:stream:v1:download.json",
                }
            },
        }
        product_keys = set()
        for product in products:
            if product.kind == models.BootAssetKind.BOOTLOADER:
                product_key = f"{reversed_fqdn}.stream:{product.os}:{product.bootloader_type}:{product.arch}"
            else:
                product_key = f"{reversed_fqdn}.stream:{product.os}:{product.release}:{product.arch}:{product.subarch}"
                if product.flavor:
                    product_key += f"-{product.flavor}"
            product_keys.add(product_key)
        now = now_utc().strftime("%a, %d %b %Y %H:%M:%S %z")
        index_json["updated"] = now
        index_json["index"][f"{reversed_fqdn}:stream:v1:download"][
            "updated"
        ] = now
        index_json["index"][f"{reversed_fqdn}:stream:v1:download"][
            "products"
        ] = sorted(product_keys)
        return index_json

    def generate_download_json(
        self, products: list[models.IndexProduct], fqdn: str
    ) -> dict[str, Any]:
        """
        Create the download json from the list of products in the materialized view.
        """
        reversed_fqdn = reverse_fqdn(fqdn)
        download_json: dict[str, Any] = {
            "content_id": f"{reversed_fqdn}:stream:v1:download",
            "datatype": "image-ids",
            "format": "products:1.0",
            "products": {},
        }
        for product in products:
            if product.kind == models.BootAssetKind.BOOTLOADER:
                product_key = f"{reversed_fqdn}.stream:{product.os}:{product.bootloader_type}:{product.arch}"
                item_json = {
                    "ftype": product.ftype.value,
                    "path": product.path,
                    "sha256": product.sha256,
                    "size": product.file_size,
                    "src_package": product.source_package,
                    "src_release": product.source_release,
                    "src_version": product.source_version,
                }
                item_key = product.source_package
            else:
                product_key = f"{reversed_fqdn}.stream:{product.os}:{product.release}:{product.arch}:{product.subarch}"
                if product.flavor:
                    product_key += f"-{product.flavor}"
                item_json = {
                    "ftype": product.ftype.value,
                    "path": product.path,
                    "sha256": product.sha256,
                    "size": product.file_size,
                }
                item_key = product.ftype.value
            if download_json["products"].get(product_key) is None:
                dl_prod = {
                    "arch": product.arch,
                    "kflavor": product.flavor,
                    "label": product.label.value,
                    "os": product.os,
                    "release": product.release,
                    "release_codename": product.codename,
                    "release_title": product.title,
                    "subarch": product.subarch,
                    "subarches": ",".join(product.compatibility)
                    if product.compatibility
                    else None,
                    "bootloader-type": product.bootloader_type,
                    "support_eol": product.eol.strftime("%Y-%m-%d")
                    if product.eol
                    else None,
                    "support_esm_eol": product.esm_eol.strftime("%Y-%m-%d")
                    if product.esm_eol
                    else None,
                    "versions": {
                        product.version: {"items": {item_key: item_json}}
                    },
                }
                download_json["products"][product_key] = {
                    k: v for k, v in dl_prod.items() if v is not None
                }
            else:
                download_json["products"][product_key]["versions"][
                    product.version
                ]["items"][item_key] = item_json
        download_json["updated"] = now_utc().strftime(
            "%a, %d %b %Y %H:%M:%S %z"
        )
        return download_json
