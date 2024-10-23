from collections.abc import AsyncIterator, Iterator
from typing import Annotated, Self

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
import pytest

from msm.api.exceptions.constants import ExceptionCode
from msm.api.exceptions.middleware import request_validation_error_handler
from msm.api.exceptions.responses import ErrorResponseModel
from msm.api.user.handlers.users import passwords_match
from msm.schema._pagination import PaginatedResults, PaginationParams
from tests.fixtures.client import Client


class DummyDetailModel(BaseModel):
    data: str = Field(min_length=4)


class DummyModel(BaseModel):
    mandatory: str = Field(min_length=4, max_length=16)
    optional: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=16)
    confirm_password: str | None = Field(
        default=None, min_length=8, max_length=16
    )
    flag: bool | None = None
    value: int | None = None
    strlist: list[str] | None = None
    details: DummyDetailModel | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def passwords_match_check(self) -> Self:
        passwords_match(self, "password", "confirm_password")
        return self


class DummyGetResponse(PaginatedResults):
    """List of existing users."""

    items: list[DummyModel]


@pytest.fixture
def validation_app() -> Iterator[FastAPI]:
    app = FastAPI()
    app.add_exception_handler(
        RequestValidationError, request_validation_error_handler
    )

    @app.put("/dummy/{id}")
    async def put(request: Request, id: int, dummy: DummyModel) -> DummyModel:
        return dummy

    @app.get("/dummies")
    async def get(
        request: Request,
        pagination_params: Annotated[PaginationParams, Depends()],
    ) -> DummyGetResponse:
        return DummyGetResponse(
            total=1,
            page=1,
            size=1,
            items=[DummyModel(mandatory="goodstring")],
        )

    yield app


@pytest.fixture
async def validation_client(validation_app: FastAPI) -> AsyncIterator[Client]:
    """Client for the API."""
    async with Client(
        app=validation_app, base_url="http://test", trust_env=False
    ) as client:
        yield client


class TestValidationExceptionHandler:
    async def test_base_model(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1",
            json={"mandatory": "aaaa", "details": {"data": "1234"}},
        )
        assert response.status_code == 200

    async def test_missing_field(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1", json={"optional": "aaaa"}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "mandatory"
        assert err.error.details[0].reason == "Missing"
        assert err.error.details[0].messages[0] == "Field required"

    async def test_extra_field(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1", json={"mandatory": "valid", "extra": "unexpected"}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "extra"
        assert err.error.details[0].reason == "ExtraForbidden"
        assert (
            err.error.details[0].messages[0]
            == "Extra inputs are not permitted"
        )

    async def test_bool_wrong_type(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1", json={"mandatory": "valid", "flag": "invalid"}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "flag"
        assert err.error.details[0].reason == "BoolParsing"
        assert (
            err.error.details[0]
            .messages[0]
            .startswith("Input should be a valid boolean")
        )

    async def test_int_wrong_type(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1", json={"mandatory": "valid", "value": "invalid"}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "value"
        assert err.error.details[0].reason == "IntParsing"
        assert (
            err.error.details[0]
            .messages[0]
            .startswith("Input should be a valid integer")
        )

    async def test_string_wrong_type(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1", json={"mandatory": True}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "mandatory"
        assert err.error.details[0].reason == "StringType"
        assert (
            err.error.details[0].messages[0]
            == "Input should be a valid string"
        )

    async def test_string_too_short(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1", json={"mandatory": "abc"}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "mandatory"
        assert err.error.details[0].reason == "StringTooShort"
        assert (
            err.error.details[0]
            .messages[0]
            .startswith("String should have at least")
        )

    async def test_string_too_long(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1", json={"mandatory": "abcdabcdabcdabcdabcd"}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "mandatory"
        assert err.error.details[0].reason == "StringTooLong"
        assert (
            err.error.details[0]
            .messages[0]
            .startswith("String should have at most")
        )

    async def test_invalid_email(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1", json={"mandatory": "abcd", "email": "invalid"}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "email"
        assert err.error.details[0].reason == "ValueError"
        assert (
            err.error.details[0]
            .messages[0]
            .startswith("An email address must have an @-sign")
        )

    async def test_invalid_list_item(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1", json={"mandatory": "abcd", "strlist": ["ok", 1]}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "strlist[1]"
        assert err.error.details[0].reason == "StringType"
        assert (
            err.error.details[0]
            .messages[0]
            .startswith("Input should be a valid string")
        )

    async def test_model_validation(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1",
            json={
                "mandatory": "abcd",
                "password": "validsecret",
                "confirm_password": "invalidsecret",
            },
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "confirm_password"
        assert err.error.details[0].reason == "PasswordMismatch"
        assert (
            err.error.details[0].messages[0]
            == "'password' and 'confirm_password' do not match."
        )

    async def test_detail_validation(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/1",
            json={
                "mandatory": "abcd",
                "details": {"data": "abc"},
            },
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "body"
        assert err.error.details[0].field == "details.data"

    async def test_path_validation(self, validation_client: Client) -> None:
        response = await validation_client.put(
            "/dummy/asdf",
            json={"mandatory": "abcd"},
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "path"
        assert err.error.details[0].field == "id"
        assert err.error.details[0].reason == "IntParsing"

    async def test_get_ok(self, validation_client: Client) -> None:
        response = await validation_client.get("/dummies", params={"page": 1})
        assert response.status_code == 200

    async def test_get_query_validation(
        self, validation_client: Client
    ) -> None:
        response = await validation_client.get(
            "/dummies", params={"page": "asdf"}
        )
        assert response.status_code == 422

        err = ErrorResponseModel(**response.json())
        assert err.error.code == ExceptionCode.INVALID_PARAMS
        assert err.error.details is not None
        assert err.error.details[0].location == "query"
        assert err.error.details[0].field == "page"
        assert err.error.details[0].reason == "IntParsing"
