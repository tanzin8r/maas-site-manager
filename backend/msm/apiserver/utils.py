"""Common utility functions for the API"""

from collections.abc import Iterable

from fastapi import (
    APIRouter,
    FastAPI,
)

from msm import __version__


def create_subapp(
    title: str, name: str, routers: Iterable[APIRouter]
) -> FastAPI:
    """Return a FastAPI application with the specified routers registered."""
    app = FastAPI(title=title, name=name, version=__version__)
    for r in routers:
        app.router.include_router(r)
    return app
