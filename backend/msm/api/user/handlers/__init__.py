from . import (
    login,
    sites,
    tokens,
    users,
)

ROUTERS = (
    login.v1_router,
    sites.v1_router,
    tokens.v1_router,
    users.v1_router,
)
