import asyncio
from pathlib import Path

from snaphelpers import Snap

from msm.db import (
    Database,
    check_server_version,
)
from msm.settings import Settings
from msm.snap._config import NginxConfig


def configure_hook(snap: Snap) -> None:
    """The `configure` hook called by the snap."""
    settings = Settings()
    if not settings.db_name:
        # service is not configured
        return

    _validate_settings(settings)
    _generate_config(settings, snap)
    snap.services.restart()


def _validate_settings(settings: Settings) -> None:
    # check connection to the database and server version
    db = Database(settings.db_dsn())
    asyncio.run(db.execute_in_transaction(check_server_version))


def _generate_config(settings: Settings, snap: Snap) -> None:
    nginx_config = NginxConfig(
        base_dir=snap.paths.snap,
        data_dir=snap.paths.data,
        port=settings.api_port,
        api_socket=Path(settings.api_socket),
    )
    nginx_config.write(snap.paths.data / "nginx.conf")
