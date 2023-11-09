import dataclasses
from datetime import (
    datetime,
    timedelta,
)
from functools import cached_property
import os
from typing import (
    Any,
    cast,
)

from jose import (
    jwt,
    JWTError,
)

TOKEN_ALGORITHM = "HS256"
TOKEN_SECRET_KEY_BYTES = 32
TOKEN_DURATION = timedelta(minutes=30)


class InvalidToken(Exception):
    """Token is invalid"""


def generate_key() -> str:
    """Generate a random secret key."""
    return os.urandom(TOKEN_SECRET_KEY_BYTES).hex()


@dataclasses.dataclass(frozen=True)
class JWT:
    payload: dict[str, Any]
    encoded: str

    _REQUIRED_FIELDS = frozenset(("iat", "iss", "exp", "sub"))

    @cached_property
    def issuer(self) -> str:
        return cast(str, self.payload["iss"])

    @cached_property
    def subject(self) -> str:
        return cast(str, self.payload["sub"])

    @cached_property
    def issued(self) -> datetime:
        return datetime.utcfromtimestamp(self.payload["iat"])

    @cached_property
    def expiration(self) -> datetime:
        return datetime.utcfromtimestamp(self.payload["exp"])

    @cached_property
    def data(self) -> dict[str, Any]:
        return {
            key: value
            for key, value in self.payload.items()
            if key not in self._REQUIRED_FIELDS
        }

    @classmethod
    def create(
        cls,
        issuer: str,
        subject: str,
        key: str = "",
        duration: timedelta = TOKEN_DURATION,
        data: dict[str, Any] | None = None,
    ) -> "JWT":
        """Create a JWT."""
        if data is None:
            data = {}
        issued = datetime.utcnow()
        expiration = issued + duration
        payload = data | {
            "sub": subject,
            "iss": issuer,
            "iat": issued,
            "exp": expiration,
        }
        encoded = jwt.encode(payload, key, algorithm=TOKEN_ALGORITHM)
        return cls(
            payload=payload,
            encoded=encoded,
        )

    @classmethod
    def decode(cls, encoded: str, key: str = "") -> "JWT":
        """Decode a token string."""
        try:
            payload = jwt.decode(encoded, key, algorithms=[TOKEN_ALGORITHM])
        except JWTError:
            raise InvalidToken()

        # check that all required fields are there
        if cls._REQUIRED_FIELDS - set(payload):
            raise InvalidToken()

        return JWT(
            payload=payload,
            encoded=encoded,
        )

    def validate(self, issuer: str) -> None:
        """Raise InvalidToken if the token is not valid."""
        expiration = datetime.utcfromtimestamp(self.payload["exp"])
        if expiration < datetime.utcnow():
            raise InvalidToken()

        if self.issuer != issuer:
            raise InvalidToken()
