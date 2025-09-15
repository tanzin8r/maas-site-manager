from collections.abc import Iterable

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
from msm.service.s3 import S3Service
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
        self.s3 = S3Service(connection)
        self.index_service = IndexService(connection)
        self.boot_asset_versions = BootAssetVersionService(connection)
        self.boot_asset_items = BootAssetItemService(connection)
        self.boot_assets = BootAssetService(
            connection,
            s3=self.s3,
            boot_asset_versions=self.boot_asset_versions,
            boot_asset_items=self.boot_asset_items,
            index_service=self.index_service,
        )
        self.boot_source_selections = BootSourceSelectionService(connection)
        self.boot_sources = BootSourceService(
            connection,
            boot_assets=self.boot_assets,
            boot_source_selections=self.boot_source_selections,
            settings=self.settings,
        )

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
    "S3Service",
    "ServiceCollection",
    "SettingsService",
    "SiteService",
    "TokenService",
    "UserService",
]
