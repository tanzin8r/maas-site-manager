from typing import (
    Annotated,
    Any,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from ...db.models import (
    User,
    UserCreate,
    UserUpdate,
)
from ...schema import (
    PaginatedResults,
    pagination_params,
    PaginationParams,
    search_text_param,
    SearchTextParam,
    SortParam,
    SortParamParser,
)
from ...service import ServiceCollection
from .._auth import (
    authenticate_user,
    authenticated_admin,
    authenticated_user,
)
from .._dependencies import services
from .._forms import (
    user_filter_params,
    UserFilterParams,
)

router = APIRouter()

user_sort_params = SortParamParser(
    fields=[
        "email",
        "username",
        "full_name",
        "is_admin",
    ]
)


class UsersGetResponse(PaginatedResults):
    """List of existing users."""

    items: list[User]


@router.get("/users")
async def get(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[User, Depends(authenticated_admin)],
    pagination_params: PaginationParams = Depends(pagination_params),
    filter_params: UserFilterParams = Depends(user_filter_params),
    sort_params: list[SortParam] = Depends(user_sort_params),
    search_text: SearchTextParam = Depends(search_text_param),
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
        items=list(results),
    )


@router.get("/users/me")
async def get_me(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
) -> User:
    """Render info about the authenticated user."""
    return authenticated_user


class UsersPatchMeRequest(BaseModel):
    """User Edit Details about themselves."""

    username: str | None = None
    full_name: str | None = None
    email: str | None = None


@router.patch("/users/me")
async def patch_me(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    patch_request: UsersPatchMeRequest,
) -> User:
    """Update the details for a user"""

    if all(v is None for v in patch_request.model_dump().values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Request body empty."},
        )

    if await services.users.exists(
        email=patch_request.email,
        username=patch_request.username,
        exclude_id=authenticated_user.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Email or Username already in use."},
        )

    user = await services.users.update(
        authenticated_user.id, UserUpdate(**patch_request.model_dump())
    )
    return user


class UsersPasswordPatchRequest(BaseModel):
    """User password change schema."""

    current_password: str
    new_password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)

    @model_validator(mode="before")
    def passwords_match(cls, values: Any) -> Any:
        if values.get("new_password") != values.get("confirm_password"):
            raise ValueError("Provided passwords do not match.")
        return values


@router.patch("/users/me/password")
async def patch_me_password(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_user: Annotated[User, Depends(authenticated_user)],
    post_request: UsersPasswordPatchRequest,
) -> None:
    """Modify the users password."""
    if await authenticate_user(
        services.users, authenticated_user.email, post_request.current_password
    ):
        await services.users.update_password(
            authenticated_user.id,
            post_request.new_password,
        )
        return None
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"message": "Incorrect password for user."},
    )


@router.get("/users/{user_id}")
async def get_id(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[User, Depends(authenticated_admin)],
    user_id: int,
) -> User:
    """
    Select a specific user by id
    """

    if user := await services.users.get_by_id(user_id):
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": "User does not exist."},
    )


class UsersPostRequest(BaseModel):
    """
    Request to create a User.
    """

    full_name: str
    username: str
    email: str
    password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)
    is_admin: bool = False

    @model_validator(mode="before")
    def passwords_match(cls, values: Any) -> Any:
        if values.get("password") != values.get("confirm_password"):
            raise ValueError("Provided passwords do not match.")
        return values


@router.post("/users")
async def post(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[User, Depends(authenticated_admin)],
    request: UsersPostRequest,
) -> User:
    """
    Create a user.
    """
    if await services.users.exists(
        email=request.email, username=request.username
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Email or Username already in use."},
        )
    return await services.users.create(UserCreate(**request.model_dump()))


class UsersPatchRequest(BaseModel):
    """User Edit Details request schema."""

    full_name: str | None = None
    username: str | None = None
    email: str | None = None
    password: str | None = Field(default=None, min_length=8, max_length=100)
    confirm_password: str | None = Field(
        default=None, min_length=8, max_length=100
    )
    is_admin: bool | None = None

    @model_validator(mode="before")
    def passwords_match(cls, values: Any) -> Any:
        if values.get("password") != values.get("confirm_password"):
            raise ValueError("Provided passwords do not match.")
        return values


@router.patch("/users/{user_id}")
async def patch(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[User, Depends(authenticated_admin)],
    user_id: int,
    patch_request: UsersPatchRequest,
) -> User:
    """Admin Update the details for a user"""

    if user_id == authenticated_admin.id and patch_request.is_admin is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Admin users cannot demote themselves."},
        )

    if all(v is None for v in patch_request.model_dump().values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Request body empty."},
        )

    if not await services.users.id_exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "User does not exist."},
        )

    if await services.users.exists(
        email=patch_request.email,
        username=patch_request.username,
        exclude_id=user_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Email or Username already in use."},
        )

    return await services.users.update(
        user_id, UserUpdate(**patch_request.model_dump())
    )


@router.delete("/users/{user_id}", status_code=204)
async def delete(
    services: Annotated[ServiceCollection, Depends(services)],
    authenticated_admin: Annotated[User, Depends(authenticated_admin)],
    user_id: int,
) -> None:
    """
    Delete a user from the database.
    Don't allow a user to delete themselves.
    """
    if authenticated_admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Cannot delete the current user."},
        )
    await services.users.delete(user_id)
    return None
