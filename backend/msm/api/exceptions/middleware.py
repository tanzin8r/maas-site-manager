"""Exception handling for the API"""

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from msm.api.exceptions.catalog import MsmBaseException
from msm.api.exceptions.responses import (
    ErrorBodyResponse,
    ErrorResponse,
    ErrorResponseModel,
)


class ExceptionMiddleware(BaseHTTPMiddleware):
    """Middleware to catch all the custom defined exceptions."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)
        except MsmBaseException as e:
            err = ErrorResponseModel(error=ErrorBodyResponse.from_exc(e))
            return ErrorResponse(err=err)


async def request_validation_error_handler(
    request: Request, exc: Exception
) -> ErrorResponse:
    """Middleware to handle RequestValidationError exceptions."""
    assert isinstance(exc, RequestValidationError)
    err = ErrorResponseModel(error=ErrorBodyResponse.from_validation_exc(exc))
    return ErrorResponse(err=err)
