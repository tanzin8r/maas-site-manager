from . import (
    login,
    root,
    sites,
    tokens,
    users,
)

API_ROUTERS = [
    root.router,
    login.router,
    sites.router,
    tokens.router,
    users.router,
]
