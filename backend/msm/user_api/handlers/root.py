from fastapi import (
    APIRouter,
    Request,
)
from pydantic import BaseModel

v1_router = APIRouter(prefix="/v1")


class RootGetResponse(BaseModel):
    """Root handler response."""

    version: str


@v1_router.get("/")
async def get(request: Request) -> RootGetResponse:
    """Root endpoint."""
    return RootGetResponse(version=request.app.version)
