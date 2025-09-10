from typing import Any, NamedTuple, Self

from pydantic import AwareDatetime, BaseModel, Field, model_validator

from msm.db import models
from msm.schema import PaginatedResults


class BootSourceGetResponse(models.BootSource):
    @classmethod
    def from_model(cls, model: models.BootSource) -> Self:
        return cls(**model.model_dump())


class BootSourcePatchResponse(models.BootSource):
    @classmethod
    def from_model(cls, model: models.BootSource) -> Self:
        return cls(**model.model_dump())


class BootSourcesGetResponse(PaginatedResults[models.BootSource]):
    pass


class BootSourceSelectionsGetResponse(
    PaginatedResults[models.BootSourceSelection]
):
    pass


class BootSourcesPostRequest(BaseModel):
    priority: int
    url: str
    keyring: str
    sync_interval: int
    name: str


class BootSourcesPostResponse(BaseModel):
    id: int


class BootSourcesPatchRequest(BaseModel):
    priority: int | None = None
    url: str | None = None
    keyring: str | None = None
    sync_interval: int | None = Field(default=None, ge=0)
    name: str | None = None

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def check_at_least_one_field_present(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be set.")
        return self


class AvailableBootSourceSelection(NamedTuple):
    os: str
    release: str
    label: models.BootAssetLabel
    arch: str

    def __eq__(self, other: Any) -> bool:
        return (self.os, self.release, self.arch) == (
            other.os,
            other.release,
            other.arch,
        )


class BootSourceAvailSelectionsPutRequest(BaseModel):
    available: list[AvailableBootSourceSelection]


class BootSourceAvailSelectionsPutResponse(BaseModel):
    stale: list[models.BootSourceSelection]


class BootAssetItemPatchRequest(BaseModel):
    ftype: str | None = None
    source_package: str | None = None
    source_version: str | None = None
    source_release: str | None = None
    bytes_synced: int | None = None  # can only be changed by workers

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def check_at_least_one_field_present(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("At least one field must be set.")
        return self


class BootAssetItemPatchResponse(models.BootAssetItem):
    @classmethod
    def from_model(cls, model: models.BootAssetItem) -> Self:
        return cls(**model.model_dump())


class ProductItem(BaseModel):
    ftype: models.ItemFileType
    sha256: str
    path: str
    file_size: int
    source_package: str | None = None
    source_version: str | None = None
    source_release: str | None = None


class Product(BaseModel):
    kind: models.BootAssetKind
    label: models.BootAssetLabel
    os: str
    arch: str
    release: str | None = None
    codename: str | None = None
    title: str | None = None
    subarch: str | None = None
    compatibility: list[str] | None = None
    flavor: str | None = None
    base_image: str | None = None
    bootloader_type: str | None = None
    eol: AwareDatetime | None = None
    esm_eol: AwareDatetime | None = None
    signed: bool = False
    versions: dict[str, list[ProductItem]]


class BootSourcesAssetsPutRequest(BaseModel):
    products: list[Product]


class BootSourcesAssetsPutResponse(BaseModel):
    to_download: list[int]


class BootAssetItemGetResponse(models.BootAssetItem):
    @classmethod
    def from_model(cls, model: models.BootAssetItem) -> Self:
        return cls(**model.model_dump())
