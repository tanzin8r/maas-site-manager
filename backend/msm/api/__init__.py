from collections.abc import AsyncGenerator
from contextlib import (
    aclosing,
    asynccontextmanager,
)
from logging import Logger
from pathlib import Path
from typing import (
    Any,
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
)
from sqlalchemy.ext.asyncio import AsyncConnection
import uvicorn
from uvicorn.server import logger

import msm

from .. import __version__
from ..db import (
    Database,
    check_server_version,
)
from ..middleware import (
    DatabaseMetricsMiddleware,
    TransactionMiddleware,
)
from ..service import (
    ConfigService,
    SettingsService,
)
from ..settings import Settings
from ._prometheus import instrument_prometheus
from ._utils import create_subapp
from .site.handlers import ROUTERS as SITE_API_ROUTERS
from .user.handlers import ROUTERS as USER_API_ROUTERS


def run() -> None:
    """Run the API application."""
    settings = Settings()
    config: dict[str, Any]
    if settings.dev_mode:
        config = {
            "host": "0.0.0.0",
            "port": settings.api_port,
            "reload": True,
            "reload_dirs": [str(Path(msm.__file__).parent)],
        }
    else:
        config = {"uds": settings.api_socket}
    uvicorn.run(
        "msm.api:create_app",
        factory=True,
        loop="uvloop",
        **config,
    )


def create_app(
    db: Database | None = None,
    transaction_middleware_class: type = TransactionMiddleware,
    prometheus_registry: CollectorRegistry = REGISTRY,
) -> FastAPI:
    """Create the API (FastAPI) ASGI application."""
    settings = Settings()
    if not db:
        db = Database(settings.db_dsn)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        _log_settings(logger, settings)

        async with aclosing(db):
            await db.execute_in_transaction(check_server_version)
            await db.ensure_schema()
            await db.execute_in_transaction(ensure_db_entries)
            yield

    app = FastAPI(
        title="MAAS Site Manager",
        name="msm",
        version=__version__,
        lifespan=lifespan,
    )
    if settings.dev_mode:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.add_middleware(DatabaseMetricsMiddleware, db=db)
    app.add_middleware(transaction_middleware_class, db=db)

    app.mount("/api", create_subapp("User API", "api", USER_API_ROUTERS))
    app.mount("/site", create_subapp("Site API", "site", SITE_API_ROUTERS))

    instrument_prometheus(app, prometheus_registry)

    return app


async def ensure_db_entries(conn: AsyncConnection) -> None:
    """Ensure global database entries are populated."""
    await ConfigService(conn).ensure()
    await SettingsService(conn).ensure()


def _log_settings(logger: Logger, settings: Settings) -> None:
    logger.info("Application settings:")
    for key, value in sorted(settings.model_dump().items()):
        logger.info(f"  {key}: {value}")
