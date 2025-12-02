"""Tests for alembic migration utilities."""

from unittest.mock import MagicMock, patch

from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection

from msm.apiserver.db.alembic import get_config, migrate_db


class TestAlembicUtilities:
    """Test cases for alembic utility functions."""

    def test_get_config_returns_config(self) -> None:
        """Test that get_config returns an Alembic Config object."""
        with patch("msm.apiserver.db.alembic.Settings") as mock_settings_class:
            # Configure mock settings
            mock_settings = MagicMock()
            mock_db_dsn = MagicMock()
            mock_db_dsn.render_as_string.return_value = (
                "postgresql://user:pass@localhost/db"
            )
            mock_settings.db_dsn.return_value = mock_db_dsn
            mock_settings_class.return_value = mock_settings

            # Call the function
            config = get_config()

            # Verify the result
            assert isinstance(config, Config)
            assert config.get_main_option("sqlalchemy.url") == (
                "postgresql://user:pass@localhost/db"
            )
            mock_settings.db_dsn.assert_called_once_with(async_engine=False)
            mock_db_dsn.render_as_string.assert_called_once_with(
                hide_password=False
            )

    def test_migrate_db_runs_migrations(self) -> None:
        """Test that migrate_db runs alembic migrations."""
        with (
            patch("msm.apiserver.db.alembic.get_config") as mock_get_config,
            patch(
                "msm.apiserver.db.alembic.ScriptDirectory"
            ) as mock_script_directory_class,
            patch(
                "msm.apiserver.db.alembic.EnvironmentContext"
            ) as mock_environment_context_class,
        ):
            # Configure mocks
            mock_config = MagicMock(spec=Config)
            mock_get_config.return_value = mock_config

            mock_script_directory = MagicMock(spec=ScriptDirectory)
            mock_script_directory._upgrade_revs.return_value = ["rev1", "rev2"]
            mock_script_directory_class.from_config.return_value = (
                mock_script_directory
            )

            mock_context = MagicMock(spec=EnvironmentContext)
            mock_environment_context_class.return_value = mock_context

            mock_connection = MagicMock(spec=Connection)

            # Call the function
            migrate_db(mock_connection)

            # Verify the calls
            mock_get_config.assert_called_once()
            mock_script_directory_class.from_config.assert_called_once_with(
                mock_config
            )
            mock_environment_context_class.assert_called_once_with(
                mock_config, mock_script_directory
            )
            mock_context.configure.assert_called_once()
            mock_context.run_migrations.assert_called_once()

            # Verify configure was called with correct arguments
            configure_call = mock_context.configure.call_args
            assert configure_call.kwargs["connection"] == mock_connection
            assert "target_metadata" in configure_call.kwargs
            assert "fn" in configure_call.kwargs

    def test_migrate_db_configure_parameters(self) -> None:
        """Test that migrate_db configures the context with correct parameters."""
        with (
            patch("msm.apiserver.db.alembic.get_config") as mock_get_config,
            patch(
                "msm.apiserver.db.alembic.ScriptDirectory"
            ) as mock_script_directory_class,
            patch(
                "msm.apiserver.db.alembic.EnvironmentContext"
            ) as mock_environment_context_class,
            patch("msm.apiserver.db.alembic.METADATA") as mock_metadata,
        ):
            # Configure mocks
            mock_config = MagicMock(spec=Config)
            mock_get_config.return_value = mock_config

            mock_script_directory = MagicMock(spec=ScriptDirectory)
            mock_script_directory_class.from_config.return_value = (
                mock_script_directory
            )

            mock_context = MagicMock(spec=EnvironmentContext)
            mock_environment_context_class.return_value = mock_context

            mock_connection = MagicMock(spec=Connection)

            # Call the function
            migrate_db(mock_connection)

            # Get the configure call arguments
            configure_call = mock_context.configure.call_args

            # Verify the metadata is passed correctly
            assert configure_call.kwargs["target_metadata"] == mock_metadata

            # Verify the connection is passed correctly
            assert configure_call.kwargs["connection"] == mock_connection

            # Test the fn callback
            fn = configure_call.kwargs["fn"]
            mock_rev = "test_rev"
            mock_upgrade_context = MagicMock()
            result = fn(mock_rev, mock_upgrade_context)

            # Verify the fn calls _upgrade_revs with correct arguments
            mock_script_directory._upgrade_revs.assert_called_once_with(
                "head", mock_rev
            )
