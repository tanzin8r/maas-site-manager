from re import compile
from typing import Any, NamedTuple

from fastapi import (
    Query,
)
from fastapi.exceptions import RequestValidationError

REMOVE_SORT_SUFFIX_REGEX = compile("(-desc|-asc)$")


class SortParam(NamedTuple):
    """Sort parameter."""

    field: str
    asc: bool = True


class SortParamParser:
    def __init__(self, fields: list[str]):
        self.fields = fields

    def __call__(
        self,
        sort_by: str | None = Query(default=None, title="Sort by properties"),
    ) -> list[SortParam]:
        """
        Parse the sort_by query parameter such
        as ?sort_by=property1-desc,property2-asc.
        By default, it uses the ascending ordering
        if no -desc/-asc suffix is specified.
        """
        if not sort_by:
            return []
        sort_query_fields = [field.strip() for field in sort_by.split(",")]
        sort_params: dict[str, SortParam] = {}
        errors: list[dict[str, Any]] = []
        for sort_query_field in sort_query_fields:
            ascending_sort: bool = not sort_query_field.endswith("-desc")
            field_name: str = REMOVE_SORT_SUFFIX_REGEX.sub(
                "", sort_query_field
            )
            if field_name not in self.fields:
                errors.append(
                    {
                        "loc": ("path", field_name),
                        "type": "ExtraForbidden",
                        "msg": "Invalid sort field",
                    }
                )
            elif field_name in sort_params:
                errors.append(
                    {
                        "loc": ("path", field_name),
                        "type": "Duplicated",
                        "msg": "Duplicate sort parameters detected",
                    }
                )
            else:
                sort_params[field_name] = SortParam(
                    field=field_name, asc=ascending_sort
                )

        if errors:
            raise RequestValidationError(errors=errors)

        return [x for x in sort_params.values()]
