"""Tests for metrics collection."""

from logging import Logger
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from temporalio.client import Client as TemporalClient

from msm.apiserver.db import Database
from msm.apiserver.metrics import collect_stats


@pytest.fixture
def mock_db() -> Database:
    """Mock database."""
    mock = MagicMock(spec=Database)
    mock_tx = AsyncMock()
    mock.transaction.return_value.__aenter__.return_value = mock_tx
    mock.transaction.return_value.__aexit__.return_value = None
    return mock


@pytest.fixture
def mock_temporal_client() -> TemporalClient:
    """Mock Temporal client."""
    return MagicMock(spec=TemporalClient)


@pytest.fixture
def mock_logger() -> Logger:
    """Mock logger."""
    return MagicMock(spec=Logger)


class TestCollectStats:
    """Test cases for metrics collection."""

    async def test_collect_stats_runs_collection_cycle(
        self,
        mock_db: Database,
        mock_temporal_client: TemporalClient,
        mock_logger: Logger,
    ) -> None:
        """Test that collect_stats runs metrics collection cycle."""
        with (
            patch(
                "msm.apiserver.metrics.ServiceCollection"
            ) as mock_service_collection_class,
            patch("msm.apiserver.metrics.Settings") as mock_settings_class,
            patch("msm.apiserver.metrics.sleep") as mock_sleep,
        ):
            # Configure mocks
            mock_settings = MagicMock()
            mock_settings.metrics_refresh_interval_seconds = 60
            mock_settings_class.return_value = mock_settings

            mock_service_collection = MagicMock()
            mock_service_collection.collect_metrics = AsyncMock()
            mock_service_collection_class.return_value = (
                mock_service_collection
            )

            # Make sleep raise an exception to break the infinite loop
            call_count = 0

            async def sleep_side_effect(seconds: float) -> None:
                nonlocal call_count
                call_count += 1
                if call_count >= 2:
                    raise KeyboardInterrupt("Test completed")

            mock_sleep.side_effect = sleep_side_effect

            # Run the function and expect it to raise after 2 iterations
            with pytest.raises(KeyboardInterrupt):
                await collect_stats(mock_db, mock_temporal_client, mock_logger)

            # Verify that metrics were collected at least once
            assert mock_service_collection.collect_metrics.call_count >= 1
            # Verify that the database transaction was used
            assert mock_db.transaction.call_count >= 1  # type: ignore[attr-defined]
            # Verify ServiceCollection was created with correct arguments
            tx = await mock_db.transaction().__aenter__()
            mock_service_collection_class.assert_called_with(
                tx, mock_temporal_client
            )

    async def test_collect_stats_uses_correct_refresh_interval(
        self,
        mock_db: Database,
        mock_temporal_client: TemporalClient,
        mock_logger: Logger,
    ) -> None:
        """Test that collect_stats uses the configured refresh interval."""
        with (
            patch(
                "msm.apiserver.metrics.ServiceCollection"
            ) as mock_service_collection_class,
            patch("msm.apiserver.metrics.Settings") as mock_settings_class,
            patch("msm.apiserver.metrics.sleep") as mock_sleep,
        ):
            # Configure mocks
            test_interval = 120
            mock_settings = MagicMock()
            mock_settings.metrics_refresh_interval_seconds = test_interval
            mock_settings_class.return_value = mock_settings

            mock_service_collection = MagicMock()
            mock_service_collection.collect_metrics = AsyncMock()
            mock_service_collection_class.return_value = (
                mock_service_collection
            )

            # Make sleep raise an exception after first call
            async def sleep_side_effect(seconds: float) -> None:
                raise KeyboardInterrupt("Test completed")

            mock_sleep.side_effect = sleep_side_effect

            # Run the function
            with pytest.raises(KeyboardInterrupt):
                await collect_stats(mock_db, mock_temporal_client, mock_logger)

            # Verify sleep was called with the correct interval
            mock_sleep.assert_called_with(test_interval)
