from logging import getLogger
from os import (
    environ,
    getenv,
)

from pydantic import (
    BaseSettings,
    Field,
    PostgresDsn,
)

logger = getLogger("site-manager.settings")


class Settings(BaseSettings):
    """API settings."""

    db_dsn: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:msm@localhost/msm",
        env="MSM_DB_DSN",
    )  # type: ignore

    default_page_size: int = Field(
        default=20, gte=1, env="MSM_DEFAULT_PAGE_SIZE"
    )

    max_page_size: int = Field(default=100, gte=1, env="MSM_MAX_PAGE_SIZE")

    allowed_origins: list[str] = Field(
        default=[
            "http://localhost:8405",
            "http://127.0.0.1:8405",
            "http://[::1]:8405",
        ],
        env="MSM_ALLOWED_ORIGINS",
    )

    secret_key: str = getenv("SECRET_KEY", "")
    if "SECRET_KEY" not in environ:
        logger.critical("Secret key not defined in environment!")

    algorithm = "HS256"

    access_token_expire_minutes = int(getenv("TOKEN_EXPIRATION_TIME", 30))


SETTINGS = Settings()
