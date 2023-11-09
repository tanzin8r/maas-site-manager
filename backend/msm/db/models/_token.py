from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    """A registration token for a site."""

    id: int
    value: str
    expired: datetime
    created: datetime

    def is_expired(self) -> bool:
        """Whether the token is expired."""
        return self.expired < datetime.utcnow()
