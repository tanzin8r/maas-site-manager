from contextlib import asynccontextmanager
from os import environ
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import _base
from .. import PACKAGE
from ..db import Database

POSTGRES_HOST = environ.get("POSTGRES_HOST")
POSTGRES_PORT = environ.get("POSTGRES_PORT")
POSTGRES_DB = environ.get("POSTGRES_DB")
POSTGRES_USER = environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")
DEFAULT_DB_DSN = (
    "postgresql+asyncpg://"
    + f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
)

# TODO: make config dynamic and allow env vars
origins = [
    "http://localhost:8405",
    "http://127.0.0.1:8405",
]


def create_app(db_dsn: str = DEFAULT_DB_DSN) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        await db.connect()
        yield
        await db.disconnect()

    db = Database(db_dsn)
    app = FastAPI(
        title="MAAS Site Manager",
        name=PACKAGE.project_name,
        version=PACKAGE.version,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.db = db
    app.router.add_api_route("/", _base.root, methods=["GET"])
    app.router.add_api_route("/sites", _base.sites, methods=["GET"])
    app.router.add_api_route("/tokens", _base.tokens, methods=["GET"])
    app.router.add_api_route("/tokens", _base.tokens_post, methods=["POST"])
    return app
