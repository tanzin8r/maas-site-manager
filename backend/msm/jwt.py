from datetime import (
    datetime,
    timedelta,
)
from typing import cast

from jose import (
    jwt,
    JWTError,
)

from .settings import SETTINGS


class InvalidToken(Exception):
    """Token is invalid"""


def create_token(subject: str, duration: timedelta | None = None) -> str:
    """Create a JWT token and return it's encoded form as string."""
    if duration is None:
        duration = timedelta(minutes=SETTINGS.access_token_expire_minutes)
    data = {
        "sub": subject,
        "iss": "MAAS site manager",
        "exp": datetime.utcnow() + duration,
    }
    encoded = jwt.encode(
        data, SETTINGS.secret_key, algorithm=SETTINGS.algorithm
    )
    return str(encoded)


def validate_token(token: str) -> str:
    """Validate a JWT token and return its subject."""
    try:
        payload = jwt.decode(
            token, SETTINGS.secret_key, algorithms=[SETTINGS.algorithm]
        )
    except JWTError:
        raise InvalidToken()
    subject = payload.get("sub")
    if subject is None:
        raise InvalidToken()
    expiration = payload.get("exp")
    if (
        not expiration
        or datetime.fromtimestamp(expiration) < datetime.utcnow()
    ):
        raise InvalidToken()
    return cast(str, subject)
