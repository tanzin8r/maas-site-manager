from msm.api.site.handlers import (
    enrol,
    report,
)

ROUTERS = (
    enrol.v1_router,
    report.v1_router,
)
