"""Common utility functions for the API"""

from fastapi import (
    HTTPException,
    status,
)
from pydantic import BaseModel


def not_found(entity: str) -> HTTPException:
    """Raise a 404 error for an something described by 'entity'
    entity should be uppercase
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": f"{entity} does not exist."},
    )


def raise_on_empty_request(patch_request: BaseModel) -> None:
    """Check if given `patch_request` is empty and raise 422 in that case"""
    if all(v is None for v in patch_request.model_dump().values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Request body empty."},
        )
