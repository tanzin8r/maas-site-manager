import dataclasses
from datetime import (
    datetime,
    timedelta,
)
from enum import StrEnum
from functools import cached_property
import os
from typing import (
    Any,
    cast,
)

from jose import (
    JWTError,
    jwt,
)

from msm.common.time import (
    now_utc,
    utc_from_timestamp,
)

TOKEN_ALGORITHM = "HS256"
TOKEN_SECRET_KEY_BYTES = 32
DEFAULT_TOKEN_DURATION = timedelta(days=7)
DEFAULT_TOKEN_ROTATION = (
    int(DEFAULT_TOKEN_DURATION.total_seconds()) // 60
) // 2


class InvalidToken(Exception):
    """Token is invalid"""


def generate_key() -> str:
    """Generate a random secret key."""
    return os.urandom(TOKEN_SECRET_KEY_BYTES).hex()


class TokenAudience(StrEnum):
    """Valid values for token audience."""

    API = "api"
    SITE = "site"
    WORKER = "worker"


class TokenPurpose(StrEnum):
    """Valid values for the token purpose."""

    ENROLMENT = "enrollment"
    ACCESS = "access"


@dataclasses.dataclass(frozen=True)
class JWT:
    payload: dict[str, Any]
    encoded: str

    _REQUIRED_FIELDS: frozenset[str] = frozenset(
        ("aud", "iat", "iss", "exp", "sub")
    )

    @cached_property
    def issuer(self) -> str:
        return cast(str, self.payload["iss"])

    @cached_property
    def subject(self) -> str:
        return cast(str, self.payload["sub"])

    @cached_property
    def issued(self) -> datetime:
        return utc_from_timestamp(self.payload["iat"])

    @cached_property
    def expiration(self) -> datetime:
        return utc_from_timestamp(self.payload["exp"])

    @cached_property
    def audience(self) -> list[TokenAudience]:
        return [TokenAudience(entry) for entry in self.payload["aud"]]

    @cached_property
    def purpose(self) -> TokenPurpose | None:
        value = self.payload.get("purpose")
        return TokenPurpose(value) if value else None

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
        audience: TokenAudience,
        service_url: str | None = None,
        purpose: TokenPurpose | None = None,
        data: dict[str, Any] | None = None,
        duration: timedelta = DEFAULT_TOKEN_DURATION,
        key: str = "",
    ) -> "JWT":
        """Create a JWT."""
        if data is None:
            data = {}

        issued = now_utc()
        expiration = issued + duration
        payload = data | {
            "sub": subject,
            "iss": issuer,
            "iat": issued,
            "exp": expiration,
            "aud": [audience],
        }
        if purpose:
            payload["purpose"] = purpose
        if service_url:
            payload["service-url"] = service_url
        encoded = jwt.encode(payload, key, algorithm=TOKEN_ALGORITHM)
        return cls(
            payload=payload,
            encoded=encoded,
        )

    @classmethod
    def decode(
        cls,
        encoded: str,
        key: str = "",
        issuer: str | None = None,
        audience: TokenAudience | None = None,
        purpose: TokenPurpose | None = None,
    ) -> "JWT":
        """Decode a token string."""
        try:
            payload = jwt.decode(
                encoded,
                key,
                algorithms=[TOKEN_ALGORITHM],
                issuer=issuer,
                audience=str(audience) if audience else None,
            )
        except JWTError:
            raise InvalidToken()

        # check that all required fields are there
        if cls._REQUIRED_FIELDS - set(payload):
            raise InvalidToken()
        token = JWT(
            payload=payload,
            encoded=encoded,
        )

        if purpose and token.purpose != purpose:
            raise InvalidToken()

        return token
