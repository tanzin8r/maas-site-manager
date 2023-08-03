import argparse
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    CollectorRegistry,
    REGISTRY,
)
import uvicorn

import msm

from .. import PACKAGE
from ..db import Database
from ..middleware import (
    DatabaseMetricsMiddleware,
    TransactionMiddleware,
)
from ..settings import Settings
from ._prometheus import instrument_prometheus
from .handlers import API_ROUTERS


def run() -> None:
    """Run the API application."""
    args = _get_args()
    if args.devmode:
        reload_dirs = [str(Path(msm.__file__).parent)]
        host = "0.0.0.0"
    else:
        reload_dirs = None
        host = "127.0.0.1"
    uvicorn.run(
        "msm.user_api:create_app",
        factory=True,
        host=host,
        port=args.port,
        loop="uvloop",
        reload=args.devmode,
        reload_dirs=reload_dirs,
    )


def create_app(
    database: Database | None = None,
    transaction_middleware_class: type = TransactionMiddleware,
    prometheus_registry: CollectorRegistry = REGISTRY,
) -> FastAPI:
    """Create the FastAPI WSGI application."""
    settings = Settings()
    db = database or Database(str(settings.db_dsn))

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        await db.ensure_schema()
        yield
        await db.engine.dispose()

    app = FastAPI(
        title="MAAS Site Manager",
        name=PACKAGE.name,
        version=PACKAGE.version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
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


def _get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MAAS site manager user API.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--devmode",
        help="run server in deveopment mode",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--port",
        "-P",
        help="server port",
        type=int,
        default=8000,
    )
    return parser.parse_args()
