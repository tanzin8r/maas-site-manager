from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import handlers
from .. import PACKAGE
from ..db import Database
from ..settings import SETTINGS


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
    app.router.add_api_route(
        "/sites/{site_id}", handlers.sites.get_id, methods=["GET"]
    )

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
        "/users/{user_id}", handlers.users.get_id, methods=["GET"]
    )
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
