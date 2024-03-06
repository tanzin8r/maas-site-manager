"""Common utility functions for the API"""

from collections.abc import Iterable

from fastapi import (
    APIRouter,
    FastAPI,
    HTTPException,
    status,
)
from pydantic import BaseModel

from msm import __version__

INVALID_TOKEN_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"},
)


def not_found(entity: str) -> HTTPException:
    """Raise a 404 error for an something described by 'entity'
    entity should be uppercase
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": f"{entity} does not exist."},
    )


def raise_on_empty_request(request: BaseModel) -> None:
    """Check if given `request` is empty and raise 422 in that case"""
    if not request.model_dump(exclude_none=True):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Request body empty."},
        )


def create_subapp(
    title: str, name: str, routers: Iterable[APIRouter]
) -> FastAPI:
    """Return a FastAPI application with the specified routers registered."""
    app = FastAPI(title=title, name=name, version=__version__)
    for r in routers:
        app.router.include_router(r)
    return app
