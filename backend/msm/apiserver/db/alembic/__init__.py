from importlib.resources import files

from alembic.config import Config
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection

from msm.apiserver.db.tables import METADATA
from msm.common.settings import Settings


def get_config() -> Config:
    """Return the Alembic Config."""
    file_name = str(files("msm.apiserver.db.alembic") / "alembic.ini")
    config = Config(file_name)
    # inject the database DSN from settings in the configuration
    settings = Settings()
    config.set_main_option(
        "sqlalchemy.url",
        settings.db_dsn(async_engine=False).render_as_string(
            hide_password=False
        ),
    )
    return config


def migrate_db(connection: Connection) -> None:
    """Migrate the database using alembic."""
    config = get_config()
    script_directory = ScriptDirectory.from_config(config)
    context = EnvironmentContext(config, script_directory)
    context.configure(
        connection=connection,
        target_metadata=METADATA,
        fn=lambda rev, context: script_directory._upgrade_revs("head", rev),
    )
    context.run_migrations()
