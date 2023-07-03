from sqlalchemy import (
    ColumnOperators,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import FromClause


async def row_count(
    session: AsyncSession, what: FromClause, *filters: ColumnOperators
) -> int:
    """Count specified entries."""
    stmt = (
        select(func.count())
        .select_from(what)
        .where(*filters)  # type: ignore[arg-type]
    )
    return (await session.execute(stmt)).scalar() or 0
