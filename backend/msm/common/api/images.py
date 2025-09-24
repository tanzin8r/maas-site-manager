from typing import Self

from pydantic import BaseModel

from msm.apiserver.db import models


class ImagesPostResponse(models.BootAssetItem):
    @classmethod
    def from_model(cls, model: models.BootAssetItem) -> Self:
        return cls(**model.model_dump())


class ImagesRemovePostRequest(BaseModel):
    asset_ids: list[int]
