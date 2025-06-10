import asyncio
import logging

from activities.download_upstream_activities import (  # type: ignore
    ImageManagementActivity,
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
    activities = ImageManagementActivity()
    worker = Worker(
        client=client,
        workflows=[
            DownloadUpstreamImage,
            GetOrCreateProduct,
            SyncUpstreamSourceWorkflow,
        ],
        activities=[
            activities.download_asset,
            activities.update_bytes_synced,
            activities.get_or_create_asset,
            activities.get_or_create_item,
            activities.get_or_create_version,
            activities.get_boot_source,
            activities.download_json,
            activities.parse_ss_index,
            activities.load_product_map,
        ],
        worker_opt=WorkerOptions(sentry=SentryOptions()),
    )

    await worker.run()


if __name__ == "__main__":  # pragma: nocover
    asyncio.run(run_worker())
