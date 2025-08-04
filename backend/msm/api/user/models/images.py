from typing import Self

from pydantic import BaseModel

from msm.db import models


class GetAvailableImagesResponse(BaseModel):
    items: list[models.AvailableImage]


class ImagesPostResponse(models.BootAssetItem):
    @classmethod
    def from_model(cls, model: models.BootAssetItem) -> Self:
        return cls(**model.dict())
