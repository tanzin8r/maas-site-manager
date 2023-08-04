from datetime import (
    datetime,
    timedelta,
)
import os
from typing import cast

from jose import (
    jwt,
    JWTError,
)

TOKEN_ALGORITHM = "HS256"
TOKEN_SECRET_KEY_BYTES = 32
TOKEN_DURATION_MINUTES = 30


class InvalidToken(Exception):
    """Token is invalid"""


def generate_key() -> str:
    """Generate a random secret key."""
    return os.urandom(TOKEN_SECRET_KEY_BYTES).hex()


def create_token(
    subject: str, key: str = "", duration: timedelta | None = None
) -> str:
    """Create a JWT token and return it's encoded form as string."""
    if duration is None:
        duration = timedelta(minutes=TOKEN_DURATION_MINUTES)
    data = {
        "sub": subject,
        "iss": "MAAS site manager",
        "exp": datetime.utcnow() + duration,
    }
    encoded = jwt.encode(data, key, algorithm=TOKEN_ALGORITHM)
    return str(encoded)


def validate_token(token: str, key: str = "") -> str:
    """Validate a JWT token and return its subject."""
    try:
        payload = jwt.decode(token, key, algorithms=[TOKEN_ALGORITHM])
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
