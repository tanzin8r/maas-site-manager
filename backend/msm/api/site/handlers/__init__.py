from msm.api.site.handlers import (
    enroll,
    report,
)

ROUTERS = (
    enroll.v1_router,
    report.v1_router,
)
