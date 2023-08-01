from datetime import (
    datetime,
    timedelta,
)
from typing import Any

from jose import jwt
import pytest

from msm.jwt import (
    create_token,
    InvalidToken,
    TOKEN_DURATION_MINUTES,
    validate_token,
)
from msm.settings import SETTINGS


class TestCreateToken:
    def test_create(self) -> None:
        subject = "subject"
        token = create_token(subject)
        payload = jwt.decode(
            token, SETTINGS.token_secret_key, algorithms=["HS256"]
        )
        assert payload["sub"] == subject
        assert payload["iss"] == "MAAS site manager"
        assert datetime.utcfromtimestamp(
            payload["exp"]
        ) < datetime.utcnow() + timedelta(minutes=TOKEN_DURATION_MINUTES)

    def test_create_with_duration(self) -> None:
        duration = timedelta(minutes=1)
        token = create_token("user@example.com", duration=duration)
        payload = jwt.decode(
            token, SETTINGS.token_secret_key, algorithms=["HS256"]
        )
        assert (
            datetime.utcfromtimestamp(payload["exp"])
            < datetime.utcnow() + duration
        )


class TestValidateToken:
    def test_valid(self) -> None:
        subject = "subject"
        token = create_token(subject)
        assert validate_token(token) == subject

    def test_invalid(self) -> None:
        with pytest.raises(InvalidToken):
            validate_token("garbage")

    @pytest.mark.parametrize(
        "data",
        [
            {"exp": datetime.utcnow() + timedelta(minutes=10)},
            {"sub": "subject"},
        ],
    )
    def test_invalid_missing_fields(self, data: dict[str, Any]) -> None:
        encoded = jwt.encode(
            data, SETTINGS.token_secret_key, algorithm="HS256"
        )
        with pytest.raises(InvalidToken):
            validate_token(str(encoded))

    def test_expired(self) -> None:
        token = create_token("subject", duration=timedelta(days=-1))
        with pytest.raises(InvalidToken):
            validate_token(token)
