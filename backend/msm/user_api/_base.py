from datetime import timedelta
from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .. import __version__
from ..db import (
    db_session,
    queries,
)
from ..schema import (
    CreateTokensRequest,
    CreateTokensResponse,
    JSONWebToken,
    PaginatedSites,
    PaginatedTokens,
    pagination_params,
    PaginationParams,
    User,
    UserLoginRequest,
)
from ..settings import SETTINGS
from ._forms import (
    site_filter_parameters,
    SiteFilterParams,
)
from ._jwt import (
    authenticate_user,
    create_access_token,
    get_authenticated_user,
)


async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"version": __version__}


async def sites(
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    session: AsyncSession = Depends(db_session),
    pagination_params: PaginationParams = Depends(pagination_params),
    filter_params: SiteFilterParams = Depends(site_filter_parameters),
) -> PaginatedSites:
    """Return all sites."""
    total, results = await queries.get_filtered_sites(
        session,
        offset=pagination_params.offset,
        limit=pagination_params.size,
        **filter_params._asdict(),
    )
    return PaginatedSites(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


async def tokens(
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    session: AsyncSession = Depends(db_session),
    pagination_params: PaginationParams = Depends(pagination_params),
) -> PaginatedTokens:
    """Return all tokens"""
    total, results = await queries.get_tokens(
        session, pagination_params.offset, pagination_params.size
    )
    return PaginatedTokens(
        total=total,
        page=pagination_params.page,
        size=pagination_params.size,
        items=list(results),
    )


async def tokens_post(
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    create_request: CreateTokensRequest,
    session: AsyncSession = Depends(db_session),
) -> CreateTokensResponse:
    """
    Create one or more tokens.
    Token duration (TTL) is expressed in seconds.
    """
    expired, tokens = await queries.create_tokens(
        session,
        create_request.duration,
        count=create_request.count,
    )
    return CreateTokensResponse(expired=expired, tokens=tokens)


async def login_for_access_token(
    user_login: UserLoginRequest,
    session: AsyncSession = Depends(db_session),
) -> JSONWebToken:
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
    return JSONWebToken(access_token=access_token, token_type="bearer")


async def read_users_me(
    authenticated_user: Annotated[User, Depends(get_authenticated_user)],
    session: AsyncSession = Depends(db_session),
) -> User:
    return authenticated_user
