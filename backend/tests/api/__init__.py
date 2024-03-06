from datetime import datetime


def api_timestamp(dt: datetime, astimezone: bool = False) -> str:
    """Format a timestamp according to the API outputformat."""

    if astimezone:
        dt = dt.astimezone()

    return (
        dt.isoformat(timespec="microseconds")
        .replace(
            ".000000", ""
        )  # when microseconds are zero, they're not included
        .replace("+00:00", "Z")  # UTC timezone uses Z
    )
