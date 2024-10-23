"""Exception handling for the API"""

import http
from typing import Any

from fastapi import (
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

INVALID_TOKEN_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    headers={"WWW-Authenticate": "Bearer"},
    detail="Invalid token",
)


def not_found(entity: str) -> HTTPException:
    """Raise a 404 error for an something described by 'entity'
    entity should be uppercase
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity} does not exist.",
    )


async def http_exception_handler(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, StarletteHTTPException)

    status = http.HTTPStatus(exc.status_code)

    resp: dict[str, Any] = {
        "error": {
            "code": "".join(x for x in status.phrase.title() if x.isalnum()),
            "message": exc.detail,
        }
    }

    return JSONResponse(resp, status_code=exc.status_code)


def _build_json_path(loc: list[Any]) -> str:
    elements: list[str] = []

    for l in loc:
        if isinstance(l, int):
            elements.append(f"{elements.pop()}[{l}]")
        else:
            elements.append(l)

    return ".".join(elements)


async def request_validation_error_handler(
    request: Request, exc: Exception
) -> Response:
    """Handle model validation errors.

    FastAPI raises a RequestValidationError for any validation error that
    occurs during the request processing, from JSON decoder errors to pydantic
    field/model validation issues.

    The `loc` property of each error tells where the failure happened: path,
    query, header, cookie or body. It also contains the id of the field. The
    `type` is the name of the error, while `msg` contains a description of it.

    Pydantic model-level validations don't have an implicit field associated to
    it. In these cases we raise a `PydanticCustomError` and include the name of
    the field as a `loc` property in the context dict.
    """

    assert isinstance(exc, RequestValidationError)

    details: list[dict[str, Any]] = []

    for err in exc.errors():
        d = {
            "location": err["loc"][0],
            "reason": "".join(x for x in err["type"].title() if x.isalnum()),
            "field": _build_json_path(err["loc"][1:]),
            "messages": [err["msg"]],
        }
        if ctx := err.get("ctx", {}):
            # get extra insights from exception context
            if loc := ctx.get("loc", None):
                d["field"] = loc
            if msg := ctx.get("reason", None):
                d["messages"] = [msg]
        details.append(d)

    resp = {
        "error": {
            "code": "InvalidParameters",
            "message": "One or more request parameters are invalid",
            "details": details,
        }
    }

    return JSONResponse(resp, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
