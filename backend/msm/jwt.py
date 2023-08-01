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

TOKEN_ALGORITHM = "HS256"
TOKEN_DURATION_MINUTES = 30


class InvalidToken(Exception):
    """Token is invalid"""


def create_token(subject: str, duration: timedelta | None = None) -> str:
    """Create a JWT token and return it's encoded form as string."""
    if duration is None:
        duration = timedelta(minutes=TOKEN_DURATION_MINUTES)
    data = {
        "sub": subject,
        "iss": "MAAS site manager",
        "exp": datetime.utcnow() + duration,
    }
    encoded = jwt.encode(
        data, SETTINGS.token_secret_key, algorithm=TOKEN_ALGORITHM
    )
    return str(encoded)


def validate_token(token: str) -> str:
    """Validate a JWT token and return its subject."""
    try:
        payload = jwt.decode(
            token, SETTINGS.token_secret_key, algorithms=[TOKEN_ALGORITHM]
        )
    except JWTError:
        raise InvalidToken()
    subject = payload.get("sub")
    if subject is None:
        raise InvalidToken()
    expiration = payload.get("exp")
    if (
        not expiration
        or datetime.utcfromtimestamp(expiration) < datetime.utcnow()
    ):
        raise InvalidToken()
    return cast(str, subject)
