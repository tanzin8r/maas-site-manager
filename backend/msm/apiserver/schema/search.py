from typing import NamedTuple

from fastapi import Query


class SearchTextParam(NamedTuple):
    """Free text search params."""

    search_text: list[str]


async def search_text_param(
    search_text: str = Query(default=""),
) -> SearchTextParam:
    """Return search parameters."""
    return SearchTextParam(search_text=search_text.split())
