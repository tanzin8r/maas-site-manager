from typing import NamedTuple

from fastapi import Query


class SiteFilterParams(NamedTuple):
    """Site filtering parameters."""

    address: list[str] | None
    city: list[str] | None
    country: list[str] | None
    name: list[str] | None
    note: list[str] | None
    postal_code: list[str] | None
    state: list[str] | None
    timezone: list[str] | None
    url: list[str] | None
    cluster_uuid: list[str] | None
    query: str | None


class TokenFilterParams(NamedTuple):
    """Token filtering parameters."""

    # note that there is no filter for `created` yet
    # we did not design filtering for anything but equality yet

    id: list[int] | None
    value: list[str] | None
    site_id: list[int] | None


class UserFilterParams(NamedTuple):
    """User filtering parameters."""

    email: list[str] | None
    username: list[str] | None
    full_name: list[str] | None
    is_admin: list[bool] | None


async def site_filter_parameters(
    city: list[str] | None = Query(default=None, title="Filter for cities"),
    country: list[str] | None = Query(
        default=None, title="Filter for country"
    ),
    name: list[str] | None = Query(default=None, title="Filter for names"),
    note: list[str] | None = Query(default=None, title="Filter for notes"),
    state: list[str] | None = Query(
        default=None, title="Filter for administrative regions"
    ),
    address: list[str] | None = Query(
        default=None, title="Filter for streets"
    ),
    postal_code: list[str] | None = Query(
        default=None, title="Filter for postal code"
    ),
    timezone: list[str] | None = Query(
        default=None, title="Filter for timezones"
    ),
    url: list[str] | None = Query(default=None, title="Filter for urls"),
    cluster_uuid: list[str] | None = Query(
        default=None, title="Filter for MAAS UUIDs"
    ),
    q: str | None = Query(
        default=None, title="Search for query in string fields"
    ),
) -> SiteFilterParams:
    """Return parameters for site filtering."""
    return SiteFilterParams(
        address=address,
        city=city,
        country=country,
        name=name,
        note=note,
        postal_code=postal_code,
        state=state,
        timezone=timezone,
        url=url,
        cluster_uuid=cluster_uuid,
        query=q,
    )


async def token_filter_parameters(
    id: list[int] | None = Query(default=None, title="Filter for token IDs"),
    value: list[str] | None = Query(default=None, title="Filter for tokens"),
    site_id: list[int] | None = Query(
        default=None, title="Filter for site IDs the token authenticated"
    ),
) -> TokenFilterParams:
    """Return parameters for token filtering."""
    return TokenFilterParams(
        id=id,
        value=value,
        site_id=site_id,
    )


async def user_filter_params(
    email: list[str] | None = Query(
        default=None, title="Filter for email address"
    ),
    username: list[str] | None = Query(
        default=None, title="Filter for username"
    ),
    full_name: list[str] | None = Query(
        default=None, title="Filter for full name"
    ),
    is_admin: list[bool] | None = Query(
        default=None, title="Filter for admin status"
    ),
) -> UserFilterParams:
    """Return parameters for user filtering."""
    return UserFilterParams(
        email=email,
        username=username,
        full_name=full_name,
        is_admin=is_admin,
    )
