from typing import Self

from msm.db import models


class ImagesPostResponse(models.BootAssetItem):
    @classmethod
    def from_model(cls, model: models.BootAssetItem) -> Self:
        return cls(**model.model_dump())
