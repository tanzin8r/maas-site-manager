from typing import NamedTuple

from fastapi import Query


class SiteFilterParams(NamedTuple):
    """Site filtering parameters."""

    city: list[str] | None
    country: list[str] | None
    name: list[str] | None
    note: list[str] | None
    region: list[str] | None
    street: list[str] | None
    timezone: list[str] | None
    url: list[str] | None


async def site_filter_parameters(
    city: list[str] | None = Query(default=None, title="Filter for cities"),
    country: list[str]
    | None = Query(default=None, title="Filter for country"),
    name: list[str] | None = Query(default=None, title="Filter for names"),
    note: list[str] | None = Query(default=None, title="Filter for notes"),
    region: list[str] | None = Query(default=None, title="Filter for regions"),
    street: list[str] | None = Query(default=None, title="Filter for streets"),
    timezone: list[str]
    | None = Query(default=None, title="Filter for timezones"),
    url: list[str] | None = Query(default=None, title="Filter for urls"),
) -> SiteFilterParams:
    """Return parameters for site filtering."""
    return SiteFilterParams(
        city=city,
        country=country,
        name=name,
        note=note,
        region=region,
        street=street,
        timezone=timezone,
        url=url,
    )
