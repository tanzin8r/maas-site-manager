from operator import or_

from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models
from ...schema import SortParam
from .._tables import User
from ._count import row_count
from ._search import (
    filters_from_arguments,
    order_by_from_arguments,
)


async def user_id_exists(session: AsyncSession, user_id: int) -> bool:
    search = await session.execute(
        select(User.c.id).select_from(User).filter(User.c.id == user_id)
    )
    return search.first() is not None


async def user_exists(
    session: AsyncSession, email: str, username: str
) -> bool:
    search = await session.execute(
        select(User.c.id)
        .select_from(User)
        .filter(
            or_(
                User.c.email == email,
                User.c.username == username,
            )
        )
    )
    return search.first() is not None


async def get_user(
    session: AsyncSession, email: str
) -> models.UserWithPassword | None:
    """
    Gets a user by its unique identifier: their email
    """
    stmt = (
        select(
            User.c.id,
            User.c.email,
            User.c.username,
            User.c.full_name,
            User.c.password,
            User.c.is_admin,
        )
        .select_from(User)
        .where(User.c.email == email)
    )
    if result := await session.execute(stmt):
        if user := result.one_or_none():
            return models.UserWithPassword(**user._asdict())
    return None


async def get_users(
    session: AsyncSession,
    sort_params: list[SortParam],
    offset: int = 0,
    limit: int | None = None,
    email: list[str] | None = None,
    username: list[str] | None = None,
    full_name: list[str] | None = None,
    is_admin: list[str] | None = None,
) -> tuple[int, list[models.User]]:
    filters = filters_from_arguments(
        User,
        email=email,
        username=username,
        full_name=full_name,
        is_admin=is_admin,
    )
    order_by = order_by_from_arguments(sort_params=sort_params)
    count = await row_count(session, User, *filters)
    stmt = (
        select(
            User.c.id,
            User.c.email,
            User.c.username,
            User.c.full_name,
            User.c.is_admin,
        )
        .select_from(User)
        .where(*filters)  # type: ignore[arg-type]
        .order_by(*order_by)
        .offset(offset)
    )
    if limit is not None:
        stmt = stmt.limit(limit)
    result = await session.execute(stmt)
    return count, [models.User(**row._asdict()) for row in result.all()]


async def create_user(
    session: AsyncSession, user_details: models.UserCreate
) -> models.User:
    result = await session.execute(
        insert(User).returning(
            User.c.id,
            User.c.email,
            User.c.username,
            User.c.full_name,
            User.c.is_admin,
        ),
        [user_details.dict()],
    )
    user = result.one()
    return models.User(**user._asdict())


async def update_user_password(
    session: AsyncSession,
    user_id: int,
    password: str,
) -> None:
    stmt = update(User).where(User.c.id == user_id).values(password=password)
    await session.execute(stmt)


async def update_user(
    session: AsyncSession, user_id: int, details: models.UserUpdate
) -> models.User:
    patch_stmt = (
        update(User)
        .where(User.c.id == user_id)
        .values({k: v for k, v in details.dict().items() if v is not None})
        .returning(
            User.c.id,
            User.c.email,
            User.c.username,
            User.c.full_name,
            User.c.is_admin,
        )
    )
    result = await session.execute(patch_stmt)
    return models.User(**result.one()._asdict())


async def delete_user(session: AsyncSession, user_id: int) -> None:
    stmt = delete(User).where(User.c.id == user_id)
    await session.execute(stmt)
