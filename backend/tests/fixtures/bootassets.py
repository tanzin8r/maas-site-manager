from datetime import datetime

import pytest

from msm.apiserver.db.models import (
    BootAsset,
    BootAssetItem,
    BootAssetVersion,
    BootSource,
    BootSourceSelection,
)
from msm.common.enums import (
    BootAssetKind,
    BootAssetLabel,
    ItemFileType,
)
from tests.fixtures.factory import Factory


@pytest.fixture
def prev_sync() -> datetime:
    return datetime.fromtimestamp(0)


@pytest.fixture
def last_sync(factory: Factory) -> datetime:
    return factory.now


@pytest.fixture
async def boot_source_custom(
    factory: Factory, prev_sync: datetime
) -> BootSource:
    return await factory.make_BootSource(
        name="MSM Custom Images",
        url="http://msm:8000",
        last_sync=prev_sync,
    )


@pytest.fixture
async def boot_source(
    factory: Factory, boot_source_custom: BootSource, prev_sync: datetime
) -> BootSource:
    return await factory.make_BootSource(
        name="high-prio",
        url="https://high.prio.source.com",
        last_sync=prev_sync,
        priority=100,
        sync_interval=30,
    )


@pytest.fixture
async def boot_source_disabled(
    factory: Factory, boot_source_custom: BootSource, prev_sync: datetime
) -> BootSource:
    return await factory.make_BootSource(
        name="disabled",
        url="https://not-now.source.com",
        last_sync=prev_sync,
        priority=100,
        sync_interval=0,
    )


@pytest.fixture
async def boot_source_grub(
    factory: Factory, boot_source_custom: BootSource, prev_sync: datetime
) -> BootSource:
    return await factory.make_BootSource(
        name="bootloaders",
        url="https://grub.source.com",
        priority=50,
        last_sync=prev_sync,
    )


@pytest.fixture
async def boot_source_low(
    factory: Factory, boot_source_custom: BootSource, prev_sync: datetime
) -> BootSource:
    return await factory.make_BootSource(
        name="low-prio",
        url="https://lowprio.source.com",
        priority=10,
        last_sync=prev_sync,
    )


@pytest.fixture
async def ubuntu_noble(factory: Factory, boot_source: BootSource) -> BootAsset:
    return await factory.make_BootAsset(
        boot_source.id,
        kind=BootAssetKind.OS,
        label=BootAssetLabel.STABLE,
        os="ubuntu",
        release="noble",
        title="24.04 LTS",
        arch="amd64",
        subarch="hwe-24.04",
        flavor="generic",
        eol=datetime(2029, 5, 31),
        esm_eol=datetime(2034, 4, 25),
        signed=True,
    )


@pytest.fixture
async def ubuntu_jammy(factory: Factory, boot_source: BootSource) -> BootAsset:
    return await factory.make_BootAsset(
        boot_source.id,
        kind=BootAssetKind.OS,
        label=BootAssetLabel.STABLE,
        os="ubuntu",
        release="jammy",
        title="22.04 LTS",
        arch="amd64",
        subarch="ga-22.04",
        flavor="generic",
        eol=datetime(2027, 4, 21),
        esm_eol=datetime(2032, 4, 21),
        signed=True,
    )


@pytest.fixture
async def centos(factory: Factory, boot_source_low: BootSource) -> BootAsset:
    return await factory.make_BootAsset(
        boot_source_low.id,
        kind=BootAssetKind.OS,
        label=BootAssetLabel.STABLE,
        os="centos",
        release="centos70",
        title="CentOS 7",
        arch="amd64",
        subarch="generic",
        eol=datetime(2024, 6, 30),
        signed=False,
    )


@pytest.fixture
async def grub(factory: Factory, boot_source_grub: BootSource) -> BootAsset:
    return await factory.make_BootAsset(
        boot_source_grub.id,
        kind=BootAssetKind.BOOTLOADER,
        label=BootAssetLabel.CANDIDATE,
        os="grub-efi-signed",
        arch="arm64",
        bootloader_type="uefi",
        signed=True,
    )


@pytest.fixture
async def sel_ubuntu_noble(
    factory: Factory, ubuntu_noble: BootAsset
) -> list[BootSourceSelection]:
    assert ubuntu_noble.release is not None
    sel1 = await factory.make_BootSourceSelection(
        boot_source_id=ubuntu_noble.boot_source_id,
        label=ubuntu_noble.label,
        os=ubuntu_noble.os,
        release=ubuntu_noble.release,
        arch="ppc64el",
        selected=False,
    )
    sel2 = await factory.make_BootSourceSelection(
        boot_source_id=ubuntu_noble.boot_source_id,
        label=ubuntu_noble.label,
        os=ubuntu_noble.os,
        release=ubuntu_noble.release,
        arch=ubuntu_noble.arch,
        selected=True,
    )
    return [sel1, sel2]


@pytest.fixture
async def sel_ubuntu_jammy(
    factory: Factory, ubuntu_jammy: BootAsset
) -> list[BootSourceSelection]:
    assert ubuntu_jammy.release is not None
    sel1 = await factory.make_BootSourceSelection(
        boot_source_id=ubuntu_jammy.boot_source_id,
        label=ubuntu_jammy.label,
        os=ubuntu_jammy.os,
        release=ubuntu_jammy.release,
        arch="riscv",
        selected=False,
    )
    sel2 = await factory.make_BootSourceSelection(
        boot_source_id=ubuntu_jammy.boot_source_id,
        label=ubuntu_jammy.label,
        os=ubuntu_jammy.os,
        release=ubuntu_jammy.release,
        arch=ubuntu_jammy.arch,
        selected=True,
    )
    return [sel1, sel2]


@pytest.fixture
async def sel_centos(
    factory: Factory, centos: BootAsset
) -> BootSourceSelection:
    assert centos.release is not None
    return await factory.make_BootSourceSelection(
        boot_source_id=centos.boot_source_id,
        label=centos.label,
        os=centos.os,
        release=centos.release,
        arch=centos.arch,
        selected=False,
    )


@pytest.fixture
async def ver_grub(factory: Factory, grub: BootAsset) -> BootAssetVersion:
    return await factory.make_BootAssetVersion(grub.id, version="20250401")


@pytest.fixture
async def ver_ubuntu_jammy_1(
    factory: Factory, ubuntu_jammy: BootAsset
) -> BootAssetVersion:
    return await factory.make_BootAssetVersion(
        ubuntu_jammy.id, version="20250601"
    )


@pytest.fixture
async def ver_ubuntu_noble_1(
    factory: Factory, ubuntu_noble: BootAsset
) -> BootAssetVersion:
    return await factory.make_BootAssetVersion(
        ubuntu_noble.id, version="20250701"
    )


@pytest.fixture
async def ver_ubuntu_noble_2(
    factory: Factory, ubuntu_noble: BootAsset
) -> BootAssetVersion:
    return await factory.make_BootAssetVersion(
        ubuntu_noble.id, version="20250802"
    )


@pytest.fixture
async def ver_ubuntu_noble_2_reloaded(
    factory: Factory, ubuntu_noble: BootAsset
) -> BootAssetVersion:
    return await factory.make_BootAssetVersion(
        ubuntu_noble.id, version="20250802.1"
    )


@pytest.fixture
async def items_ubuntu_jammy_1(
    factory: Factory, ver_ubuntu_jammy_1: BootAssetVersion
) -> list[BootAssetItem]:
    return [
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_ubuntu_jammy_1.id,
            ftype=ItemFileType.BOOT_KERNEL,
            sha256="abc123",
            path=f"{ver_ubuntu_jammy_1.version}/ga-22.04/boot-kernel",
            file_size=123,
            bytes_synced=123,
        ),
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_ubuntu_jammy_1.id,
            ftype=ItemFileType.BOOT_INITRD,
            sha256="abc456",
            path=f"{ver_ubuntu_jammy_1.version}/ga-22.04/boot-initrd",
            file_size=465,
            bytes_synced=465,
        ),
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_ubuntu_jammy_1.id,
            ftype=ItemFileType.SQUASHFS_IMAGE,
            sha256="12345555",
            path=f"{ver_ubuntu_jammy_1.version}/squashfs",
            file_size=12345555,
            bytes_synced=12345555,
        ),
    ]


@pytest.fixture
async def items_ubuntu_noble_1(
    factory: Factory, ver_ubuntu_noble_1: BootAssetVersion
) -> list[BootAssetItem]:
    return [
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_ubuntu_noble_1.id,
            ftype=ItemFileType.BOOT_KERNEL,
            sha256="abc123",
            path=f"{ver_ubuntu_noble_1.version}/hwe-24.04/boot-kernel",
            file_size=123,
            bytes_synced=123,
        ),
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_ubuntu_noble_1.id,
            ftype=ItemFileType.BOOT_INITRD,
            sha256="abc456",
            path=f"{ver_ubuntu_noble_1.version}/hwe-24.04/boot-initrd",
            file_size=465,
            bytes_synced=465,
        ),
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_ubuntu_noble_1.id,
            ftype=ItemFileType.SQUASHFS_IMAGE,
            sha256="12345555",
            path=f"{ver_ubuntu_noble_1.version}/squashfs",
            file_size=12345555,
            bytes_synced=12345555,
        ),
    ]


@pytest.fixture
async def items_ubuntu_noble_2(
    factory: Factory, ver_ubuntu_noble_2: BootAssetVersion
) -> list[BootAssetItem]:
    return [
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_ubuntu_noble_2.id,
            ftype=ItemFileType.BOOT_KERNEL,
            sha256="cadecafe1",
            path=f"{ver_ubuntu_noble_2.version}/hwe-24.04/boot-kernel",
            file_size=55551,
        ),
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_ubuntu_noble_2.id,
            ftype=ItemFileType.BOOT_INITRD,
            sha256="cadecafe2",
            path=f"{ver_ubuntu_noble_2.version}/hwe-24.04/boot-initrd",
            file_size=55552,
        ),
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_ubuntu_noble_2.id,
            ftype=ItemFileType.SQUASHFS_IMAGE,
            sha256="cadecafe3",
            path=f"{ver_ubuntu_noble_2.version}/squashfs",
            file_size=555555,
        ),
    ]


@pytest.fixture
async def items_grub(
    factory: Factory, ver_grub: BootAssetVersion
) -> list[BootAssetItem]:
    return [
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_grub.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="deadbeef",
            path=f"{ver_grub.version}/grub2-signed.tar.xz",
            file_size=8888,
            bytes_synced=8888,
            source_package="grub2-signed",
            source_release="focal",
            source_version="1.167.2+2.04-1ubuntu44.2",
        ),
        await factory.make_BootAssetItem(
            boot_asset_version_id=ver_grub.id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="deadbeef2",
            path=f"{ver_grub.version}/shim-signed.tar.xz",
            file_size=7777,
            bytes_synced=7777,
            source_package="shim-signed",
            source_release="focal",
            source_version="1.167.2+2.04-1ubuntu44.2",
        ),
    ]
