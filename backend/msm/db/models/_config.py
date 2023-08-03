from pydantic import BaseModel


class Config(BaseModel):
    """Application-level configuration."""

    token_secret_key: str = ""
