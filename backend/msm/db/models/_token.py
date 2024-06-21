from pydantic import (
    AwareDatetime,
    BaseModel,
)

from msm.time import now_utc


class Token(BaseModel):
    """A registration token for a site."""

    id: int
    value: str
    audience: str
    purpose: str
    expired: AwareDatetime
    created: AwareDatetime
    site_id: int | None = None

    def is_expired(self) -> bool:
        """Whether the token is expired."""
        return self.expired < now_utc()
