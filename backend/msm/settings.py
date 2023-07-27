from pydantic import (
    Field,
    PostgresDsn,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(case_sensitive=True)

    db_dsn: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:msm@localhost/msm",
        validation_alias="MSM_DB_DSN",
    )  # type: ignore

    allowed_origins: list[str] = Field(
        default=[
            "http://localhost:8405",
            "http://127.0.0.1:8405",
            "http://[::1]:8405",
        ],
        validation_alias="MSM_ALLOWED_ORIGINS",
    )

    token_secret_key: str = Field(
        default="", validation_alias="MSM_TOKEN_SECRET_KEY"
    )


SETTINGS = Settings()
