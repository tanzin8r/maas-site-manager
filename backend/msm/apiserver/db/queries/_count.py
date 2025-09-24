from sqlalchemy import (
    ColumnOperators,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql.expression import FromClause


async def row_count(
    conn: AsyncConnection, what: FromClause, *filters: ColumnOperators
) -> int:
    """Count specified entries."""
    stmt = (
        select(func.count()).select_from(what).where(*filters)  # type: ignore[arg-type]
    )
    return (await conn.execute(stmt)).scalar() or 0
