from datetime import timedelta
from functools import cached_property
from typing import Any, override

from sqlalchemy.ext.asyncio import AsyncConnection
from temporalio.client import (
    Client as TemporalClient,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleHandle,
    ScheduleIntervalSpec,
    ScheduleOverlapPolicy,
    SchedulePolicy,
    ScheduleSpec,
    ScheduleUpdate,
    ScheduleUpdateInput,
)
from temporalio.common import RetryPolicy
from temporalio.service import RPCError
from temporallib.client import Options  # type: ignore
from temporallib.encryption import EncryptionOptions  # type: ignore

from msm.apiserver.service.base import Service
from msm.apiserver.service.config import ConfigService
from msm.apiserver.service.s3 import S3Service
from msm.apiserver.service.settings import SettingsService
from msm.apiserver.service.token import TokenService
from msm.common.jwt import TokenAudience, TokenPurpose
from msm.common.settings import Settings
import msm.common.workflows.sync as msm_wf

WORKER_TOKEN_DURATION = timedelta(days=365 * 5)
BOOT_SELECTION_REFRESH_INTVAL = 5


class S3ParametersError(Exception):
    """Raised when S3 configuration is incomplete."""


class TemporalService(Service):
    """Service for managing Temporal workflows and schedules.

    This service provides functionality to interact with Temporal workflows,
    including creating, managing, and scheduling workflows for upstream source
    synchronization and refresh operations.
    """

    def __init__(
        self,
        connection: AsyncConnection,
        config: ConfigService,
        tokens: TokenService,
        settings: SettingsService,
        temporal_client: TemporalClient,
    ):
        super().__init__(connection)
        self.tokens: TokenService = tokens
        self.config: ConfigService = config
        self.settings: SettingsService = settings
        self.application_settings: Settings = Settings()
        self.temporal_client: TemporalClient = temporal_client

    @cached_property
    def options(self) -> Options:
        return Options(
            host=self.application_settings.temporal_server_address,
            queue=self.application_settings.temporal_task_queue,
            namespace=self.application_settings.temporal_namespace,
            tls_root_cas=self.application_settings.temporal_tls_root_cas,
            encryption=EncryptionOptions(),
        )

    async def get_worker_credentials(self) -> tuple[str, str]:
        """Get service URL and worker token for authentication.

        Returns:
            tuple[str, str]: A tuple containing the service URL and worker token value.
        """
        service_url = await self.settings.get_service_url()
        _, tokens = await self.tokens.get(
            audience=[TokenAudience.WORKER], purpose=[TokenPurpose.ACCESS]
        )
        token = next(iter(tokens))
        return service_url, token.value

    async def schedule_create(
        self,
        scheduler_id: str,
        workflow: str,
        workflow_id: str,
        param: Any,
        interval: int,
    ) -> str:
        """Create a scheduled workflow.

        Args:
            scheduler_id: Unique identifier for the scheduler
            workflow: Name of the workflow to schedule
            workflow_id: Unique identifier for the workflow instance
            param: Parameters to pass to the workflow
            interval: Interval in minutes between workflow executions

        Returns:
            str: The ID of the created schedule handle
        """

        hdl = await self.temporal_client.create_schedule(
            scheduler_id,
            Schedule(
                action=ScheduleActionStartWorkflow(
                    workflow,
                    param,
                    id=workflow_id,
                    task_queue=self.options.queue or "not-set",
                    retry_policy=RetryPolicy(  # don't spin too fast
                        initial_interval=timedelta(minutes=1),
                        maximum_interval=timedelta(minutes=1),
                    ),
                    execution_timeout=timedelta(minutes=2 * interval),
                ),
                spec=ScheduleSpec(
                    intervals=[
                        ScheduleIntervalSpec(every=timedelta(minutes=interval))
                    ]
                ),
                policy=SchedulePolicy(
                    overlap=ScheduleOverlapPolicy.BUFFER_ONE,
                ),
            ),
        )
        return hdl.id

    async def schedule_cancel(self, scheduler_id: str) -> None:
        """Cancel a scheduled workflow.

        Args:
            scheduler_id: Unique identifier for the scheduler to cancel
        """
        hdl = self.temporal_client.get_schedule_handle(scheduler_id)
        await hdl.delete()

    async def schedule_pause(
        self, scheduler_id: str, note: str | None = None
    ) -> None:
        """Pause a scheduled workflow.

        Args:
            scheduler_id: Unique identifier for the scheduler to pause
            note: Optional note explaining the reason for pausing
        """
        hdl = self.temporal_client.get_schedule_handle(scheduler_id)
        await hdl.pause(note=note)

    async def schedule_resume(
        self, scheduler_id: str, note: str | None = None
    ) -> None:
        """Resume a paused scheduled workflow.

        Args:
            scheduler_id: Unique identifier for the scheduler to resume
            note: Optional note explaining the reason for resuming
        """
        hdl = self.temporal_client.get_schedule_handle(scheduler_id)
        await hdl.unpause(note=note)

    async def schedule_fire(
        self, scheduler_id: str, force: bool = False
    ) -> None:
        """Fire a scheduled workflow immediately.

        Args:
            scheduler_id: Unique identifier for the scheduler to fire
            force: If True, cancel other running instances; if False, buffer the execution
        """
        hdl = self.temporal_client.get_schedule_handle(scheduler_id)
        await hdl.trigger(
            overlap=ScheduleOverlapPolicy.CANCEL_OTHER if force else None
        )

    def get_schedule_handle(self, schedule_id: str) -> ScheduleHandle:
        return self.temporal_client.get_schedule_handle(schedule_id)

    @override
    async def ensure(self) -> None:
        """Prepare Site Manager to schedule Temporal workflows."""
        await super().ensure()

        # renew JWT credentials for the workers
        _, tokens = await self.tokens.get(
            audience=[TokenAudience.WORKER], purpose=[TokenPurpose.ACCESS]
        )
        if expired := [t.id for t in tokens if t.is_expired()]:
            _ = await self.tokens.delete_many(expired)

            config = await self.config.get()
            service_url = await self.settings.get_service_url()
            _ = await self.tokens.create(
                issuer=config.service_identifier,
                secret_key=config.token_secret_key,
                service_url=service_url,
                audience=TokenAudience.WORKER,
                purpose=TokenPurpose.ACCESS,
                duration=WORKER_TOKEN_DURATION,
            )


class BootSourceWorkflowService(Service):
    def __init__(
        self,
        connection: AsyncConnection,
        s3: S3Service,
        temporal: TemporalService,
    ):
        super().__init__(connection)
        self.s3: S3Service = s3
        self.temporal: TemporalService = temporal

    @cached_property
    def s3_params(self) -> msm_wf.S3Params:
        """S3 parameters for workflows."""
        if not all(
            [
                self.s3.s3_endpoint,
                self.s3.s3_bucket,
                self.s3.s3_access_key,
                self.s3.s3_secret_key,
            ]
        ):
            raise S3ParametersError()

        return msm_wf.S3Params(
            endpoint=self.s3.s3_endpoint,
            bucket=self.s3.s3_bucket,
            access_key=self.s3.s3_access_key,
            secret_key=self.s3.s3_secret_key,
            path=self.s3.s3_path,
        )

    async def enable_sync(
        self,
        boot_source_id: int,
        sync_interval: int,
    ) -> None:
        """
        Enable upstream synchronization for a boot source.

        This method sets up scheduled workflows for synchronizing boot source selections
        and images from upstream sources at specified intervals.

        Args:
            boot_source_id: The ID of the boot source to enable sync for.
            sync_interval: The interval in seconds between synchronization runs.
            msm_url: The API URL for workers. If empty, will be retrieved automatically.
            msm_jwt: The API JWT credentials for workers. If empty, will be retrieved automatically.
        """
        msm_url, msm_jwt = await self.temporal.get_worker_credentials()
        try:
            hdls = [
                self.temporal.get_schedule_handle(
                    f"sched-boot-select-{boot_source_id}"
                ),
                self.temporal.get_schedule_handle(
                    f"sched-boot-source-{boot_source_id}"
                ),
            ]
            s3_params = self.s3_params

            def update_schedule(input: ScheduleUpdateInput) -> ScheduleUpdate:
                if isinstance(
                    input.description.schedule.action,
                    ScheduleActionStartWorkflow,
                ):
                    if (
                        input.description.schedule.action.workflow
                        == msm_wf.SYNC_UPSTREAM_SOURCE_WF_NAME
                    ):
                        input.description.schedule.action.args = [
                            msm_wf.SyncUpstreamSourceParams(
                                msm_url=msm_url,
                                msm_jwt=msm_jwt,
                                boot_source_id=boot_source_id,
                                s3_params=s3_params,
                            )
                        ]
                        input.description.schedule.spec = ScheduleSpec(
                            intervals=[
                                ScheduleIntervalSpec(
                                    every=timedelta(minutes=sync_interval)
                                )
                            ]
                        )
                    elif (
                        input.description.schedule.action.workflow
                        == msm_wf.REFRESH_UPSTREAM_SOURCE_WF_NAME
                    ):
                        input.description.schedule.action.args = [
                            msm_wf.RefreshUpstreamSourceParams(
                                msm_url=msm_url,
                                msm_jwt=msm_jwt,
                                boot_source_id=boot_source_id,
                            )
                        ]
                        input.description.schedule.spec = ScheduleSpec(
                            intervals=[
                                ScheduleIntervalSpec(
                                    every=timedelta(
                                        minutes=max(
                                            sync_interval // 2,
                                            BOOT_SELECTION_REFRESH_INTVAL,
                                        ),
                                    )
                                )
                            ]
                        )
                return ScheduleUpdate(schedule=input.description.schedule)

            for hdl in hdls:
                await hdl.update(update_schedule)
        except RPCError:
            # sync selections
            _ = await self.temporal.schedule_create(
                scheduler_id=f"sched-boot-select-{boot_source_id}",
                workflow=msm_wf.REFRESH_UPSTREAM_SOURCE_WF_NAME,
                workflow_id=f"wf-refresh-bootsel-{boot_source_id}",
                param=msm_wf.RefreshUpstreamSourceParams(
                    msm_url=msm_url,
                    msm_jwt=msm_jwt,
                    boot_source_id=boot_source_id,
                ),
                interval=max(
                    sync_interval // 2, BOOT_SELECTION_REFRESH_INTVAL
                ),
            )

            # sync images
            _ = await self.temporal.schedule_create(
                scheduler_id=f"sched-boot-source-{boot_source_id}",
                workflow=msm_wf.SYNC_UPSTREAM_SOURCE_WF_NAME,
                workflow_id=f"wf-sync-upstream-{boot_source_id}",
                param=msm_wf.SyncUpstreamSourceParams(
                    msm_url=msm_url,
                    msm_jwt=msm_jwt,
                    boot_source_id=boot_source_id,
                    s3_params=self.s3_params,
                ),
                interval=sync_interval,
            )

    async def disable_sync(self, boot_source_id: int) -> None:
        """Disable upstream synchronization for a boot source."""
        await self.temporal.schedule_cancel(
            f"sched-boot-select-{boot_source_id}"
        )
        await self.temporal.schedule_cancel(
            f"sched-boot-source-{boot_source_id}"
        )

    async def trigger_sync(self, boot_source_id: int) -> None:
        """Trigger synchronization for a boot source."""
        await self.temporal.schedule_fire(
            f"sched-boot-source-{boot_source_id}"
        )
