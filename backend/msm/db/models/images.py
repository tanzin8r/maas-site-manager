from enum import Enum

from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
)


class BootAssetKind(int, Enum):
    OS = 0
    BOOTLOADER = 1


class BootAssetLabel(str, Enum):
    STABLE = "stable"
    CANDIDATE = "candidate"


class ItemFileType(str, Enum):
    # Tarball of root image.
    ROOT_TGZ = "root-tgz"
    ROOT_TBZ = "root-tbz"
    ROOT_TXZ = "root-txz"

    # Tarball of dd image.
    ROOT_DD = "root-dd"
    ROOT_DDTAR = "root-dd.tar"

    # Raw dd image
    ROOT_DDRAW = "root-dd.raw"

    # Compressed dd image types
    ROOT_DDBZ2 = "root-dd.bz2"
    ROOT_DDGZ = "root-dd.gz"
    ROOT_DDXZ = "root-dd.xz"

    # Compressed tarballs of dd images
    ROOT_DDTBZ = "root-dd.tar.bz2"
    ROOT_DDTXZ = "root-dd.tar.xz"
    # For backwards compatibility, DDTGZ files are named root-dd
    ROOT_DDTGZ = "root-dd"

    # Following are not allowed on user upload. Only used for syncing
    # from another simplestreams source. (Most likely images.maas.io)

    # Root Image (gets converted to root-image root-tgz, on the rack)
    ROOT_IMAGE = "root-image.gz"

    # Root image in SquashFS form, does not need to be converted
    SQUASHFS_IMAGE = "squashfs"

    # Boot Kernel
    BOOT_KERNEL = "boot-kernel"

    # Boot Initrd
    BOOT_INITRD = "boot-initrd"

    # Boot DTB
    BOOT_DTB = "boot-dtb"

    # tar.xz of files which need to be extracted so the files are usable
    # by MAAS
    ARCHIVE_TAR_XZ = "archive.tar.xz"


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


class BootAssetVersionCreate(BaseModel):
    boot_asset_id: int
    version: str


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


class BootSourceSelection(BaseModel):
    id: int
    boot_source_id: int
    label: BootAssetLabel
    os: str
    release: str
    available: list[str]
    selected: list[str]


class BootSourceSelectionCreate(BaseModel):
    boot_source_id: int
    label: BootAssetLabel
    os: str
    release: str
    available: list[str]
    selected: list[str]


class BootSourceSelectionUpdate(BaseModel):
    """The allowed updates to a BootSourceSelection from a user."""

    label: BootAssetLabel | None = None
    os: str | None = None
    release: str | None = None
    available: list[str] | None = None
    selected: list[str] | None = None


class BootSource(BaseModel):
    id: int
    priority: int
    url: str
    name: str
    keyring: str | None = None
    sync_interval: int = Field(ge=0)


class BootSourceCreate(BaseModel):
    priority: int
    url: str
    name: str
    keyring: str | None = None
    sync_interval: int = Field(ge=0)


class BootSourceUpdate(BaseModel):
    """The allowed updates to a BootSource from a user."""

    priority: int | None = None
    url: str | None = None
    name: str | None = None
    keyring: str | None = None
    sync_interval: int | None = Field(default=None, ge=0)
