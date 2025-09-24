from pydantic import BaseModel

from msm.apiserver.db import models


class ImageSource(BaseModel):
    selection_id: int
    id: int
    name: str
    url: str


class GetSelectableImagesResponse(BaseModel):
    items: list[models.SelectableImage]


class GetSelectedImagesResponse(BaseModel):
    items: list[models.SelectedImage]


class GetImageSourcesResponse(BaseModel):
    items: list[ImageSource]


class SelectImagesPostRequest(BaseModel):
    selection_ids: list[int]


class RemoveSelectedImagesPostRequest(BaseModel):
    selection_ids: list[int]
