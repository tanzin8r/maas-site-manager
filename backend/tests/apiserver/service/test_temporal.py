from typing import Any
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture
from temporalio.service import RPCError, RPCStatusCode

from msm.apiserver.db.models import BootSource
from msm.apiserver.service.temporal import (
    WORKER_TOKEN_DURATION,
    BootSourceWorkflowService,
    TemporalService,
)
from msm.common.jwt import TokenAudience, TokenPurpose


class TestTemporalService:
    """Test class for TemporalService."""

    @pytest.mark.asyncio
    async def test_get_worker_credentials_success(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
    ) -> None:
        """Test successful retrieval of worker credentials."""
        mock_service_url = "https://example.com"
        mock_token_value = "mock-token-123"
        mock_token = mocker.MagicMock()
        mock_token.value = mock_token_value

        mock_settings_get_service_url = mocker.patch.object(
            temporal_service.settings,
            "get_service_url",
            return_value=mock_service_url,
        )
        mock_tokens_get = mocker.patch.object(
            temporal_service.tokens, "get", return_value=(1, [mock_token])
        )

        (
            service_url,
            token_value,
        ) = await temporal_service.get_worker_credentials()

        assert service_url == mock_service_url
        assert token_value == mock_token_value
        mock_settings_get_service_url.assert_called_once()
        mock_tokens_get.assert_called_once_with(
            audience=[TokenAudience.WORKER], purpose=[TokenPurpose.ACCESS]
        )

    @pytest.mark.asyncio
    async def test_schedule_create_success(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
        temporal_client: Any,
    ) -> None:
        scheduler_id = "test-scheduler"
        workflow = "TestWorkflow"
        workflow_id = "test-workflow-123"
        param = mocker.sentinel
        interval = 30
        expected_handle_id = "schedule-handle-123"

        mock_schedule_handle = mocker.MagicMock()
        mock_schedule_handle.id = expected_handle_id
        temporal_client.create_schedule.return_value = mock_schedule_handle

        result = await temporal_service.schedule_create(
            scheduler_id, workflow, workflow_id, param, interval
        )

        assert result == expected_handle_id
        temporal_client.create_schedule.assert_called_once()

        # Verify the call arguments
        call_args = temporal_client.create_schedule.call_args
        assert call_args[0][0] == scheduler_id  # First positional argument
        # Second positional argument (Schedule object)
        schedule_obj = call_args[0][1]
        assert schedule_obj.action.workflow == workflow
        assert schedule_obj.action.args[0] == param
        assert schedule_obj.action.id == workflow_id

    @pytest.mark.asyncio
    async def test_schedule_cancel_success(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
        temporal_client: Any,
    ) -> None:
        """Test successful schedule cancellation."""
        scheduler_id = "test-scheduler-to-cancel"

        mock_schedule_handle = mocker.AsyncMock()
        temporal_client.get_schedule_handle.return_value = mock_schedule_handle

        await temporal_service.schedule_cancel(scheduler_id)

        temporal_client.get_schedule_handle.assert_called_once_with(
            scheduler_id
        )
        mock_schedule_handle.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_schedule_pause_success(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
        temporal_client: Any,
    ) -> None:
        """Test successful schedule pause."""
        scheduler_id = "test-scheduler-to-pause"
        note = "Pausing for maintenance"

        mock_schedule_handle = mocker.AsyncMock()
        temporal_client.get_schedule_handle.return_value = mock_schedule_handle

        await temporal_service.schedule_pause(scheduler_id, note)

        temporal_client.get_schedule_handle.assert_called_once_with(
            scheduler_id
        )
        mock_schedule_handle.pause.assert_called_once_with(note=note)

    @pytest.mark.asyncio
    async def test_schedule_pause_without_note(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
        temporal_client: Any,
    ) -> None:
        """Test successful schedule pause without note."""
        scheduler_id = "test-scheduler-to-pause"

        mock_schedule_handle = mocker.AsyncMock()
        temporal_client.get_schedule_handle.return_value = mock_schedule_handle
        await temporal_service.schedule_pause(scheduler_id)

        temporal_client.get_schedule_handle.assert_called_once_with(
            scheduler_id
        )
        mock_schedule_handle.pause.assert_called_once_with(note=None)

    @pytest.mark.asyncio
    async def test_schedule_resume_success(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
        temporal_client: Any,
    ) -> None:
        """Test successful schedule resume."""
        scheduler_id = "test-scheduler-to-resume"
        note = "Pausing for maintenance"

        mock_schedule_handle = mocker.AsyncMock()
        temporal_client.get_schedule_handle.return_value = mock_schedule_handle
        await temporal_service.schedule_resume(scheduler_id, note)

        temporal_client.get_schedule_handle.assert_called_once_with(
            scheduler_id
        )
        mock_schedule_handle.unpause.assert_called_once_with(note=note)

    @pytest.mark.asyncio
    async def test_schedule_resume_without_note(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
        temporal_client: Any,
    ) -> None:
        """Test successful schedule resume without note."""
        scheduler_id = "test-scheduler-to-resume"

        mock_schedule_handle = mocker.AsyncMock()
        temporal_client.get_schedule_handle.return_value = mock_schedule_handle
        await temporal_service.schedule_resume(scheduler_id)

        temporal_client.get_schedule_handle.assert_called_once_with(
            scheduler_id
        )
        mock_schedule_handle.unpause.assert_called_once_with(note=None)

    @pytest.mark.asyncio
    async def test_schedule_fire_success(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
        temporal_client: Any,
    ) -> None:
        """Test successful schedule fire."""
        scheduler_id = "test-scheduler-to-fire"

        mock_schedule_handle = mocker.AsyncMock()
        temporal_client.get_schedule_handle.return_value = mock_schedule_handle
        await temporal_service.schedule_fire(scheduler_id)

        temporal_client.get_schedule_handle.assert_called_once_with(
            scheduler_id
        )
        mock_schedule_handle.trigger.assert_called_once_with(overlap=None)

    @pytest.mark.asyncio
    async def test_schedule_fire_with_force(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
        temporal_client: Any,
    ) -> None:
        """Test successful schedule fire with force=True."""
        from temporalio.client import ScheduleOverlapPolicy

        scheduler_id = "test-scheduler-to-fire"

        mock_schedule_handle = mocker.AsyncMock()
        temporal_client.get_schedule_handle.return_value = mock_schedule_handle
        await temporal_service.schedule_fire(scheduler_id, force=True)

        temporal_client.get_schedule_handle.assert_called_once_with(
            scheduler_id
        )
        mock_schedule_handle.trigger.assert_called_once_with(
            overlap=ScheduleOverlapPolicy.CANCEL_OTHER
        )

    @pytest.mark.asyncio
    async def test_ensure_tokens_expired(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
    ) -> None:
        """Test successful ensure operation."""
        # Mock tokens service
        mock_existing_token = mocker.MagicMock()
        mock_existing_token.id = "existing-token-123"
        mock_existing_token.is_expired.return_value = True
        mock_tokens_get = mocker.patch.object(
            temporal_service.tokens,
            "get",
            return_value=(1, [mock_existing_token]),
        )
        mock_tokens_delete_many = mocker.patch.object(
            temporal_service.tokens, "delete_many", return_value=None
        )
        mock_tokens_create = mocker.patch.object(
            temporal_service.tokens, "create", return_value=mocker.MagicMock()
        )

        # Mock config service
        mock_config = mocker.MagicMock()
        mock_config.service_identifier = "test-service"
        mock_config.token_secret_key = "secret-key-123"
        mock_config_get = mocker.patch.object(
            temporal_service.config, "get", return_value=mock_config
        )

        # Mock settings service
        mock_service_url = "https://test-service.com"
        mock_settings_get_service_url = mocker.patch.object(
            temporal_service.settings,
            "get_service_url",
            return_value=mock_service_url,
        )

        await temporal_service.ensure()

        # Verify tokens were renewed
        mock_tokens_get.assert_called_once_with(
            audience=[TokenAudience.WORKER],
            purpose=[TokenPurpose.ACCESS],
        )
        mock_tokens_delete_many.assert_called_once_with(
            [mock_existing_token.id]
        )

        # Verify config and settings were retrieved
        mock_config_get.assert_called_once()
        mock_settings_get_service_url.assert_called_once()

        # Verify new token was created
        mock_tokens_create.assert_called_once_with(
            issuer=mock_config.service_identifier,
            secret_key=mock_config.token_secret_key,
            service_url=mock_service_url,
            audience=TokenAudience.WORKER,
            purpose=TokenPurpose.ACCESS,
            duration=WORKER_TOKEN_DURATION,
        )

    async def test_ensure_tokens_not_expired(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
    ) -> None:
        """Test successful ensure operation."""
        # Mock tokens service
        mock_existing_token = mocker.MagicMock()
        mock_existing_token.id = "existing-token-123"
        mock_existing_token.is_expired.return_value = False
        mock_tokens_get = mocker.patch.object(
            temporal_service.tokens,
            "get",
            return_value=(1, [mock_existing_token]),
        )
        mock_tokens_delete_many = mocker.patch.object(
            temporal_service.tokens, "delete_many", return_value=None
        )
        mock_tokens_create = mocker.patch.object(
            temporal_service.tokens, "create", return_value=mocker.MagicMock()
        )

        await temporal_service.ensure()

        mock_tokens_get.assert_called_once_with(
            audience=[TokenAudience.WORKER],
            purpose=[TokenPurpose.ACCESS],
        )
        mock_tokens_delete_many.assert_not_called()

        # Verify new token was not created
        mock_tokens_create.assert_not_called()

    async def test_ensure_no_tokens(
        self,
        mocker: MockerFixture,
        temporal_service: TemporalService,
    ) -> None:
        mock_tokens_get = mocker.patch.object(
            temporal_service.tokens,
            "get",
            return_value=(0, []),
        )
        mock_tokens_delete_many = mocker.patch.object(
            temporal_service.tokens, "delete_many", return_value=None
        )
        mock_tokens_create = mocker.patch.object(
            temporal_service.tokens, "create", return_value=mocker.MagicMock()
        )

        # Mock config service
        mock_config = mocker.MagicMock()
        mock_config.service_identifier = "test-service"
        mock_config.token_secret_key = "secret-key-123"
        mock_config_get = mocker.patch.object(
            temporal_service.config, "get", return_value=mock_config
        )

        # Mock settings service
        mock_service_url = "https://test-service.com"
        mock_settings_get_service_url = mocker.patch.object(
            temporal_service.settings,
            "get_service_url",
            return_value=mock_service_url,
        )

        await temporal_service.ensure()

        mock_tokens_get.assert_called_once_with(
            audience=[TokenAudience.WORKER],
            purpose=[TokenPurpose.ACCESS],
        )
        mock_tokens_delete_many.assert_not_called()

        # Verify config and settings were retrieved
        mock_config_get.assert_called_once()
        mock_settings_get_service_url.assert_called_once()

        # Verify new token was created
        mock_tokens_create.assert_called_once_with(
            issuer=mock_config.service_identifier,
            secret_key=mock_config.token_secret_key,
            service_url=mock_service_url,
            audience=TokenAudience.WORKER,
            purpose=TokenPurpose.ACCESS,
            duration=WORKER_TOKEN_DURATION,
        )


@pytest.mark.asyncio
class TestBootSourceWorkflowService:
    async def test_enable_sync_new_schedule(
        self,
        mocker: MockerFixture,
        workflow_service: BootSourceWorkflowService,
        boot_source: BootSource,
    ) -> None:
        s3_params = mocker.sentinel
        _ = mocker.patch.object(
            workflow_service,
            "s3_params",
            new_callable=mocker.PropertyMock(return_value=s3_params),
        )

        mock_schedule_handle1 = mocker.AsyncMock()
        mock_schedule_handle2 = mocker.AsyncMock()
        mock_update_1 = mocker.patch.object(mock_schedule_handle1, "update")
        mock_update_2 = mocker.patch.object(mock_schedule_handle2, "update")

        mock_update_1.side_effect = RPCError("", RPCStatusCode.NOT_FOUND, b"")
        mock_update_2.side_effect = RPCError("", RPCStatusCode.NOT_FOUND, b"")

        mock_get_handle = mocker.patch.object(
            workflow_service.temporal, "get_schedule_handle", autospec=True
        )
        mock_get_handle.side_effect = [
            mock_schedule_handle1,
            mock_schedule_handle2,
        ]

        mock_schedule_create = mocker.patch.object(
            workflow_service.temporal, "schedule_create", autospec=True
        )

        mock_get_worker_credentials = mocker.patch.object(
            workflow_service.temporal,
            "get_worker_credentials",
            autospec=True,
        )
        mock_get_worker_credentials.return_value = (
            "https://test.service.url",
            "test-jwt-token",
        )

        await workflow_service.enable_sync(
            boot_source.id, boot_source.sync_interval
        )

        mock_get_worker_credentials.assert_called_once()
        mock_schedule_create.assert_called()

        # Check the workflow parameters
        expected_calls = [
            call(
                scheduler_id=f"sched-boot-select-{boot_source.id}",
                workflow="RefreshUpstreamSource",
                workflow_id=f"wf-refresh-bootsel-{boot_source.id}",
                param=mocker.ANY,
                interval=boot_source.sync_interval // 2,
            ),
            call(
                scheduler_id=f"sched-boot-source-{boot_source.id}",
                workflow="SyncUpstreamSource",
                workflow_id=f"wf-sync-upstream-{boot_source.id}",
                param=mocker.ANY,
                interval=boot_source.sync_interval,
            ),
        ]
        assert mock_schedule_create.call_args_list == expected_calls

    async def test_enable_sync_update_schedule(
        self,
        mocker: MockerFixture,
        workflow_service: BootSourceWorkflowService,
        boot_source: BootSource,
    ) -> None:
        s3_params = mocker.sentinel
        _ = mocker.patch.object(
            workflow_service,
            "s3_params",
            new_callable=mocker.PropertyMock(return_value=s3_params),
        )

        mock_schedule_handle1 = mocker.AsyncMock()
        mock_schedule_handle2 = mocker.AsyncMock()
        mock_update_1 = mocker.patch.object(mock_schedule_handle1, "update")
        mock_update_2 = mocker.patch.object(mock_schedule_handle2, "update")
        mock_get_handle = mocker.patch.object(
            workflow_service.temporal, "get_schedule_handle", autospec=True
        )
        mock_get_handle.side_effect = [
            mock_schedule_handle1,
            mock_schedule_handle2,
        ]

        mock_schedule_create = mocker.patch.object(
            workflow_service.temporal, "schedule_create", autospec=True
        )

        mock_get_worker_credentials = mocker.patch.object(
            workflow_service.temporal,
            "get_worker_credentials",
            autospec=True,
        )
        mock_get_worker_credentials.return_value = (
            "https://test.service.url",
            "test-jwt-token",
        )

        await workflow_service.enable_sync(
            boot_source.id, boot_source.sync_interval
        )

        mock_get_worker_credentials.assert_called_once()
        mock_update_1.assert_called_once()
        mock_update_2.assert_called_once()
        mock_schedule_create.assert_not_called()

    async def test_disable_sync(
        self,
        mocker: MockerFixture,
        workflow_service: BootSourceWorkflowService,
        boot_source: BootSource,
    ) -> None:
        mock_schedule_cancel = mocker.patch.object(
            workflow_service.temporal, "schedule_cancel", autospec=True
        )
        await workflow_service.disable_sync(boot_source.id)
        mock_schedule_cancel.assert_called()

        # Check the workflow parameters
        expected_calls = [
            call(f"sched-boot-select-{boot_source.id}"),
            call(f"sched-boot-source-{boot_source.id}"),
        ]
        assert mock_schedule_cancel.call_args_list == expected_calls

    async def test_trigger_sync(
        self,
        mocker: MockerFixture,
        workflow_service: BootSourceWorkflowService,
        boot_source: BootSource,
    ) -> None:
        mock_schedule_fire = mocker.patch.object(
            workflow_service.temporal, "schedule_fire", autospec=True
        )
        await workflow_service.trigger_sync(boot_source.id)
        mock_schedule_fire.assert_called()

        # Check the workflow parameters
        expected_calls = [
            call(f"sched-boot-source-{boot_source.id}"),
            call(f"sched-boot-select-{boot_source.id}"),
        ]
        assert mock_schedule_fire.call_args_list == expected_calls
