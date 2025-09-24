from enum import StrEnum
from typing import override

import pytz


class CasePreservingStrEnum(StrEnum):
    """Representation of a string enum with case preservation."""

    @staticmethod
    @override
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name


# Enum with timezones accepted by pytz.
TimeZone = CasePreservingStrEnum("TimeZone", pytz.all_timezones)  # type: ignore
