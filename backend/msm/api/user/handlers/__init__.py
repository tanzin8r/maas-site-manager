from fastapi import APIRouter

from . import (
    login,
    root,
    sites,
    tokens,
    users,
)


def api_router() -> APIRouter:
    """Return a router for API routes."""
    router = APIRouter()
    for r in (
        root.v1_router,
        login.v1_router,
        sites.v1_router,
        tokens.v1_router,
        users.v1_router,
    ):
        router.include_router(r)
    return router
