from datetime import datetime
from typing import Any, NamedTuple, Self

from pydantic import AwareDatetime, BaseModel, Field, model_validator

from msm.db import models
from msm.schema import (
    PaginatedResults,
)


class BootAssetsPostRequest(BaseModel):
    boot_source_id: int
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
    eol: datetime | None = None
    esm_eol: datetime | None = None
    signed: bool = False


class BootAssetsPostResponse(BaseModel):
    id: int


class BootAssetsGetResponse(PaginatedResults):
    items: list[models.BootAssetWithSourceName]


class BootSourceGetResponse(models.BootSource):
    @classmethod
    def from_model(cls, model: models.BootSource) -> Self:
        return cls(**model.model_dump())


class BootSourcePatchResponse(models.BootSource):
    @classmethod
    def from_model(cls, model: models.BootSource) -> Self:
        return cls(**model.model_dump())


class BootSourcesGetResponse(PaginatedResults):
    items: list[models.BootSource]


class BootSourceSelectionsGetResponse(PaginatedResults):
    items: list[models.BootSourceSelection]


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
    arches: list[str]

    def __eq__(self, other: Any) -> bool:
        return (self.os, self.release) == (other.os, other.release)


class BootSourceAvailSelectionsPutRequest(BaseModel):
    available: list[AvailableBootSourceSelection]


class BootSourceAvailSelectionsPutResponse(BaseModel):
    stale: list[models.BootSourceSelection]


class BootAssetVersionPostRequest(BaseModel):
    version: str


class BootAssetVersionPostResponse(BaseModel):
    id: int


class BootAssetVersionsGetResponse(PaginatedResults):
    items: list[models.BootAssetVersion]


class BootAssetItemPostRequest(BaseModel):
    ftype: str
    sha256: str
    path: str
    file_size: int
    source_package: str | None = None
    source_version: str | None = None
    source_release: str | None = None


class BootAssetItemPostResponse(BaseModel):
    id: int


class BootAssetItemsGetResponse(PaginatedResults):
    items: list[models.BootAssetItem]


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
