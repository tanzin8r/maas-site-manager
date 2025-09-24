from typing import Any

from sqlalchemy import Table, func, literal


def sum_or_zero(table: Table, col: str, alias: str | None = None) -> Any:
    return func.coalesce(func.sum(table.c[col]), literal(0)).label(
        alias or f"n_{col}"
    )
