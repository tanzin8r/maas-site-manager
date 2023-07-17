from passlib.context import CryptContext

_CONTEXT = CryptContext(schemes=["bcrypt"])


def hash_password(password: str) -> str:
    """Return the hash for a plain text password."""
    return _CONTEXT.hash(password)


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    """Verify a plain password against a password hash created by passlib."""
    return _CONTEXT.verify(plain_password, hashed_password)
