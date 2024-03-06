from msm.api.user.handlers import (
    login,
    settings,
    sites,
    tokens,
    users,
)

ROUTERS = (
    login.v1_router,
    settings.v1_router,
    sites.v1_router,
    tokens.v1_router,
    users.v1_router,
)
