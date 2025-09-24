from collections.abc import Callable
from typing import Any

from sqlalchemy.types import UserDefinedType

from msm.apiserver.db.models import Coordinates


class Point(UserDefinedType):  # type: ignore
    """
    The postgresql POINT
    https://www.postgresql.org/docs/current/datatype-geometric.html#DATATYPE-GEOMETRIC-POINTS
    """

    cache_ok = True

    def get_col_spec(self, **kw: Any) -> str:
        return "POINT"

    @property
    def python_type(self) -> type[Coordinates]:
        return Coordinates

    def bind_processor(
        self, dialect: Any
    ) -> Callable[[dict[str, float] | None], tuple[float, float] | None]:
        def process(
            value: dict[str, float] | None,
        ) -> tuple[float, float] | None:
            if value is not None:
                try:
                    return (value["latitude"], value["longitude"])
                except KeyError:
                    raise TypeError(
                        "Cooridnates must have latitude and longitude"
                    )
            return value

        return process

    def result_processor(
        self, dialect: Any, coltype: Any
    ) -> Callable[[Any], Coordinates | None]:
        # convert the result to a plain tuple

        def convert(value: Any) -> Coordinates | None:
            if value is None:
                return None
            coords = tuple(value)
            return Coordinates(latitude=coords[0], longitude=coords[1])

        return convert
