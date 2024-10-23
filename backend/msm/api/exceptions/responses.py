from typing import Any, Self

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from msm.api.exceptions.catalog import BaseExceptionDetail, MsmBaseException
from msm.api.exceptions.constants import ExceptionCode


def _build_json_path(loc: list[Any]) -> str:
    elements: list[str] = []
    for l in loc:
        if isinstance(l, int) and elements:
            elements.append(f"{elements.pop()}[{l}]")
        else:
            elements.append(str(l))
    return ".".join(elements)


class ErrorBodyResponse(BaseModel):
    """Model for the error response body.

    Attributes:
        code: The exception code.
        message: A message explaining what went wrong.
        details: An optional list of additional details. Usually only used with
          RequestValidationError.
        status_code: The HTTP status code to be returned to the client.
    """

    code: ExceptionCode
    message: str
    details: list[BaseExceptionDetail] | None = None
    status_code: int = Field(
        default=status.HTTP_500_INTERNAL_SERVER_ERROR, exclude=True
    )

    @classmethod
    def from_exc(cls, exc: MsmBaseException) -> Self:
        return cls(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            status_code=exc.status_code,
        )

    @classmethod
    def from_validation_exc(cls, exc: RequestValidationError) -> Self:
        """Constructor for RequestValidationError.

        FastAPI raises a RequestValidationError for any validation error that
        occurs during the request processing, from JSON decoder errors to pydantic
        field/model validation issues.

        Each error in the `exc.errors()` is an instance of `pydantic_core.ErrorDetails`
        that has the following attributes:
            type: the name of the error
            msg: the description of the error
            loc: a tuple explaining where the failure happened. The first item
              could be one of: path, query, header, cookie, body. The next items
              specify the path of the wrong field. E.g. if the passed json is in
              the form `{"foo": {"bar": [0, "wrong-field"]}}` the loc parameter
              would be something like `(<location>, "foo", "bar", 1)`.
            ctx: additional context regarding the input data.

        Attributes:
            exc: The RequestValidationError raised by FastAPI.
        """
        details: list[BaseExceptionDetail] = []
        for err in exc.errors():
            d = BaseExceptionDetail(
                reason="".join(x for x in err["type"].title() if x.isalnum()),
                messages=[err["msg"]],
                location=err["loc"][0],
                field=_build_json_path(err["loc"][1:]),
            )
            if ctx := err.get("ctx", None):
                if loc := ctx.get("loc", None):
                    d.field = loc
                if msg := ctx.get("reason", None):
                    d.messages = [msg]

            details.append(d)
        return cls(
            code=ExceptionCode.INVALID_PARAMS,
            message="One or more request parameters are invalid",
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class ErrorResponseModel(BaseModel):
    error: ErrorBodyResponse


class ErrorResponse(JSONResponse):
    def __init__(self, err: ErrorResponseModel):
        super().__init__(
            content=jsonable_encoder(err, exclude_none=True),
            status_code=err.error.status_code,
        )
