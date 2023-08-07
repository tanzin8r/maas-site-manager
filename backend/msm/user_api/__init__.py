from contextlib import asynccontextmanager
from logging import Logger
from pathlib import Path
from typing import (
    Any,
    AsyncGenerator,
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    CollectorRegistry,
    REGISTRY,
)
from sqlalchemy.ext.asyncio import AsyncConnection
import uvicorn
from uvicorn.server import logger

import msm

from .. import PACKAGE
from ..db import Database
from ..middleware import (
    DatabaseMetricsMiddleware,
    TransactionMiddleware,
)
from ..service import ConfigService
from ..settings import Settings
from ._prometheus import instrument_prometheus
from .handlers import API_ROUTERS


def run() -> None:
    """Run the API application."""
    settings = Settings()
    config: dict[str, Any]
    if settings.dev_mode:
        config = {
            "host": "0.0.0.0",
            "port": 8000,
            "reload": True,
            "reload_dirs": [str(Path(msm.__file__).parent)],
        }
    else:
        config = {"uds": settings.user_api_socket}
    uvicorn.run(
        "msm.user_api:create_app",
        factory=True,
        loop="uvloop",
        **config,
    )


def create_app(
    db: Database | None = None,
    transaction_middleware_class: type = TransactionMiddleware,
    prometheus_registry: CollectorRegistry = REGISTRY,
) -> FastAPI:
    """Create the FastAPI WSGI application."""
    settings = Settings()
    if not db:
        db = Database(settings.db_dsn)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        _log_settings(logger, settings)

        async def ensure_config(conn: AsyncConnection) -> None:
            service = ConfigService(conn)
            await service.ensure()

        await db.ensure_schema()
        await db.execute_in_transaction(ensure_config)
        yield
        await db.engine.dispose()

    app = FastAPI(
        title="MAAS Site Manager",
        name=PACKAGE.name,
        version=PACKAGE.version,
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

    for router in API_ROUTERS:
        app.include_router(router)

    instrument_prometheus(app, prometheus_registry)

    return app


def _log_settings(logger: Logger, settings: Settings) -> None:
    logger.info("Application settings:")
    for key, value in sorted(settings.model_dump().items()):
        logger.info(f"  {key}: {value}")
