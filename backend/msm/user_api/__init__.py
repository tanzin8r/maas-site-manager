from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .. import PACKAGE
from ..db import Database
from ..settings import SETTINGS
from .handlers import API_ROUTERS


def create_app(database: Database | None = None) -> FastAPI:
    """Create the FastAPI WSGI application."""
    db = database or Database(str(SETTINGS.db_dsn))

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
    app.state.db = db
    app.add_middleware(
        CORSMiddleware,
        allow_origins=SETTINGS.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in API_ROUTERS:
        app.include_router(router)
    return app
