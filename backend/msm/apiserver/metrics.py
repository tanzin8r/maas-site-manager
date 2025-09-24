from logging import Logger

from anyio import sleep
from prometheus_client import Info

from msm import __version__
from msm.apiserver.db import Database
from msm.apiserver.service import ServiceCollection
from msm.common.settings import Settings

msm_info = Info("msm", "MAAS site manager info")
msm_info.info({"version": __version__})


async def collect_stats(
    db: Database,
    logger: Logger,
) -> None:
    refresh_interval = Settings().metrics_refresh_interval_seconds

    while True:
        async with db.transaction() as tx:
            services = ServiceCollection(tx)
            await services.collect_metrics()
        await sleep(refresh_interval)
