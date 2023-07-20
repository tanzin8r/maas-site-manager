from fastapi import (
    APIRouter,
    Request,
)
from pydantic import BaseModel

router = APIRouter()


class RootGetResponse(BaseModel):
    """Root handler response."""

    version: str


@router.get("/")
async def get(request: Request) -> RootGetResponse:
    """Root endpoint."""
    return RootGetResponse(version=request.app.version)
