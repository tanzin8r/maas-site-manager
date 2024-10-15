from pydantic import BaseModel

from msm.jwt import DEFAULT_TOKEN_DURATION


class Settings(BaseModel):
    """Application settings that can be changed via the API."""

    service_url: str = ""
    token_lifetime_minutes: int = int(
        DEFAULT_TOKEN_DURATION.total_seconds() // 60
    )
    token_rotation_interval_minutes: int = int(
        ((DEFAULT_TOKEN_DURATION.total_seconds()) // 60) // 2
    )


class SettingsUpdate(BaseModel):
    """Change application settings."""

    service_url: str | None = None
    token_lifetime_minutes: int | None = None
    token_rotation_interval_minutes: int | None = None
