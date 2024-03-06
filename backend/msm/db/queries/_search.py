from functools import reduce
from operator import or_
from typing import Any

from sqlalchemy import (
    ColumnOperators,
    String,
    Table,
    Text,
    UnaryExpression,
    asc,
    desc,
)

from msm.schema import SortParam


def filters_from_arguments(
    table: Table,
    **filter_args: list[Any] | None,
) -> list[ColumnOperators]:
    """Return clauses to join with AND and all entries for a single arg by OR.
    This enables to convert query params such as

      ?name=name1&name=name2&city=city

    to a where clause such as

      (name ilike %name1% OR name ilike %name2%) AND city ilike %city%

    :param table: the table to create the WHERE clause for
    :param filter_args: the parameters matching the table's column name
                        as keys and lists of strings that will be matched
    :returns: a list with clauses to filter table values, which are meant to be
              used in AND. Clauses for each column are joined with OR.

    Matching is performed using `ilike` for text-based fields, exact match
    otherwise.

    """

    def compare_expr(name: str, value: Any) -> ColumnOperators:
        column = table.c[name]
        if isinstance(column.type, Text | String):
            return column.icontains(value, autoescape=True)
        else:
            return column.__eq__(value)

    return [
        reduce(
            or_,
            (compare_expr(name, value) for value in values),
        )
        for name, values in filter_args.items()
        if values
    ]


def order_by_from_arguments(
    sort_params: list[SortParam],
) -> list[UnaryExpression[Any]]:
    return [
        asc(param.field) if param.asc else desc(param.field)
        for param in sort_params
    ]
