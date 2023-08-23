from snaphelpers import (
    is_snap,
    Snap,
)

CONFIG_VARS = (
    ("db.host", "MSM_DB_HOST"),
    ("db.port", "MSM_DB_PORT"),
    ("db.name", "MSM_DB_NAME"),
    ("db.user", "MSM_DB_USER"),
    ("db.password", "MSM_DB_PASSWORD"),
)


def environ_from_snap() -> dict[str, str]:
    """Return MSM_* environment variables from snap config."""
    if not is_snap():
        return {}

    environ = {}
    options = Snap().config.get_options("db")
    for config, var in CONFIG_VARS:
        if (value := options.get(config)) is not None:
            environ[var] = value

    return environ
