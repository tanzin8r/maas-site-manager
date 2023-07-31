import csv
from io import StringIO
from typing import Iterable

from fastapi import Response
from pydantic import BaseModel


class CSVResponse(Response):
    """Return a CSV response serializing a list of pydantic models."""

    media_type = "text/csv"

    def render(self, content: Iterable[BaseModel]) -> bytes:
        if not content:
            return b""

        entries = list(content)
        model_fields = list(entries[0].model_fields)

        stream = StringIO()
        writer = csv.writer(stream)
        writer.writerow(model_fields)
        for entry in entries:
            writer.writerow((value for key, value in entry))
        return stream.getvalue().encode()
