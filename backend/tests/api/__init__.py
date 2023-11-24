from datetime import datetime


def api_timestamp(dt: datetime) -> str:
    """Format a timestamp according to the API outputformat."""
    return (
        dt.isoformat(timespec="microseconds")
        .replace(
            ".000000", ""
        )  # when microseconds are zero, they're not included
        .replace("+00:00", "Z")  # UTC timezone uses Z
    )
