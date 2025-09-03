from collections.abc import Iterable
from os.path import join

import boto3
from prometheus_client import CollectorRegistry
from sqlalchemy.ext.asyncio import AsyncConnection

from msm.service.base import Service
from msm.service.config import ConfigService
from msm.service.images import (
    BootAssetItemService,
    BootAssetService,
    BootAssetVersionService,
    BootSourceSelectionService,
    BootSourceService,
    IndexNotFound,
    IndexService,
)
from msm.service.settings import SettingsService
from msm.service.site import InvalidPendingSites, SiteService
from msm.service.token import TokenService
from msm.service.user import UserService


class ServiceCollection:
    """Provide all services."""

    def __init__(self, connection: AsyncConnection):
        self.sites = SiteService(connection)
        self.tokens = TokenService(connection)
        self.users = UserService(connection)
        self.settings = SettingsService(connection)
        self.boot_assets = BootAssetService(connection)
        self.boot_asset_items = BootAssetItemService(connection)
        self.boot_asset_versions = BootAssetVersionService(connection)
        self.boot_sources = BootSourceService(connection)
        self.boot_source_selections = BootSourceSelectionService(connection)
        self.index_service = IndexService(connection)

    @property
    def services(self) -> Iterable[Service]:
        """Service collection."""
        return [
            self.sites,
            self.tokens,
            self.users,
            self.settings,
            self.boot_assets,
            self.boot_asset_items,
            self.boot_asset_versions,
            self.boot_sources,
            self.boot_source_selections,
            self.index_service,
        ]

    @classmethod
    def register_metrics(cls, registry: CollectorRegistry) -> None:
        """Add metrics to registry."""
        Service.register_metrics(registry)

    async def collect_metrics(self) -> None:
        """Update metrics for this service."""
        for svc in self.services:
            await svc.collect_metrics()

    async def purge_source(self, id: int) -> None:
        _, assets = await self.boot_assets.get([], boot_source_id=[id])
        for asset in assets:
            _, versions = await self.boot_asset_versions.get(
                [], boot_asset_id=[asset.id]
            )
            for version in versions:
                await self.boot_asset_items.delete_by_version_id(version.id)
            await self.boot_asset_versions.delete_by_asset_id(asset.id)
        await self.boot_assets.delete_by_source_id(id)
        await self.boot_source_selections.delete_by_source_id(id)
        await self.boot_sources.delete(id)

    async def delete_item_and_purge(self, id: int) -> None:
        version_id = await self.boot_asset_items.delete(id)
        item_count = await self.boot_asset_items.row_count(
            boot_asset_version_id=[version_id]
        )
        if item_count:
            return
        asset_id = await self.boot_asset_versions.delete(version_id)
        version_count = await self.boot_asset_versions.row_count(
            boot_asset_id=[asset_id]
        )
        if version_count:
            return
        await self.boot_assets.delete(asset_id)

    async def purge_assets(
        self,
        asset_ids: list[int],
        s3_endpoint: str,
        s3_bucket: str,
        s3_path: str,
        s3_access_key: str,
        s3_secret_key: str,
    ) -> None:
        s3_client = boto3.client(
            "s3",
            use_ssl=False,
            verify=False,
            endpoint_url=s3_endpoint,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key,
        )
        for id in asset_ids:
            if asset := await self.boot_assets.get_by_id(id):
                _, versions = await self.boot_asset_versions.get(
                    [], boot_asset_id=[asset.id]
                )
                for version in versions:
                    _, items = await self.boot_asset_items.get(
                        [], boot_asset_version_id=[version.id]
                    )
                    for item in items:
                        s3_client.delete_object(
                            Bucket=s3_bucket, Key=join(s3_path, str(item.id))
                        )
                    await self.boot_asset_items.delete_by_version_id(
                        version.id
                    )
                await self.boot_asset_versions.delete_by_asset_id(asset.id)
                await self.boot_assets.delete(asset.id)
        await self.index_service.refresh()


__all__ = [
    "BootAssetItemService",
    "BootAssetService",
    "BootAssetVersionService",
    "BootSourceSelectionService",
    "BootSourceService",
    "ConfigService",
    "IndexNotFound",
    "IndexService",
    "InvalidPendingSites",
    "ServiceCollection",
    "SettingsService",
    "SiteService",
    "TokenService",
    "UserService",
]
