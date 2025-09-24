from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
)

from msm.common.enums import (
    BootAssetKind,
    BootAssetLabel,
    ItemFileType,
)


class BootAssetItem(BaseModel):
    id: int
    boot_asset_version_id: int | None = None
    ftype: ItemFileType
    sha256: str
    path: str
    file_size: int
    source_package: str | None = None
    source_version: str | None = None
    source_release: str | None = None
    bytes_synced: int


class BootAssetItemCreate(BaseModel):
    boot_asset_version_id: int | None = None
    ftype: ItemFileType
    sha256: str
    path: str
    file_size: int
    source_package: str | None = None
    source_version: str | None = None
    source_release: str | None = None


class BootAssetItemUpdate(BaseModel):
    boot_asset_version_id: int | None = None
    ftype: ItemFileType | None = None
    sha256: str | None = None
    path: str | None = None
    file_size: int | None = None
    source_package: str | None = None
    source_version: str | None = None
    source_release: str | None = None
    bytes_synced: int | None = None


class BootAssetVersion(BaseModel):
    id: int
    boot_asset_id: int
    version: str
    last_seen: AwareDatetime


class BootAssetVersionCreate(BaseModel):
    boot_asset_id: int
    version: str
    last_seen: AwareDatetime


class BootAssetVersionUpdate(BaseModel):
    boot_asset_id: int
    version: str
    last_seen: AwareDatetime


class BootAsset(BaseModel):
    id: int
    boot_source_id: int
    kind: BootAssetKind
    label: BootAssetLabel
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


class BootAssetWithSourceName(BootAsset):
    source_name: str


class BootAssetCreate(BaseModel):
    boot_source_id: int
    kind: BootAssetKind
    label: BootAssetLabel
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


class BootAssetUpdate(BaseModel):
    kind: BootAssetKind | None = None
    label: BootAssetLabel | None = None
    os: str | None = None
    release: str | None = None
    codename: str | None = None
    title: str | None = None
    arch: str | None = None
    subarch: str | None = None
    compatibility: list[str] | None = None
    flavor: str | None = None
    base_image: str | None = None
    bootloader_type: str | None = None
    eol: AwareDatetime | None = None
    esm_eol: AwareDatetime | None = None
    signed: bool = False


class BootSourceSelection(BaseModel):
    id: int
    boot_source_id: int
    label: BootAssetLabel
    os: str
    release: str
    arch: str
    selected: bool


class BootSourceSelectionCreate(BaseModel):
    boot_source_id: int
    label: BootAssetLabel
    os: str
    release: str
    arch: str
    selected: bool


class BootSourceSelectionUpdate(BaseModel):
    """The allowed updates to a BootSourceSelection from a user."""

    label: BootAssetLabel | None = None
    os: str | None = None
    release: str | None = None
    arch: str | None = None
    selected: bool | None = None


class BootSource(BaseModel):
    id: int
    priority: int
    url: str
    name: str
    keyring: str | None = None
    sync_interval: int = Field(ge=0)
    last_sync: AwareDatetime


class BootSourceCreate(BaseModel):
    priority: int
    url: str
    name: str
    keyring: str | None = None
    sync_interval: int = Field(ge=0)
    last_sync: AwareDatetime


class BootSourceUpdate(BaseModel):
    """The allowed updates to a BootSource from a user."""

    priority: int | None = None
    url: str | None = None
    name: str | None = None
    keyring: str | None = None
    sync_interval: int | None = Field(default=None, ge=0)
    last_sync: AwareDatetime | None = None


class SelectableImage(BaseModel):
    selection_id: int
    os: str
    release: str
    arch: str
    boot_source_id: int
    boot_source_name: str
    boot_source_url: str


class SelectedImage(BaseModel):
    boot_source_id: int
    boot_source_name: str
    boot_source_url: str
    os: str
    arch: str
    release: str
    size: int
    downloaded: int
    custom_image_id: int | None = None
    selection_id: int | None = None


class IndexProduct(BaseModel):
    """Class representing the necessary items to specify a product in the index."""

    id: int
    boot_source_id: int
    kind: BootAssetKind
    label: BootAssetLabel
    os: str
    arch: str
    ftype: ItemFileType
    sha256: str
    path: str
    file_size: int
    bytes_synced: int
    version: str
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
    source_package: str | None = None
    source_version: str | None = None
    source_release: str | None = None
