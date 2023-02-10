from fastapi import FastAPI

from . import _base
from .. import PACKAGE
from ..db import Database

# XXX drop hardcoded default
DEFAULT_DB_DSN = "postgresql+asyncpg://postgres:pass@localhost/postgres"


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
    app.router.add_api_route("/tokens", _base.tokens_post, methods=["POST"])
    return app
