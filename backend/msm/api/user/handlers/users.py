from typing import (
    Annotated,
    Self,
)

from fastapi import (
    APIRouter,
    Depends,
)
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    model_validator,
)
from pydantic_core import PydanticCustomError

from msm.api.dependencies import services
from msm.api.exceptions.catalog import (
    BadRequestException,
    BaseExceptionDetail,
    ForbiddenException,
    NotFoundException,
)
from msm.api.exceptions.constants import ExceptionCode
from msm.api.exceptions.responses import (
    BadRequestErrorResponseModel,
    ForbiddenErrorResponseModel,
    NotFoundErrorResponseModel,
    UnauthorizedErrorResponseModel,
    ValidationErrorResponseModel,
)
from msm.api.user.auth import (
    authenticate_user,
    authenticated_admin,
    authenticated_user,
)
from msm.api.user.forms import (
    UserFilterParams,
    user_filter_params,
)
from msm.db import models
from msm.schema import (
    PaginatedResults,
    PaginationParams,
    SearchTextParam,
    SortParam,
    SortParamParser,
    search_text_param,
)
from msm.service import ServiceCollection

v1_router = APIRouter(prefix="/v1")

user_sort_params = SortParamParser(
    fields=[
        "email",
        "username",
        "full_name",
        "is_admin",
    ]
)


class User(BaseModel):
    """A user."""

    id: int
    email: EmailStr
    username: str
    full_name: str
    is_admin: bool

    @classmethod
    def from_model(cls, user: models.User) -> "User":
        """Return an instance from a User model."""
        return cls(**user.model_dump())


class UsersGetResponse(PaginatedResults[User]):
    """List of existing users."""


def passwords_match(
    model: BaseModel, field: str, confirmation_field: str
) -> None:
    if getattr(model, field) != getattr(model, confirmation_field):
        raise PydanticCustomError(
            "Password Mismatch",
            "'{ref}' and '{loc}' do not match.",
            {
                "ref": field,
                "loc": confirmation_field,
            },
        )


async def check_for_existing_user(
    services: ServiceCollection,
    username: str | None = None,
    email: str | None = None,
    exclude_id: int | None = None,
) -> list[BaseExceptionDetail]:
    """
    Check if the given user already exists. Return a list of BaseExceptionDetail for conflicting elements.
    """
    details = []
    conflicting = await services.users.exists(
        email=email, username=username, exclude_id=exclude_id
    )
    if conflicting is not None:
        for conflict in conflicting:
            details.append(
                BaseExceptionDetail(
                    reason=ExceptionCode.ALREADY_EXISTS,
                    messages=[f"{conflict} already exists"],
                    field=conflict,
                    location="body",
                )
            )
    return details


@v1_router.get(
    "/users",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        403: {"model": ForbiddenErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[models.User, Depends(authenticated_admin)],
    pagination_params: Annotated[PaginationParams, Depends()],
    filter_params: Annotated[UserFilterParams, Depends(user_filter_params)],
    sort_params: Annotated[list[SortParam], Depends(user_sort_params)],
    search_text: Annotated[SearchTextParam, Depends(search_text_param)],
) -> UsersGetResponse:
    """Return all users"""
    total, results = await services.users.get(
        sort_params=sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
        search_text=search_text.search_text,
        **filter_params._asdict(),
    )
    return UsersGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=[User.from_model(user) for user in results],
    )


@v1_router.get(
    "/users/me",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
    },
)
async def get_me(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
) -> User:
    """Render info about the authenticated user."""
    return User.from_model(authenticated_user)


class UsersPatchMeRequest(BaseModel):
    """User Edit Details about themselves."""

    username: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None

    @model_validator(mode="after")
    def check_at_least_one_field_present(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be set.")
        return self


@v1_router.patch(
    "/users/me",
    responses={
        400: {"model": BadRequestErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def patch_me(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    patch_request: UsersPatchMeRequest,
) -> User:
    """Update the details for a user"""
    details = await check_for_existing_user(
        services,
        patch_request.username,
        patch_request.email,
        authenticated_user.id,
    )
    if details:
        raise BadRequestException(
            code=ExceptionCode.ALREADY_EXISTS,
            message="Email or Username already in use.",
            details=details,
        )

    user = await services.users.update(
        authenticated_user.id, models.UserUpdate(**patch_request.model_dump())
    )
    return User.from_model(user)


class UsersPasswordPatchRequest(BaseModel):
    """User password change schema."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)

    @model_validator(mode="after")
    def passwords_match_check(self) -> Self:
        passwords_match(self, "new_password", "confirm_password")
        return self


@v1_router.patch(
    "/users/me/password",
    responses={
        400: {"model": BadRequestErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def patch_me_password(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[models.User, Depends(authenticated_user)],
    patch_request: UsersPasswordPatchRequest,
) -> None:
    """Modify the users password."""
    if await authenticate_user(
        services.users,
        authenticated_user.email,
        patch_request.current_password,
    ):
        await services.users.update_password(
            authenticated_user.id,
            patch_request.new_password,
        )
        return None
    raise BadRequestException(
        code=ExceptionCode.INVALID_CREDENTIALS,
        message="Invalid user credentials.",
        details=[
            BaseExceptionDetail(
                reason=ExceptionCode.INVALID_CREDENTIALS,
                messages=["Incorrect current password."],
                field="current_password",
                location="body",
            )
        ],
    )


@v1_router.get(
    "/users/{id}",
    responses={
        401: {"model": UnauthorizedErrorResponseModel},
        403: {"model": ForbiddenErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def get_id(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[models.User, Depends(authenticated_admin)],
    id: int,
) -> User:
    """Select a specific user"""

    if user := await services.users.get_by_id(id):
        return User.from_model(user)
    raise NotFoundException(
        code=ExceptionCode.MISSING_RESOURCE,
        message="Resource not found.",
        details=[
            BaseExceptionDetail(
                reason=ExceptionCode.MISSING_RESOURCE,
                messages=["User does not exist."],
                field="id",
                location="path",
            )
        ],
    )


class UsersPostRequest(BaseModel):
    """Request to create a User."""

    full_name: str
    username: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)
    is_admin: bool = False

    @model_validator(mode="after")
    def passwords_match_check(self) -> Self:
        passwords_match(self, "password", "confirm_password")
        return self


@v1_router.post(
    "/users",
    responses={
        400: {"model": BadRequestErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
        403: {"model": ForbiddenErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def post(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[models.User, Depends(authenticated_admin)],
    post_request: UsersPostRequest,
) -> User:
    """Create a user."""
    details = await check_for_existing_user(
        services,
        post_request.username,
        post_request.email,
    )
    if details:
        raise BadRequestException(
            code=ExceptionCode.ALREADY_EXISTS,
            message="Email or Username already in use.",
            details=details,
        )

    user = await services.users.create(
        models.UserCreate(**post_request.model_dump())
    )
    return User.from_model(user)


class UsersPatchRequest(BaseModel):
    """Request to edit details for a User."""

    full_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=100)
    confirm_password: str | None = Field(
        default=None, min_length=8, max_length=100
    )
    is_admin: bool | None = None

    @model_validator(mode="after")
    def passwords_match_check(self) -> Self:
        passwords_match(self, "password", "confirm_password")
        return self

    @model_validator(mode="after")
    def check_at_least_one_field_present(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be set.")
        return self


@v1_router.patch(
    "/users/{id}",
    responses={
        400: {"model": BadRequestErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
        403: {"model": ForbiddenErrorResponseModel},
        404: {"model": NotFoundErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def patch(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[models.User, Depends(authenticated_admin)],
    id: int,
    patch_request: UsersPatchRequest,
) -> User:
    """Admin action to update the details for a user."""

    if id == authenticated_admin.id and patch_request.is_admin is False:
        raise ForbiddenException(
            code=ExceptionCode.INVALID_PARAMS,
            message="A request parameter is invalid.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.INVALID_PARAMS,
                    messages=["Admin users cannot demote themselves."],
                    field="id",
                    location="path",
                )
            ],
        )

    if not await services.users.id_exists(id):
        raise NotFoundException(
            code=ExceptionCode.MISSING_RESOURCE,
            message="Resource not found.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.MISSING_RESOURCE,
                    messages=["User does not exist."],
                    field="id",
                    location="path",
                )
            ],
        )

    details = await check_for_existing_user(
        services, patch_request.username, patch_request.email, id
    )
    if details:
        raise BadRequestException(
            code=ExceptionCode.ALREADY_EXISTS,
            message="Email or Username already in use.",
            details=details,
        )

    user = await services.users.update(
        id, models.UserUpdate(**patch_request.model_dump())
    )
    return User.from_model(user)


@v1_router.delete(
    "/users/{id}",
    status_code=204,
    responses={
        400: {"model": BadRequestErrorResponseModel},
        401: {"model": UnauthorizedErrorResponseModel},
        403: {"model": ForbiddenErrorResponseModel},
        422: {"model": ValidationErrorResponseModel},
    },
)
async def delete(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[models.User, Depends(authenticated_admin)],
    id: int,
) -> None:
    """Delete a user from the database."""
    if authenticated_admin.id == id:
        raise BadRequestException(
            code=ExceptionCode.INVALID_PARAMS,
            message="A request parameter is invalid.",
            details=[
                BaseExceptionDetail(
                    reason=ExceptionCode.INVALID_PARAMS,
                    messages=["Cannot delete the current user."],
                    field="id",
                    location="path",
                )
            ],
        )
    await services.users.delete(id)
    return None
