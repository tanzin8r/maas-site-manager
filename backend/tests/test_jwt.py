from datetime import timedelta
from typing import Any

from jose import jwt
import pytest

from msm.jwt import (
    JWT,
    TOKEN_DURATION,
    InvalidToken,
    TokenAudience,
    TokenPurpose,
)
from msm.time import (
    now_utc,
    utc_from_timestamp,
)

SAMPLE_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"


class TestJWT:
    @pytest.mark.parametrize("key", ["", SAMPLE_KEY])
    def test_create(self, key: str) -> None:
        issuer = "issuer"
        subject = "subject"
        token = JWT.create(
            issuer=issuer,
            subject=subject,
            audience=TokenAudience.API,
            key=key,
        )
        payload = jwt.decode(
            token.encoded, key, algorithms=["HS256"], audience="api"
        )
        assert payload["sub"] == subject
        assert payload["iss"] == issuer
        assert utc_from_timestamp(payload["exp"]) < now_utc() + TOKEN_DURATION
        assert utc_from_timestamp(payload["iat"]) < now_utc()
        assert payload["aud"] == ["api"]

    @pytest.mark.parametrize("key", ["", SAMPLE_KEY])
    def test_create_with_duration(self, key: str) -> None:
        duration = timedelta(minutes=1)
        token = JWT.create(
            issuer="issuer",
            subject="user@example.com",
            audience=TokenAudience.API,
            duration=duration,
            key=key,
        )
        payload = jwt.decode(
            token.encoded, key, algorithms=["HS256"], audience="api"
        )
        assert utc_from_timestamp(payload["exp"]) < now_utc() + duration
        assert utc_from_timestamp(payload["iat"]) < now_utc()

    def test_decode_valid(self) -> None:
        data = {"foo": "bar"}
        token = JWT.create(
            issuer="issuer",
            subject="subject",
            audience=TokenAudience.API,
            data=data,
        )
        assert (
            JWT.decode(
                token.encoded, issuer="issuer", audience=TokenAudience.API
            )
            == token
        )

    def test_decode_with_purpose(self) -> None:
        token = JWT.create(
            issuer="issuer",
            subject="subject",
            audience=TokenAudience.SITE,
            purpose=TokenPurpose.ENROLMENT,
        )
        assert (
            JWT.decode(
                token.encoded,
                issuer="issuer",
                audience=TokenAudience.SITE,
                purpose=TokenPurpose.ENROLMENT,
            )
            == token
        )

    def test_decode_invalid(self) -> None:
        with pytest.raises(InvalidToken):
            JWT.decode("garbage", issuer="issuer")

    @pytest.mark.parametrize(
        "data",
        [
            {"exp": now_utc() + timedelta(minutes=10)},
            {"sub": "subject"},
        ],
    )
    def test_decode_invalid_missing_fields(self, data: dict[str, Any]) -> None:
        encoded = jwt.encode(data, key=SAMPLE_KEY, algorithm="HS256")
        with pytest.raises(InvalidToken):
            JWT.decode(str(encoded), issuer="issuer")

    def test_decode_expired(self) -> None:
        issuer = "issuer"
        token = JWT.create(
            issuer=issuer,
            subject="subject",
            audience=TokenAudience.SITE,
            duration=timedelta(days=-1),
        )
        with pytest.raises(InvalidToken):
            JWT.decode(
                token.encoded, issuer=issuer, audience=TokenAudience.SITE
            )

    def test_decode_different_issuer(self) -> None:
        token = JWT.create(
            issuer="other", subject="subject", audience=TokenAudience.API
        )
        with pytest.raises(InvalidToken):
            JWT.decode(
                token.encoded, issuer="issuer", audience=TokenAudience.API
            )

    def test_decode_invalid_audience(self) -> None:
        token = JWT.create(
            issuer="other", subject="subject", audience=TokenAudience.API
        )
        with pytest.raises(InvalidToken):
            JWT.decode(
                token.encoded, issuer="issuer", audience=TokenAudience.SITE
            )

    def test_decode_missing_purpose(self) -> None:
        token = JWT.create(
            issuer="other",
            subject="subject",
            audience=TokenAudience.SITE,
        )
        with pytest.raises(InvalidToken):
            JWT.decode(
                token.encoded,
                issuer="issuer",
                audience=TokenAudience.SITE,
                purpose=TokenPurpose.ENROLMENT,
            )
