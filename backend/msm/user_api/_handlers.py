from datetime import timedelta
from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import (
    db_session,
    queries,
)
from ..db.models import User
from ..db.queries import InvalidPendingSites
from ..schema import (
    pagination_params,
    PaginationParams,
)
from ..schema._sorting import (
    SortParam,
    SortParamParser,
)
from ..settings import SETTINGS
from ._csv import CSVResponse
from ._forms import (
    site_filter_parameters,
    SiteFilterParams,
)
from ._jwt import (
    authenticate_user,
    create_access_token,
    get_authenticated_admin,
    get_authenticated_user,
)
from ._schema import (
    LoginPostRequest,
    LoginPostResponse,
    PendingSitesGetResponse,
    PendingSitesPostRequest,
    RootGetResponse,
    SitesGetResponse,
    TokensGetResponse,
    TokensPostRequest,
    TokensPostResponse,
    UsersGetResponse,
)

site_sort_parameters = SortParamParser(
    fields=[
        "name",
        "name_unique",
        "country",
        "city",
        "region",
        "street",
        "timezone",
        "connection_status",
    ]
)


async def root_get(request: Request) -> RootGetResponse:
    """Root endpoint."""
    return RootGetResponse(version=request.app.version)


async def sites_get(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    pagination_params: PaginationParams = Depends(pagination_params),
    filter_params: SiteFilterParams = Depends(site_filter_parameters),
    sort_params: list[SortParam] = Depends(site_sort_parameters),
) -> SitesGetResponse:
    """Return accepted sites."""
    total, results = await queries.get_sites(
        session,
        sort_params=sort_params,
        offset=pagination_params.offset,
        limit=pagination_params.size,
        **filter_params._asdict(),
    )
    return SitesGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


async def pending_sites_get(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    pagination_params: PaginationParams = Depends(pagination_params),
) -> PendingSitesGetResponse:
    """Return pending sites."""
    total, results = await queries.get_pending_sites(
        session,
        offset=pagination_params.offset,
        limit=pagination_params.size,
    )
    return PendingSitesGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


async def pending_sites_post(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    action: PendingSitesPostRequest,
) -> None:
    """Accept or reject pending sites."""
    try:
        await queries.accept_reject_pending_sites(
            session,
            action.ids,
            action.accept,
        )
    except InvalidPendingSites as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(error), "ids": error.ids},
        )

    return None


async def tokens_get(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    pagination_params: PaginationParams = Depends(pagination_params),
) -> TokensGetResponse:
    """Return all tokens"""
    total, results = await queries.get_tokens(
        session, pagination_params.offset, pagination_params.size
    )
    return TokensGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


async def tokens_export_get(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
) -> CSVResponse:
    tokens = await queries.get_active_tokens(session)
    return CSVResponse(content=tokens)


async def tokens_post(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    create_request: TokensPostRequest,
) -> TokensPostResponse:
    """
    Create one or more tokens.
    Token duration (TTL) is expressed in seconds.
    """
    expired, tokens = await queries.create_tokens(
        session,
        create_request.duration,
        count=create_request.count,
    )
    return TokensPostResponse(expired=expired, tokens=tokens)


async def login_post(
    session: Annotated[AsyncSession, Depends(db_session)],
    user_login: LoginPostRequest,
) -> LoginPostResponse:
    user = await authenticate_user(
        session, user_login.username, user_login.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=SETTINGS.access_token_expire_minutes
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return LoginPostResponse(access_token=access_token, token_type="bearer")


async def users_get(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_admin: Annotated[User, Depends(get_authenticated_admin)],
    pagination_params: PaginationParams = Depends(pagination_params),
) -> UsersGetResponse:
    """Return all users"""
    total, results = await queries.get_users(
        session, pagination_params.offset, pagination_params.size
    )
    return UsersGetResponse(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


async def users_delete(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_admin: Annotated[User, Depends(get_authenticated_admin)],
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
    await queries.delete_user(session, user_id)
    return None


async def users_me_get(
    session: Annotated[AsyncSession, Depends(db_session)],
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
) -> User:
    """Render info about the authenticated user."""
    return authenticated_user
