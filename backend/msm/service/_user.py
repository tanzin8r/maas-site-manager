from typing import Any

from sqlalchemy import (
    delete,
    insert,
    Select,
    select,
    update,
)
from sqlalchemy.sql import (
    and_,
    or_,
)

from ..db import (
    models,
    queries,
)
from ..db.tables import User
from ..schema import SortParam
from ._base import Service


class UserService(Service):
    async def get(
        self,
        sort_params: list[SortParam],
        offset: int = 0,
        limit: int | None = None,
        search_text: list[str] | None = None,
        email: list[str] | None = None,
        username: list[str] | None = None,
        full_name: list[str] | None = None,
        is_admin: list[str] | None = None,
    ) -> tuple[int, list[models.User]]:
        filters = queries.filters_from_arguments(
            User,
            email=email,
            username=username,
            full_name=full_name,
            is_admin=is_admin,
        )
        order_by = queries.order_by_from_arguments(sort_params=sort_params)
        if search_text:
            filters.append(
                or_(
                    *queries.filters_from_arguments(  # type: ignore[arg-type]
                        User,
                        email=search_text,
                        username=search_text,
                        full_name=search_text,
                    )
                )
            )
        count = await queries.row_count(self.conn, User, *filters)
        stmt = (
            self._select_statement()
            .where(*filters)  # type: ignore[arg-type]
            .order_by(*order_by)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.conn.execute(stmt)
        return count, [models.User(**row._asdict()) for row in result.all()]

    async def get_by_email(self, email: str) -> models.UserWithPassword | None:
        """Gets a user by email."""
        stmt = self._select_statement(include_password=True).where(
            User.c.email == email
        )
        if result := await self.conn.execute(stmt):
            if user := result.one_or_none():
                return models.UserWithPassword(**user._asdict())
        return None

    async def get_by_id(self, id: int) -> models.UserWithPassword | None:
        """Gets a user by id."""
        stmt = self._select_statement(include_password=True).where(
            User.c.id == id
        )
        if result := await self.conn.execute(stmt):
            if user := result.one_or_none():
                return models.UserWithPassword(**user._asdict())
        return None

    async def create(self, user_details: models.UserCreate) -> models.User:
        result = await self.conn.execute(
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

    async def id_exists(self, user_id: int) -> bool:
        search = await self.conn.execute(
            select(User.c.id).select_from(User).filter(User.c.id == user_id)
        )
        return search.first() is not None

    async def exists(
        self,
        email: str | None = None,
        username: str | None = None,
        exclude_id: int | None = None,
    ) -> bool:
        if not email and not username:
            return False
        elif not username:
            user_filter = User.c.email == email
        elif not email:
            user_filter = User.c.username == username
        else:
            user_filter = or_(
                User.c.email == email, User.c.username == username
            )
        if exclude_id is not None:
            user_filter = and_(user_filter, User.c.id != exclude_id)
        search = await self.conn.execute(
            select(User.c.id).select_from(User).filter(user_filter)
        )
        return search.first() is not None

    async def update_password(
        self,
        user_id: int,
        password: str,
    ) -> None:
        stmt = (
            update(User).where(User.c.id == user_id).values(password=password)
        )
        await self.conn.execute(stmt)

    async def update(
        self, user_id: int, details: models.UserUpdate
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
        result = await self.conn.execute(patch_stmt)
        return models.User(**result.one()._asdict())

    async def delete(self, user_id: int) -> None:
        stmt = delete(User).where(User.c.id == user_id)
        await self.conn.execute(stmt)

    def _select_statement(self, include_password: bool = False) -> Select[Any]:
        fields = [
            User.c.id,
            User.c.email,
            User.c.username,
            User.c.full_name,
            User.c.is_admin,
        ]
        if include_password:
            fields.append(User.c.password)
        return select(*fields).select_from(User)
