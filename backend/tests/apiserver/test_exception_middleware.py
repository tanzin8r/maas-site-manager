"""Tests for exception middleware."""

from collections.abc import AsyncIterator, Iterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from httpx import ASGITransport
from pydantic import BaseModel, Field
import pytest

from msm.apiserver.exceptions.catalog import (
    AlreadyExistsException,
    BadRequestException,
    FileTooLargeException,
    ForbiddenException,
    MsmBaseException,
    NotFoundException,
    UnauthorizedException,
)
from msm.apiserver.exceptions.constants import ExceptionCode
from msm.apiserver.exceptions.middleware import (
    ExceptionMiddleware,
    request_validation_error_handler,
)
from tests.fixtures.client import Client


@pytest.fixture
def app() -> Iterator[FastAPI]:
    """FastAPI app with ExceptionMiddleware."""
    app = FastAPI()
    app.add_middleware(ExceptionMiddleware)

    @app.get("/bad-request")
    async def bad_request(request: Request) -> None:
        raise BadRequestException(
            message="Bad request error",
            code=ExceptionCode.INVALID_PARAMS,
        )

    @app.get("/unauthorized")
    async def unauthorized(request: Request) -> None:
        raise UnauthorizedException(
            message="Unauthorized error",
            code=ExceptionCode.NOT_AUTHENTICATED,
        )

    @app.get("/forbidden")
    async def forbidden(request: Request) -> None:
        raise ForbiddenException(
            message="Forbidden error",
            code=ExceptionCode.MISSING_PERMISSIONS,
        )

    @app.get("/not-found")
    async def not_found(request: Request) -> None:
        raise NotFoundException(
            message="Not found error",
            code=ExceptionCode.MISSING_RESOURCE,
        )

    @app.get("/file-too-large")
    async def file_too_large(request: Request) -> None:
        raise FileTooLargeException(
            message="File too large error",
            code=ExceptionCode.FILE_TOO_LARGE,
        )

    @app.get("/already-exists")
    async def already_exists(request: Request) -> None:
        raise AlreadyExistsException(
            message="Already exists error",
            code=ExceptionCode.ALREADY_EXISTS,
        )

    @app.get("/msm-base")
    async def msm_base(request: Request) -> None:
        raise MsmBaseException(
            message="Base exception error",
            code=ExceptionCode.INVALID_PARAMS,
        )

    yield app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[Client]:
    """Client for the API."""
    async with Client(
        transport=ASGITransport(app=app),
        base_url="http://test",
        trust_env=False,
    ) as client:
        yield client


class TestExceptionMiddleware:
    """Test cases for ExceptionMiddleware."""

    async def test_bad_request_exception(self, client: Client) -> None:
        """Test BadRequestException is properly handled."""
        response = await client.get("/bad-request")
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["message"] == "Bad request error"
        assert data["error"]["code"] == ExceptionCode.INVALID_PARAMS

    async def test_unauthorized_exception(self, client: Client) -> None:
        """Test UnauthorizedException is properly handled."""
        response = await client.get("/unauthorized")
        assert response.status_code == 401
        data = response.json()
        assert data["error"]["message"] == "Unauthorized error"
        assert data["error"]["code"] == ExceptionCode.NOT_AUTHENTICATED

    async def test_forbidden_exception(self, client: Client) -> None:
        """Test ForbiddenException is properly handled."""
        response = await client.get("/forbidden")
        assert response.status_code == 403
        data = response.json()
        assert data["error"]["message"] == "Forbidden error"
        assert data["error"]["code"] == ExceptionCode.MISSING_PERMISSIONS

    async def test_not_found_exception(self, client: Client) -> None:
        """Test NotFoundException is properly handled."""
        response = await client.get("/not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["message"] == "Not found error"
        assert data["error"]["code"] == ExceptionCode.MISSING_RESOURCE

    async def test_file_too_large_exception(self, client: Client) -> None:
        """Test FileTooLargeException is properly handled."""
        response = await client.get("/file-too-large")
        assert response.status_code == 413
        data = response.json()
        assert data["error"]["message"] == "File too large error"
        assert data["error"]["code"] == ExceptionCode.FILE_TOO_LARGE

    async def test_already_exists_exception(self, client: Client) -> None:
        """Test AlreadyExistsException is properly handled."""
        response = await client.get("/already-exists")
        assert response.status_code == 409
        data = response.json()
        assert data["error"]["message"] == "Already exists error"
        assert data["error"]["code"] == ExceptionCode.ALREADY_EXISTS

    async def test_msm_base_exception(self, client: Client) -> None:
        """Test MsmBaseException is properly handled."""
        response = await client.get("/msm-base")
        assert response.status_code == 500
        data = response.json()
        assert data["error"]["message"] == "Base exception error"
        assert data["error"]["code"] == ExceptionCode.INVALID_PARAMS


class TestRequestValidationErrorHandler:
    """Test cases for request_validation_error_handler."""

    async def test_request_validation_error_handler(self) -> None:
        """Test request_validation_error_handler formats validation errors."""
        app = FastAPI()
        app.add_exception_handler(
            RequestValidationError, request_validation_error_handler
        )

        class TestModel(BaseModel):
            email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
            age: int = Field(..., ge=0, le=120)

        @app.post("/test")
        async def test_endpoint(data: TestModel) -> dict[str, bool]:
            return {"success": True}

        async with Client(
            transport=ASGITransport(app=app),
            base_url="http://test",
            trust_env=False,
        ) as client:
            # Test with invalid data
            response = await client.post(
                "/test",
                json={"email": "invalid-email", "age": "not-a-number"},
            )

            assert response.status_code == 422
            data = response.json()
            assert "error" in data
            assert "details" in data["error"]
            assert len(data["error"]["details"]) > 0
