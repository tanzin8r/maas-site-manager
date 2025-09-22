import asyncio
import logging

from temporallib.client import Client, Options  # type: ignore
from temporallib.encryption import EncryptionOptions  # type: ignore
from temporallib.worker import (  # type: ignore
    SentryOptions,
    Worker,
    WorkerOptions,
)

from .activities.bootasset import (
    BootAssetActivities,
)
from .activities.images import (
    ImageManagementActivities,
)
from .activities.simplestream import (
    SimpleStreamActivities,
)
from .workflows.download_upstream import (
    DownloadUpstreamImageWorkflow,
)
from .workflows.sync import (
    RefreshUpstreamSourceWorkflow,
    SyncUpstreamSourceWorkflow,
)

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    """Connect Temporal worker to Temporal server."""
    client = await Client.connect(
        client_opt=Options(encryption=EncryptionOptions()),
    )
    ba_act = BootAssetActivities()
    img_act = ImageManagementActivities()
    ss_act = SimpleStreamActivities()
    worker = Worker(
        client=client,
        workflows=[
            DownloadUpstreamImageWorkflow,
            RefreshUpstreamSourceWorkflow,
            SyncUpstreamSourceWorkflow,
        ],
        activities=[
            ba_act.get_boot_asset_item,
            ba_act.get_boot_source,
            ba_act.put_asset_list,
            ba_act.put_available_asset_list,
            img_act.download_asset,
            ss_act.fetch_ss_asset_list,
            ss_act.load_product_map,
            ss_act.parse_ss_index,
        ],
        worker_opt=WorkerOptions(
            sentry=SentryOptions(dsn=None, release=None, environment=None)
        ),
    )

    await worker.run()


if __name__ == "__main__":  # pragma: nocover
    asyncio.run(run_worker())
