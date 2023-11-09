from datetime import (
    datetime,
    timedelta,
)
from typing import Any

from jose import jwt
import pytest

from msm.jwt import (
    InvalidToken,
    JWT,
    TOKEN_DURATION,
)

SAMPLE_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"


class TestJWT:
    @pytest.mark.parametrize("key", ["", SAMPLE_KEY])
    def test_create(self, key: str) -> None:
        issuer = "issuer"
        subject = "subject"
        token = JWT.create(issuer=issuer, subject=subject, key=key)
        payload = jwt.decode(token.encoded, key, algorithms=["HS256"])
        assert payload["sub"] == subject
        assert payload["iss"] == issuer
        assert (
            datetime.utcfromtimestamp(payload["exp"])
            < datetime.utcnow() + TOKEN_DURATION
        )
        assert datetime.utcfromtimestamp(payload["iat"]) < datetime.utcnow()

    @pytest.mark.parametrize("key", ["", SAMPLE_KEY])
    def test_create_with_duration(self, key: str) -> None:
        duration = timedelta(minutes=1)
        token = JWT.create(
            issuer="issuer",
            subject="user@example.com",
            key=key,
            duration=duration,
        )
        payload = jwt.decode(token.encoded, key, algorithms=["HS256"])
        assert (
            datetime.utcfromtimestamp(payload["exp"])
            < datetime.utcnow() + duration
        )
        assert datetime.utcfromtimestamp(payload["iat"]) < datetime.utcnow()

    def test_decode_valid(self) -> None:
        data = {"foo": "bar"}
        token = JWT.create(issuer="issuer", subject="subject", data=data)
        assert JWT.decode(token.encoded) == token

    def test_decode_invalid(self) -> None:
        with pytest.raises(InvalidToken):
            JWT.decode("garbage")

    @pytest.mark.parametrize(
        "data",
        [
            {"exp": datetime.utcnow() + timedelta(minutes=10)},
            {"sub": "subject"},
        ],
    )
    def test_decode_invalid_missing_fields(self, data: dict[str, Any]) -> None:
        encoded = jwt.encode(data, key=SAMPLE_KEY, algorithm="HS256")
        with pytest.raises(InvalidToken):
            JWT.decode(str(encoded))

    def test_validate_expired(self) -> None:
        issuer = "issuer"
        token = JWT.create(
            issuer=issuer, subject="subject", duration=timedelta(days=-1)
        )
        with pytest.raises(InvalidToken):
            token.validate(issuer=issuer)

    def test_validate_different_issuer(self) -> None:
        token = JWT.create(issuer="other", subject="subject")
        with pytest.raises(InvalidToken):
            token.validate(issuer="issuer")
