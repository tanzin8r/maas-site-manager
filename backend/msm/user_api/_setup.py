from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import handlers
from .. import PACKAGE
from ..db import Database
from ..settings import SETTINGS


def create_app(db_dsn: str | None = None) -> FastAPI:
    """Create the FastAPI WSGI application."""
    if db_dsn is None:
        db_dsn = str(SETTINGS.db_dsn)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        await db.setup()
        yield
        await db.dispose()

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
    app.router.add_api_route("/", handlers.root.get, methods=["GET"])

    app.router.add_api_route("/login", handlers.login.post, methods=["POST"])

    app.router.add_api_route(
        "/requests", handlers.sites.pending_get, methods=["GET"]
    )
    app.router.add_api_route(
        "/requests",
        handlers.sites.pending_post,
        methods=["POST"],
        status_code=204,
    )
    app.router.add_api_route("/sites", handlers.sites.get, methods=["GET"])

    app.router.add_api_route("/tokens", handlers.tokens.get, methods=["GET"])
    app.router.add_api_route("/tokens", handlers.tokens.post, methods=["POST"])
    app.router.add_api_route(
        "/tokens/export", handlers.tokens.export_get, methods=["GET"]
    )

    app.router.add_api_route(
        "/users/me", handlers.users.me_get, methods=["GET"]
    )
    app.router.add_api_route(
        "/users/me", handlers.users.me_patch, methods=["PATCH"]
    )
    app.router.add_api_route(
        "/users/me/password", handlers.users.password_post, methods=["POST"]
    )
    app.router.add_api_route("/users", handlers.users.get, methods=["GET"])
    app.router.add_api_route("/users", handlers.users.post, methods=["POST"])
    app.router.add_api_route(
        "/users/{user_id}", handlers.users.patch, methods=["PATCH"]
    )
    app.router.add_api_route(
        "/users/{user_id}",
        handlers.users.delete,
        methods=["DELETE"],
        status_code=204,
    )
    return app
