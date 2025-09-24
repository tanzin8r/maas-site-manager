from pydantic import BaseModel


class Config(BaseModel):
    """Application-level configuration."""

    # Unique identifier for a Site Manager installation
    service_identifier: str = ""
    # Key used to sign JWTs
    token_secret_key: str = ""
