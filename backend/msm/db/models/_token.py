from pydantic import (
    AwareDatetime,
    BaseModel,
)

from ...time import now_utc


class Token(BaseModel):
    """A registration token for a site."""

    id: int
    value: str
    expired: AwareDatetime
    created: AwareDatetime

    def is_expired(self) -> bool:
        """Whether the token is expired."""
        return self.expired < now_utc()
