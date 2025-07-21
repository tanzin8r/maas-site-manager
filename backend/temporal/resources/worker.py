import asyncio
import logging

from activities.images import (  # type: ignore
    ImageManagementActivities,
)
from activities.simplestream import (  # type: ignore
    SimpleStreamActivities,
)
from temporallib.client import Client, Options  # type: ignore
from temporallib.encryption import EncryptionOptions  # type: ignore
from temporallib.worker import (  # type: ignore
    SentryOptions,
    Worker,
    WorkerOptions,
)
from workflows.download_upstream import (  # type: ignore
    DownloadUpstreamImage,
    GetOrCreateProduct,
)
from workflows.sync import (  # type: ignore
    SyncUpstreamSourceWorkflow,
)

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    """Connect Temporal worker to Temporal server."""
    client = await Client.connect(
        client_opt=Options(encryption=EncryptionOptions()),
    )
    img_act = ImageManagementActivities()
    ss_act = SimpleStreamActivities()
    worker = Worker(
        client=client,
        workflows=[
            DownloadUpstreamImage,
            GetOrCreateProduct,
            SyncUpstreamSourceWorkflow,
        ],
        activities=[
            img_act.download_asset,
            img_act.get_or_create_asset,
            img_act.get_or_create_item,
            img_act.get_or_create_version,
            ss_act.get_boot_source,
            ss_act.parse_ss_index,
            ss_act.load_product_map,
        ],
        worker_opt=WorkerOptions(sentry=SentryOptions()),
    )

    await worker.run()


if __name__ == "__main__":  # pragma: nocover
    asyncio.run(run_worker())
