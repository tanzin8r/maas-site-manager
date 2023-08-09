# XXX Pydantic v2 removes trailing zeroes from ISO timestamps, which sometimes
# causes comparisons to fail since datetime.isoformat() includes them.
#
# This makes a local isoformat() to strip them, and fromisoformat() to
# accept a timestamp with less than 6 decimal points.
#
# See https://github.com/pydantic/pydantic/issues/6761 for the Pydantic bug.
#

from datetime import datetime


def isoformat(dt: datetime) -> str:
    return datetime.isoformat(dt).rstrip("0")


def fromisoformat(datestring: str) -> datetime:
    if "." in datestring:
        _, decimal = datestring.rsplit(".", 1)
        missing_digits = 6 - len(decimal)
        datestring += "0" * missing_digits
    return datetime.fromisoformat(datestring)
