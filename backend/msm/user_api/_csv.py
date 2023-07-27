import csv
from io import StringIO

from fastapi import Response
from pydantic import BaseModel


class CSVResponse(Response):
    """Return a CSV response serializing a list of pydantic models."""

    media_type = "text/csv"

    def render(self, content: list[BaseModel]) -> bytes:
        if not content:
            return b""

        model_fields = list(content[0].model_fields)
        stream = StringIO()

        writer = csv.writer(stream)
        writer.writerow(model_fields)
        for entry in content:
            writer.writerow((value for key, value in entry))
        return stream.getvalue().encode()
