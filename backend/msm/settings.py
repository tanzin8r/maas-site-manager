from typing import (
    Any,
    cast,
)

from pydantic import (
    Field,
    SecretStr,
)
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from snaphelpers import (
    is_snap,
    Snap,
    SnapConfigOptions,
)
from sqlalchemy import URL


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(case_sensitive=True)

    cors_allowed_origins: list[str] = Field(
        default=[
            "http://localhost:8405",
            "http://127.0.0.1:8405",
            "http://[::1]:8405",
        ],
        validation_alias="MSM_ALLOWED_ORIGINS",
    )
    dev_mode: bool = Field(default=False, validation_alias="MSM_DEV_MODE")
    db_host: str = Field(
        default="localhost",
        validation_alias="MSM_DB_HOST",
        json_schema_extra={"snap-key": "db.host"},
    )
    db_port: int = Field(
        default=5432,
        validation_alias="MSM_DB_PORT",
        json_schema_extra={"snap-key": "db.port"},
    )
    db_name: str | None = Field(
        default=None,
        validation_alias="MSM_DB_NAME",
        json_schema_extra={"snap-key": "db.name"},
    )
    db_user: str | None = Field(
        default=None,
        validation_alias="MSM_DB_USER",
        json_schema_extra={"snap-key": "db.user"},
    )
    db_password: SecretStr | None = Field(
        default=None,
        validation_alias="MSM_DB_PASSWORD",
        json_schema_extra={"snap-key": "db.password"},
    )
    api_port: int = Field(default=8000, validation_alias="MSM_API_PORT")
    api_socket: str = Field(
        default="api.socket", validation_alias="MSM_API_SOCKET"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        sources = super().settings_customise_sources(
            settings_cls,
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
        return sources + (SnapSettingsSource(settings_cls),)

    @property
    def db_dsn(self) -> URL:
        """The DSN, from configured settings."""
        password = (
            self.db_password.get_secret_value() if self.db_password else None
        )
        return URL.create(
            "postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            username=self.db_user,
            password=password,
        )


class SnapSettingsSource(PydanticBaseSettingsSource):
    """Source to get configurations options from the snap.

    This looks up fields in snap settings if they define a `snap-key` attribute
    in `json_schema_extra`.
    """

    # top-level snap config keys
    SNAP_KEYS = frozenset(["db"])

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        # empty method since settings are returned in __call__
        return None, "", False

    def __call__(self) -> dict[str, Any]:
        snap_configs = self._get_snap_configs()
        if snap_configs is None:
            return {}

        settings: dict[str, Any] = {}
        for field in self.settings_cls.model_fields.values():
            if not field.json_schema_extra:
                continue

            schema_extra = cast(dict[str, Any], field.json_schema_extra)
            if snap_key := schema_extra.get("snap-key"):
                if (value := snap_configs.get(snap_key)) is not None:
                    key = cast(str, field.validation_alias)
                    settings[key] = value

        return settings

    def _get_snap_configs(self) -> SnapConfigOptions | None:
        """Return snap configs, or None if not running in a snap."""
        if not is_snap():
            return None
        return Snap().config.get_options(*self.SNAP_KEYS)
