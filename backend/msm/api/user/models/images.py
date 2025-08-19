from typing import Self

from pydantic import BaseModel

from msm.db import models


class GetSelectableImagesResponse(BaseModel):
    items: list[models.SelectableImage]


class ImagesPostResponse(models.BootAssetItem):
    @classmethod
    def from_model(cls, model: models.BootAssetItem) -> Self:
        return cls(**model.model_dump())
