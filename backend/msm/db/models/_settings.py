from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings that can be changed via the API."""

    service_url: str = ""
    enrolment_url: str = ""
    token_lifetime_minutes: int = 0
    token_rotation_interval_minutes: int = 0
