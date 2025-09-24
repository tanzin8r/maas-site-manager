from msm.apiserver.site.handlers import (
    enroll,
    report,
)

ROUTERS = (
    enroll.v1_router,
    report.v1_router,
)
