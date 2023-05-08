from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import _handlers
from .. import PACKAGE
from ..db import Database
from ..settings import SETTINGS


def create_app(db_dsn: str | None = None) -> FastAPI:
    """Create the FastAPI WSGI application."""
    if db_dsn is None:
        db_dsn = str(SETTINGS.db_dsn)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        await db.connect()
        yield
        await db.disconnect()

    db = Database(db_dsn)
    app = FastAPI(
        title="MAAS Site Manager",
        name=PACKAGE.name,
        version=PACKAGE.version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=SETTINGS.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.db = db
    app.router.add_api_route("/", _handlers.root_get, methods=["GET"])
    app.router.add_api_route("/login", _handlers.login_post, methods=["POST"])
    app.router.add_api_route(
        "/requests", _handlers.pending_sites_get, methods=["GET"]
    )
    app.router.add_api_route(
        "/requests",
        _handlers.pending_sites_post,
        methods=["POST"],
        status_code=204,
    )
    app.router.add_api_route("/sites", _handlers.sites_get, methods=["GET"])
    app.router.add_api_route("/tokens", _handlers.tokens_get, methods=["GET"])
    app.router.add_api_route(
        "/tokens", _handlers.tokens_post, methods=["POST"]
    )
    app.router.add_api_route(
        "/users/me", _handlers.users_me_get, methods=["GET"]
    )
    return app
