from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncConnection

from msm.apiserver.db import CUSTOM_IMAGE_SOURCE_ID
from msm.common.enums import ItemFileType
from msm.common.time import utc_from_timestamp
from msm.sampledata.db import (
    ModelCollection,
    SampleDataModel,
)


async def make_fixture_images(conn: AsyncConnection) -> list[SampleDataModel]:
    collection = ModelCollection("boot_source")
    collection.add(
        id=CUSTOM_IMAGE_SOURCE_ID,
        priority=1,
        url="http://maas.site.manager",
        keyring="",
        name="MSM Custom Images",
        sync_interval=0,
        last_sync=utc_from_timestamp(0.0),
    )
    # create the custom source separately, since we're not specifying
    # ID for the other sources.
    await collection.create(conn)

    collection.add(
        priority=3,
        url="http://primary.image.server",
        name="Public Image Server",
        keyring="""-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBFxEQeMBCACtgu58j4RuE34OW3Xoy4PIXlLv/8P+FUUFs8Dk4WO5zUJN2NfN
45fIASdKcH8cV2wbCVwjKEP0h4p5IE+lrwQK7bwYx7Qt+qmrm5eLMUM8IvXA18wf
AOPS7XeKTzxa4/jWagJupmmYL+MuV9o5haqYplOYCcVR135KAZfx743YuWcNqvcr
3Em0+gh4F2TXsefjniwuJRGY3Kbb/MAM2zC2f7FfCJVb1C30OLB+KwCddZP/23ll
nOqmzaVF0qQrHQ5EZGK3j3S4fzHNq14TMS3c21YkPOO/DV6BkgIHtG5NIIdVEdQh
wV8clpj0ZP7ShIE8cDhTy8k+xrIByPUVfpMpABEBAAG0J0JpbGwgQnVjaGFuYW4g
PHcuYnVjaGFuYW5AbmFwaWVyLmFjLnVrPokBVAQTAQgAPhYhBK9cqX/wEcCpQ6+5
TFPDJcqRPXoQBQJcREHjAhsDBQkDwmcABQsJCAcCBhUKCQgLAgQWAgMBAh4BAheA
AAoJEFPDJcqRPXoQ2KIH/2sRAsqbrqCMNMRsiBo9XtCFzQ052odbzubIScnwzrDF
Y9z+qPSAwaWGO+1R3LPDH5sMLQ2YOsNqg8VvTJBtOjR9YGNX9/bqqVFRKKSQ0HiD
Sb2M7phBdk4WLkqLZ/AfgHaLKpfNX0bq7WhqZ+Pez0nqjN08JkIog7LhaQZh/Chf
0pl+wHV0rEFuaDQn83yF5DWB1Dt4fbzfVUrEJb92tSrReHALQQA3h5WkTA0qxhDd
9XyEWknDrYCWIWoj0XWjiVUre2fw3SKn8KHvJDeDYVKzYy18oA+da+xgs9b+n+Tq
mMlfslWhw9wRyp0jbVLEs3yxLgE4elbCCmgiTNpnmMW5AQ0EXERB4wEIAKCPJqmM
o8m6Xm163XtAZnx3t02EJSAV6u0yINIC8aEudNWg+/ptKKanUDm38dPnOl1mgOyC
FEu4qFJHbMidkEEac5J0lgvhRK7jv94KF3vxqKr/bYnxltghqCfXesga9jfAHV8J
M6sx4exOoc+/52YskpvDUs/eTPnWoQnbgjP+wsZpNq0owS6yO5urDfD6lvefgK5A
TfB9lQUE0lpb6IMKkcBZZvpZWOchbwPWCB9JZMuirDSyksuTLdqgEsW7MyKBjCae
E/THuTazumad/PyEb0RCbODdMb55L6CD2W2DUquVBLI9FN6KTYWk5L/JzNAIWBV9
TKfevup933j1m+sAEQEAAYkBPAQYAQgAJhYhBK9cqX/wEcCpQ6+5TFPDJcqRPXoQ
BQJcREHjAhsMBQkDwmcAAAoJEFPDJcqRPXoQGRgH/3592g1F4+WRaPbuCgfEMihd
ma5gplU2J7NjNbV9IcY8VZsGw7UAT7FfmTPqlvwFM3w3gQCDXCKGztieUkzMTPqb
LujBR4y55d5xDY6mP40zwRgdRlen2XsgHLPajRQpAhZq8ZvOdGe/ANCyXVdFHbGy
aFAMUfAhxkbITQKXH+EIkCHXDtDUHUxmAQvsZ8Z+Jm+ZwdhWkMsK43tw8UXLIynp
AeOoATdohke3EVK5+0Dc/jezcUWz2IKfw7LB3sQ4c6H8Ey8PThlNAIgwMCDp5WTB
DmFoRWTU6CpKtwIg/lb1ncbslH2xAFeUX6ASHXR8vBOnIXWss21FuAaNmWe4lmw=
=S+hs
-----END PGP PUBLIC KEY BLOCK-----""",
        sync_interval=7200,
    )
    collection.add(
        priority=2,
        url="http://alt.image.server",
        name="Alternative Image Server",
        keyring="""-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBFxEQeMBCACtgu58j4RuE34OW3Xoy4PIXlLv/8P+FUUFs8Dk4WO5zUJN2NfN
45fIASdKcH8cV2wbCVwjKEP0h4p5IE+lrwQK7bwYx7Qt+qmrm5eLMUM8IvXA18wf
AOPS7XeKTzxa4/jWagJupmmYL+MuV9o5haqYplOYCcVR135KAZfx743YuWcNqvcr
3Em0+gh4F2TXsefjniwuJRGY3Kbb/MAM2zC2f7FfCJVb1C30OLB+KwCddZP/23ll
nOqmzaVF0qQrHQ5EZGK3j3S4fzHNq14TMS3c21YkPOO/DV6BkgIHtG5NIIdVEdQh
wV8clpj0ZP7ShIE8cDhTy8k+xrIByPUVfpMpABEBAAG0J0JpbGwgQnVjaGFuYW4g
PHcuYnVjaGFuYW5AbmFwaWVyLmFjLnVrPokBVAQTAQgAPhYhBK9cqX/wEcCpQ6+5
TFPDJcqRPXoQBQJcREHjAhsDBQkDwmcABQsJCAcCBhUKCQgLAgQWAgMBAh4BAheA
AAoJEFPDJcqRPXoQ2KIH/2sRAsqbrqCMNMRsiBo9XtCFzQ052odbzubIScnwzrDF
Y9z+qPSAwaWGO+1R3LPDH5sMLQ2YOsNqg8VvTJBtOjR9YGNX9/bqqVFRKKSQ0HiD
Sb2M7phBdk4WLkqLZ/AfgHaLKpfNX0bq7WhqZ+Pez0nqjN08JkIog7LhaQZh/Chf
0pl+wHV0rEFuaDQn83yF5DWB1Dt4fbzfVUrEJb92tSrReHALQQA3h5WkTA0qxhDd
9XyEWknDrYCWIWoj0XWjiVUre2fw3SKn8KHvJDeDYVKzYy18oA+da+xgs9b+n+Tq
mMlfslWhw9wRyp0jbVLEs3yxLgE4elbCCmgiTNpnmMW5AQ0EXERB4wEIAKCPJqmM
o8m6Xm163XtAZnx3t02EJSAV6u0yINIC8aEudNWg+/ptKKanUDm38dPnOl1mgOyC
FEu4qFJHbMidkEEac5J0lgvhRK7jv94KF3vxqKr/bYnxltghqCfXesga9jfAHV8J
M6sx4exOoc+/52YskpvDUs/eTPnWoQnbgjP+wsZpNq0owS6yO5urDfD6lvefgK5A
TfB9lQUE0lpb6IMKkcBZZvpZWOchbwPWCB9JZMuirDSyksuTLdqgEsW7MyKBjCae
E/THuTazumad/PyEb0RCbODdMb55L6CD2W2DUquVBLI9FN6KTYWk5L/JzNAIWBV9
TKfevup933j1m+sAEQEAAYkBPAQYAQgAJhYhBK9cqX/wEcCpQ6+5TFPDJcqRPXoQ
BQJcREHjAhsMBQkDwmcAAAoJEFPDJcqRPXoQGRgH/3592g1F4+WRaPbuCgfEMihd
ma5gplU2J7NjNbV9IcY8VZsGw7UAT7FfmTPqlvwFM3w3gQCDXCKGztieUkzMTPqb
LujBR4y55d5xDY6mP40zwRgdRlen2XsgHLPajRQpAhZq8ZvOdGe/ANCyXVdFHbGy
aFAMUfAhxkbITQKXH+EIkCHXDtDUHUxmAQvsZ8Z+Jm+ZwdhWkMsK43tw8UXLIynp
AeOoATdohke3EVK5+0Dc/jezcUWz2IKfw7LB3sQ4c6H8Ey8PThlNAIgwMCDp5WTB
DmFoRWTU6CpKtwIg/lb1ncbslH2xAFeUX6ASHXR8vBOnIXWss21FuAaNmWe4lmw=
=S+hs
-----END PGP PUBLIC KEY BLOCK-----""",
        sync_interval=7200,
    )

    boot_sources = await collection.create(conn)

    collection = ModelCollection("boot_source_selection")
    collection.add(
        boot_source_id=boot_sources[0].id,
        label="stable",
        os="ubuntu",
        release="noble",
        arch="amd64",
        selected=True,
    )
    collection.add(
        boot_source_id=boot_sources[0].id,
        label="candidate",
        os="ubuntu",
        release="jammy",
        arch="amd64",
        selected=True,
    )
    collection.add(
        boot_source_id=boot_sources[0].id,
        label="candidate",
        os="ubuntu",
        release="jammy",
        arch="arm64",
        selected=True,
    )
    collection.add(
        boot_source_id=boot_sources[1].id,
        label="candidate",
        os="ubuntu",
        release="jammy",
        arch="amd64",
        selected=False,
    )

    await collection.create(conn)

    collection = ModelCollection("boot_asset")
    collection.add(
        boot_source_id=boot_sources[0].id,
        kind=0,
        label="stable",
        os="ubuntu",
        release="noble",
        version="24.04",
        krel="noble",
        codename="noble numbat",
        title="24.04 LTS",
        arch="amd64",
        subarch="ga-24.04",
        compatibility=["ga-24.04"],
        flavor="generic",
        base_image=None,
        eol=datetime(2029, 4, 1, tzinfo=UTC),
        esm_eol=datetime(2036, 4, 1, tzinfo=UTC),
        bootloader_type=None,
        signed=True,
    )

    collection.add(
        boot_source_id=boot_sources[0].id,
        kind=0,
        label="candidate",
        os="ubuntu",
        release="jammy",
        version="22.04",
        krel="jammy",
        codename="jammy jellyfish",
        title="22.04 LTS",
        arch="amd64",
        subarch="generic",
        compatibility=["generic"],
        flavor="generic",
        base_image=None,
        eol=datetime(2027, 4, 1, tzinfo=UTC),
        esm_eol=datetime(2034, 4, 1, tzinfo=UTC),
        bootloader_type=None,
        signed=True,
    )
    collection.add(
        boot_source_id=boot_sources[0].id,
        kind=0,
        label="candidate",
        os="ubuntu",
        release="jammy",
        version="22.04",
        krel="jammy",
        codename="jammy jellyfish",
        title="22.04 LTS",
        arch="arm64",
        subarch="generic",
        compatibility=["generic"],
        flavor="generic",
        base_image=None,
        eol=datetime(2027, 4, 1, tzinfo=UTC),
        esm_eol=datetime(2034, 4, 1, tzinfo=UTC),
        bootloader_type=None,
        signed=True,
    )
    collection.add(
        boot_source_id=boot_sources[0].id,
        kind=1,
        label="stable",
        os="grub-efi-signed",
        release=None,
        krel=None,
        codename=None,
        title=None,
        arch="amd64",
        version=None,
        subarch=None,
        compatibility=None,
        flavor=None,
        base_image=None,
        eol=None,
        esm_eol=None,
        bootloader_type="uefi",
        signed=True,
    )
    collection.add(
        boot_source_id=boot_sources[1].id,
        kind=0,
        label="candidate",
        os="ubuntu",
        release="jammy",
        krel="jammy",
        codename="jammy jellyfish",
        title="22.04 LTS",
        version="22.04",
        arch="amd64",
        subarch="generic",
        compatibility=["generic"],
        flavor="generic",
        base_image=None,
        eol=datetime(2027, 4, 1, tzinfo=UTC),
        esm_eol=datetime(2034, 4, 1, tzinfo=UTC),
        bootloader_type=None,
        signed=True,
    )

    # custom image
    collection.add(
        boot_source_id=CUSTOM_IMAGE_SOURCE_ID,
        kind=0,
        label="candidate",
        os="custom",
        release="plucky",
        krel=None,
        codename=None,
        title="25.04",
        version="25.04",
        arch="amd64",
        subarch=None,
        compatibility=None,
        flavor=None,
        base_image="custom/plucky",
        eol=datetime(3000, 1, 1, tzinfo=UTC),
        esm_eol=datetime(3000, 1, 1, tzinfo=UTC),
        bootloader_type=None,
        signed=False,
    )

    boot_assets = await collection.create(conn)

    collection = ModelCollection("boot_asset_version")
    # noble (0-1)
    collection.add(boot_asset_id=boot_assets[0].id, version="20240401.1")
    collection.add(boot_asset_id=boot_assets[0].id, version="20250401.1")
    # jammy amd64 (2-3)
    collection.add(boot_asset_id=boot_assets[1].id, version="20220401.1")
    collection.add(boot_asset_id=boot_assets[1].id, version="20230401.1")
    # jammy arm64 (4-5)
    collection.add(boot_asset_id=boot_assets[2].id, version="20220401.1")
    collection.add(boot_asset_id=boot_assets[2].id, version="20230401.1")
    # bootloader (6-7)
    collection.add(boot_asset_id=boot_assets[3].id, version="20200401.1")
    collection.add(boot_asset_id=boot_assets[3].id, version="20210401.1")

    # duplicate jammy (8-9)
    collection.add(boot_asset_id=boot_assets[4].id, version="20220401.1")
    collection.add(boot_asset_id=boot_assets[4].id, version="20230401.1")

    # custom plucky
    collection.add(boot_asset_id=boot_assets[5].id, version="20251212.1")

    boot_asset_versions = await collection.create(conn)

    collection = ModelCollection("boot_asset_item")
    # noble
    for version_id in [0, 1]:
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.BOOT_INITRD,
            sha256="1bca818efa07048a6368ddb093c79dc964daf18c17c95910bb9188cab1e3952d",
            path=f"noble/amd64/{boot_asset_versions[version_id].version}/ga-24.04/generic/boot-initrd",
            file_size=73067242,
            bytes_synced=73067242,
            source_package=None,
            source_release=None,
            source_version=None,
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.BOOT_KERNEL,
            sha256="f5079df42eda3657ef802d263211744dd6774b6d975eabfd2f0f3fc62b97fb49",
            path=f"noble/amd64/{boot_asset_versions[version_id].version}/ga-24.04/generic/boot-kernel",
            file_size=14981512,
            bytes_synced=14981512,
            source_package=None,
            source_release=None,
            source_version=None,
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.MANIFEST,
            sha256="c3c206393946c1bd2801106f84bad8b1e949a11a57425d9992b7838430352def",
            path=f"noble/amd64/{boot_asset_versions[version_id].version}/squashfs.manifest",
            file_size=18759,
            bytes_synced=18759,
            source_package=None,
            source_release=None,
            source_version=None,
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.SQUASHFS_IMAGE,
            sha256="c1a77484a804b3dcfd7b433c622ba7f2801786d33e30d556c4b40ef3e58e3bc2",
            path=f"noble/amd64/{boot_asset_versions[version_id].version}/squashfs",
            file_size=268480512,
            bytes_synced=268480512,
            source_package=None,
            source_release=None,
            source_version=None,
        )
    # jammy amd64
    for version_id in [2, 3, 8, 9]:
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.BOOT_INITRD,
            sha256="d539ad8c9dd6ca339749c7c2cfb672684f6cb8476cf2500a5e7a78895ad894eb",
            path=f"jammy/amd64/{boot_asset_versions[version_id].version}/generic/generic/boot-initrd",
            file_size=73067242,
            bytes_synced=73067242,
            source_package=None,
            source_release=None,
            source_version=None,
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.BOOT_KERNEL,
            sha256="41b1faab5ec2da6cf9a6c9d0b6a817dc3e656b00bee137ec2a71afa6711c1af9",
            path=f"jammy/amd64/{boot_asset_versions[version_id].version}/generic/generic/boot-kernel",
            file_size=14981512,
            bytes_synced=14981512,
            source_package=None,
            source_release=None,
            source_version=None,
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.MANIFEST,
            sha256="0b8fe8dbf00231753f0de0306f8687f416ef33ada3a390c5c3266dc9b2301625",
            path=f"jammy/amd64/{boot_asset_versions[version_id].version}/squashfs.manifest",
            file_size=18759,
            bytes_synced=18759,
            source_package=None,
            source_release=None,
            source_version=None,
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.SQUASHFS_IMAGE,
            sha256="74adfaece846b3f129b9b24b35ca554d16afbc3b1a0e24bb8568076809de232b",
            path=f"jammy/amd64/{boot_asset_versions[version_id].version}/squashfs",
            file_size=268480512,
            bytes_synced=268480512,
            source_package=None,
            source_release=None,
            source_version=None,
        )
    # jammy arm64
    for version_id in [4, 5]:
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.BOOT_INITRD,
            sha256="d539ad8c9dd6ca339749c7c2cfb672684f6cb8476cf2500a5e7a78895ad894eb",
            path=f"jammy/arm64/{boot_asset_versions[version_id].version}/generic/generic/boot-initrd",
            file_size=73067242,
            bytes_synced=73067242,
            source_package=None,
            source_release=None,
            source_version=None,
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.BOOT_KERNEL,
            sha256="41b1faab5ec2da6cf9a6c9d0b6a817dc3e656b00bee137ec2a71afa6711c1af9",
            path=f"jammy/arm64/{boot_asset_versions[version_id].version}/generic/generic/boot-kernel",
            file_size=14981512,
            bytes_synced=14981512,
            source_package=None,
            source_release=None,
            source_version=None,
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.MANIFEST,
            sha256="0b8fe8dbf00231753f0de0306f8687f416ef33ada3a390c5c3266dc9b2301625",
            path=f"jammy/arm64/{boot_asset_versions[version_id].version}/squashfs.manifest",
            file_size=18759,
            bytes_synced=18759,
            source_package=None,
            source_release=None,
            source_version=None,
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.SQUASHFS_IMAGE,
            sha256="74adfaece846b3f129b9b24b35ca554d16afbc3b1a0e24bb8568076809de232b",
            path=f"jammy/arm64/{boot_asset_versions[version_id].version}/squashfs",
            file_size=268480512,
            bytes_synced=268480512,
            source_package=None,
            source_release=None,
            source_version=None,
        )
    # bootloader
    for version_id in [6, 7]:
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="9d4a3a826ed55c46412613d2f7caf3185da4d6b18f35225f4f6a5b86b2bccfe3",
            path=f"bootloaders/uefi/amd64/{boot_asset_versions[version_id].version}/grub2-signed.tar.xz",
            file_size=375316,
            bytes_synced=375316,
            source_package="grub2-signed",
            source_release="focal",
            source_version="1.167.2+2.04-1ubuntu44.2",
        )
        collection.add(
            boot_asset_version_id=boot_asset_versions[version_id].id,
            ftype=ItemFileType.ARCHIVE_TAR_XZ,
            sha256="07b42d0aa2540b6999c726eacf383e2c8f172378c964bdefab6d71410e2b72db",
            path=f"bootloaders/uefi/amd64/{boot_asset_versions[version_id].version}/shim-signed.tar.xz",
            file_size=322336,
            bytes_synced=322336,
            source_package="shim-signed",
            source_release="focal",
            source_version="1.40.7+15.4-0ubuntu9",
        )
    # custom plucky
    collection.add(
        boot_asset_version_id=boot_asset_versions[10].id,
        ftype=ItemFileType.ROOT_TGZ,
        sha256="07b42d0aa2540b6999c726eacf383e2c8f172378c964bdefab6d71410e2b72db",
        path=f"plucky/amd64/{boot_asset_versions[10].version}/plucky-custom.tgz",
        file_size=123456,
        bytes_synced=123456,
        source_package=None,
        source_release=None,
        source_version=None,
    )
    await collection.create(conn)
    return boot_assets


async def purge_images(conn: AsyncConnection) -> None:
    """Delete all tokens"""
    await ModelCollection("boot_asset_item").purge(conn)
    await ModelCollection("boot_asset_version").purge(conn)
    await ModelCollection("boot_asset").purge(conn)
    await ModelCollection("boot_source_selection").purge(conn)
    await ModelCollection("boot_source").purge(conn, retain_custom_source=True)
