#
# This file is automatically loaded by Alembic when performing operations
#

from collections.abc import Iterable

from alembic import context
from alembic.migration import MigrationContext
from alembic.operations.ops import MigrationScript
from alembic.script.base import ScriptDirectory
from sqlalchemy import engine_from_config, pool

from msm.apiserver.db.alembic import get_config
from msm.apiserver.db.tables import METADATA


def process_revision_directives(
    context: MigrationContext,
    revision: str | Iterable[str | None],
    directives: list[MigrationScript],
) -> None:
    # override the revision ID incrementing the last used one
    migration_script: MigrationScript = directives[0]
    config = get_config()
    rev_id = 0
    if head_rev := ScriptDirectory.from_config(config).get_current_head():
        rev_id = int(head_rev) + 1
    migration_script.rev_id = f"{rev_id:04}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    config = get_config()
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=METADATA,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    config = get_config()
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=METADATA,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
