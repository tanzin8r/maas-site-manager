from os import environ

from fastapi import FastAPI

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


def create_app(db_dsn: str = DEFAULT_DB_DSN) -> FastAPI:
    db = Database(db_dsn)
    app = FastAPI(
        name=PACKAGE.project_name,
        version=PACKAGE.version,
        on_startup=[db.connect],
        on_shutdown=[db.disconnect],
    )
    app.state.db = db
    app.router.add_api_route("/", _base.root, methods=["GET"])
    app.router.add_api_route("/sites", _base.sites, methods=["GET"])
    app.router.add_api_route("/tokens", _base.tokens, methods=["GET"])
    app.router.add_api_route("/tokens", _base.tokens_post, methods=["POST"])
    return app
