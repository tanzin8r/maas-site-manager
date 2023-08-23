import asyncio
import os
from pathlib import Path

from snaphelpers import Snap

from msm.db import (
    check_server_version,
    Database,
)
from msm.settings import Settings

from ._config import NginxConfig
from ._env import environ_from_snap


def configure_hook(snap: Snap) -> None:
    """The `configure` hook called by the snap."""
    env = environ_from_snap()
    if not env:
        # no config option has been set
        return
    os.environ.update(env)
    settings = Settings()

    _validate_settings(settings)
    _generate_config(settings, snap)
    snap.services.restart()


def _validate_settings(settings: Settings) -> None:
    # check connection to the database and server version
    db = Database(settings.db_dsn)
    asyncio.run(db.execute_in_transaction(check_server_version))


def _generate_config(settings: Settings, snap: Snap) -> None:
    nginx_config = NginxConfig(
        base_dir=snap.paths.snap,
        data_dir=snap.paths.data,
        port=settings.user_api_port,
        user_api_socket=Path(settings.user_api_socket),
    )
    nginx_config.write(snap.paths.data / "nginx.conf")
