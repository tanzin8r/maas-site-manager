from typing import Any

from sqlalchemy import (
    ColumnElement,
    String,
    Table,
    Text,
    UnaryExpression,
    asc,
    desc,
    or_,
)

from msm.apiserver.schema import SortParam


def compare_expr(
    table: Table, column_name: str, value: Any
) -> ColumnElement[bool]:
    """
    Create an "column_name ILIKE %value%" WHERE clause for string columns
    and an "column_name == value" clause otherwise
    """
    column = table.c[column_name]
    if isinstance(column.type, Text | String) and value is not None:
        return column.icontains(value, autoescape=True)
    else:
        return column.__eq__(value)


def filters_from_arguments(
    table: Table,
    **filter_args: list[Any] | None,
) -> list[ColumnElement[bool]]:
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
    return [
        or_(*(compare_expr(table, name, value) for value in values))
        for name, values in filter_args.items()
        if values
    ]


def query_all_columns(
    table: Table, query: str | None, column_names: list[str]
) -> list[ColumnElement[bool]]:
    """
    Creates a where clause that queries all column_names in table for
    the given query string.

    As `filters_from_arguments` it uses `ILIKE` for text-based fields and
    exact match otherwise
    """
    return (
        [or_(*(compare_expr(table, column, query) for column in column_names))]
        if query
        else []
    )


def order_by_from_arguments(
    sort_params: list[SortParam],
) -> list[UnaryExpression[Any]]:
    return [
        asc(param.field) if param.asc else desc(param.field)
        for param in sort_params
    ]
