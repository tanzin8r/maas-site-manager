from contextlib import contextmanager
from typing import (
    Any,
    Callable,
    Iterator,
)

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.routing import Mount


@contextmanager
def override_dependencies(
    app: FastAPI,
    dependencies_map: dict[Callable[..., Any], Callable[..., Any]],
) -> Iterator[None]:
    """Context manager to override app dependencies in tests."""
    for orig_func, override_func in dependencies_map.items():
        app.dependency_overrides[orig_func] = override_func
    yield
    for orig_func in dependencies_map:
        del app.dependency_overrides[orig_func]


def get_api_routes(app: FastAPI, prefix: str) -> set[tuple[str, str]]:
    """Return API routes under the prefix, as tuples of (method, URL).

    The specified prefix must be a `Mount` for a sub-application.
    """
    [mount] = [
        m for m in app.routes if isinstance(m, Mount) and m.path == prefix
    ]

    routes = set()
    for route in mount.app.routes:  # type: ignore[attr-defined]
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods:
            routes.add((method, f"{prefix}{route.path}"))
    return routes
