import json
import typing
from unittest.mock import AsyncMock, MagicMock

from activities.simplestream import (  # type: ignore
    FetchAssetListParams,
    FetchAssetListResult,
    FetchSsIndexesParams,
    LoadProductMapParams,
    LoadProductMapResult,
    Product,
    SimpleStreamActivities,
)
from httpx import AsyncClient, Response
import pytest
from pytest_mock import MockerFixture
from temporalio.testing import ActivityEnvironment

from temporal.tests.activities import AsyncIterator


@pytest.fixture
async def ss_act(mocker: MockerFixture) -> SimpleStreamActivities:
    mock_response = mocker.create_autospec(Response)
    mock_response.aiter_bytes.return_value = AsyncIterator([b"abc", b"def"])

    mock_client = mocker.create_autospec(AsyncClient)
    mock_client.stream.return_value.__aenter__.return_value = mock_response
    mocker.patch.object(
        SimpleStreamActivities, "_create_client", return_value=mock_client
    )
    return SimpleStreamActivities()


@pytest.fixture
def ss_product_noble() -> typing.Any:
    return json.loads("""\
{
 "content_id": "com.ubuntu.maas:stable:v3:download",
 "datatype": "image-ids",
 "format": "products:1.0",
 "products": {
  "com.ubuntu.maas.stable:v3:boot:24.04:amd64:ga-24.04": {
   "arch": "amd64",
   "kflavor": "generic",
   "krel": "noble",
   "label": "stable",
   "os": "ubuntu",
   "release": "noble",
   "release_codename": "Noble Numbat",
   "release_title": "24.04 LTS",
   "subarch": "ga-24.04",
   "subarches": "generic,hwe-p,hwe-q,hwe-r,hwe-s,hwe-t,hwe-u,hwe-v,hwe-w,ga-16.04,ga-16.10,ga-17.04,ga-17.10,ga-18.04,ga-18.10,ga-19.04,ga-19.10,ga-20.04,ga-20.10,ga-21.04,ga-21.10,ga-22.04,ga-22.10,ga-23.04,ga-23.10,ga-24.04",
   "support_eol": "2029-05-31",
   "support_esm_eol": "2034-04-25",
   "version": "24.04",
   "versions": {
    "20250716": {
     "items": {
      "boot-initrd": {
       "ftype": "boot-initrd",
       "kpackage": "linux-generic",
       "path": "noble/amd64/20250716/ga-24.04/generic/boot-initrd",
       "sha256": "bde9fbe54d2301403f5aafef264bbbe960e96c1384663ae414ba527f3b41fab8",
       "size": 78320226
      },
      "boot-kernel": {
       "ftype": "boot-kernel",
       "kpackage": "linux-generic",
       "path": "noble/amd64/20250716/ga-24.04/generic/boot-kernel",
       "sha256": "67cd9af083515de2101de032b49a64fc4b65778e5383df6ef21cf788a3f4688e",
       "size": 15010184
      },
      "manifest": {
       "ftype": "manifest",
       "path": "noble/amd64/20250716/squashfs.manifest",
       "sha256": "01a0481afa758a0b52664604a1db3c185c52a34488acedd4f58dce1dcfd1cd1f",
       "size": 18943
      },
      "squashfs": {
       "ftype": "squashfs",
       "path": "noble/amd64/20250716/squashfs",
       "sha256": "df6706086e706fd6126426c5e03400f13f4a8318e36d1d1a01eccf73a4c19f34",
       "size": 271847424
      }
     }
    },
    "20250805": {
     "items": {
      "boot-initrd": {
       "ftype": "boot-initrd",
       "kpackage": "linux-generic",
       "path": "noble/amd64/20250805/ga-24.04/generic/boot-initrd",
       "sha256": "1940dad3f4761308e9eef8cf1869b3c1c185c88e72ffbf3c94e97deca3638b69",
       "size": 78333904
      },
      "boot-kernel": {
       "ftype": "boot-kernel",
       "kpackage": "linux-generic",
       "path": "noble/amd64/20250805/ga-24.04/generic/boot-kernel",
       "sha256": "f82754bc29f710b2f0143fe0b19a2b2f40652c026cc6de44d75f3f991019c1ff",
       "size": 15006088
      },
      "manifest": {
       "ftype": "manifest",
       "path": "noble/amd64/20250805/squashfs.manifest",
       "sha256": "b5bedb0b99372b9d9368c418a0cd57506544bf1ce63b4d5164cb19101441e7e2",
       "size": 18977
      },
      "squashfs": {
       "ftype": "squashfs",
       "path": "noble/amd64/20250805/squashfs",
       "sha256": "4369b408d0b5c132b93652be8c7706a2d4ec1b54d511341ace8769967f23df2a",
       "size": 274694144
      }
     }
    }
   }
  }
 }
}
""")


@pytest.fixture
def ss_product_complex() -> typing.Any:
    return json.loads("""\
{
 "content_id": "com.ubuntu.maas:stable:v3:download",
 "datatype": "image-ids",
 "format": "products:1.0",
 "products": {
  "com.ubuntu.maas.stable:v3:boot:24.04:amd64:ga-24.04": {
   "arch": "amd64",
   "kflavor": "generic",
   "krel": "noble",
   "label": "stable",
   "os": "ubuntu",
   "release": "noble",
   "release_codename": "Noble Numbat",
   "release_title": "24.04 LTS",
   "subarch": "ga-24.04",
   "subarches": "generic,hwe-p,hwe-q,hwe-r,hwe-s,hwe-t,hwe-u,hwe-v,hwe-w,ga-16.04,ga-16.10,ga-17.04,ga-17.10,ga-18.04,ga-18.10,ga-19.04,ga-19.10,ga-20.04,ga-20.10,ga-21.04,ga-21.10,ga-22.04,ga-22.10,ga-23.04,ga-23.10,ga-24.04",
   "support_eol": "2029-05-31",
   "support_esm_eol": "2034-04-25",
   "version": "24.04",
   "versions": {
    "20250805": {
     "items": {
      "boot-initrd": {
       "ftype": "boot-initrd",
       "kpackage": "linux-generic",
       "path": "noble/amd64/20250805/ga-24.04/generic/boot-initrd",
       "sha256": "1940dad3f4761308e9eef8cf1869b3c1c185c88e72ffbf3c94e97deca3638b69",
       "size": 78333904
      },
      "boot-kernel": {
       "ftype": "boot-kernel",
       "kpackage": "linux-generic",
       "path": "noble/amd64/20250805/ga-24.04/generic/boot-kernel",
       "sha256": "f82754bc29f710b2f0143fe0b19a2b2f40652c026cc6de44d75f3f991019c1ff",
       "size": 15006088
      },
      "manifest": {
       "ftype": "manifest",
       "path": "noble/amd64/20250805/squashfs.manifest",
       "sha256": "b5bedb0b99372b9d9368c418a0cd57506544bf1ce63b4d5164cb19101441e7e2",
       "size": 18977
      },
      "squashfs": {
       "ftype": "squashfs",
       "path": "noble/amd64/20250805/squashfs",
       "sha256": "4369b408d0b5c132b93652be8c7706a2d4ec1b54d511341ace8769967f23df2a",
       "size": 274694144
      }
     }
    }
   }
  },
  "com.ubuntu.maas.stable:v3:boot:25.04:s390x:ga-25.04": {
   "arch": "s390x",
   "kflavor": "generic",
   "krel": "plucky",
   "label": "stable",
   "os": "ubuntu",
   "release": "plucky",
   "release_codename": "Plucky Puffin",
   "release_title": "25.04",
   "subarch": "ga-25.04",
   "subarches": "generic,hwe-p,hwe-q,hwe-r,hwe-s,hwe-t,hwe-u,hwe-v,hwe-w,ga-16.04,ga-16.10,ga-17.04,ga-17.10,ga-18.04,ga-18.10,ga-19.04,ga-19.10,ga-20.04,ga-20.10,ga-21.04,ga-21.10,ga-22.04,ga-22.10,ga-23.04,ga-23.10,ga-24.04,ga-24.10,ga-25.04",
   "support_eol": "2026-01-15",
   "support_esm_eol": "2026-01-15",
   "version": "25.04",
   "versions": {
    "20250729": {
     "items": {
      "boot-initrd": {
       "ftype": "boot-initrd",
       "kpackage": "linux-generic",
       "path": "plucky/s390x/20250729/ga-25.04/generic/boot-initrd",
       "sha256": "765aa0791a089f0b023f3bbc124856aca38557507c1227bdbe8feb330035193e",
       "size": 33205895
      },
      "boot-kernel": {
       "ftype": "boot-kernel",
       "kpackage": "linux-generic",
       "path": "plucky/s390x/20250729/ga-25.04/generic/boot-kernel",
       "sha256": "c14c340f1ea761c19c347919e6e54dcbe6ae76db33971efedaecdc160e85902e",
       "size": 10715704
      },
      "manifest": {
       "ftype": "manifest",
       "path": "plucky/s390x/20250729/squashfs.manifest",
       "sha256": "4e2c0886591e5cb136a7889a5eb236ff15f831bb5151f7957028c0bd9285bfcd",
       "size": 17235
      },
      "squashfs": {
       "ftype": "squashfs",
       "path": "plucky/s390x/20250729/squashfs",
       "sha256": "557909d4617c0171232efbba960b83e3c962c2cd4f0d786e8de01ac9ed0a2c21",
       "size": 278691840
      }
     }
    }
   }
  },
  "com.ubuntu.maas.stable:1:grub-efi-signed:uefi:amd64": {
   "arch": "amd64",
   "arches": "amd64",
   "bootloader-type": "uefi",
   "label": "stable",
   "os": "grub-efi-signed",
   "versions": {
    "20210819.0": {
     "items": {
      "grub2-signed": {
       "ftype": "archive.tar.xz",
       "path": "bootloaders/uefi/amd64/20210819.0/grub2-signed.tar.xz",
       "sha256": "9d4a3a826ed55c46412613d2f7caf3185da4d6b18f35225f4f6a5b86b2bccfe3",
       "size": 375316,
       "src_package": "grub2-signed",
       "src_release": "focal",
       "src_version": "1.167.2+2.04-1ubuntu44.2"
      },
      "shim-signed": {
       "ftype": "archive.tar.xz",
       "path": "bootloaders/uefi/amd64/20210819.0/shim-signed.tar.xz",
       "sha256": "07b42d0aa2540b6999c726eacf383e2c8f172378c964bdefab6d71410e2b72db",
       "size": 322336,
       "src_package": "shim-signed",
       "src_release": "focal",
       "src_version": "1.40.7+15.4-0ubuntu9"
      }
     }
    }
   }
  },
  "com.ubuntu.maas.stable:centos-bases:7.0:amd64": {
   "arch": "amd64",
   "label": "stable",
   "os": "centos",
   "release": "centos70",
   "release_title": "CentOS 7",
   "subarch": "generic",
   "subarches": "generic",
   "support_eol": "2024-06-30",
   "version": "7.0",
   "versions": {
    "20240128_01": {
     "items": {
      "manifest": {
       "ftype": "manifest",
       "path": "centos/centos70/amd64/20240128_01/root-tgz.manifest",
       "sha256": "1824770031fe2c6bb642ab0f3a7e6ffa58394072516ac453ebbe2c1377abd239",
       "size": 10794
      },
      "root-tgz": {
       "ftype": "root-tgz",
       "path": "centos/centos70/amd64/20240128_01/root-tgz",
       "sha256": "e928234f396e4fc981e1bf59c8532c1d2c625957f2322190995c40ee50736394",
       "size": 542934905
      }
     }
    }
   }
  } 
 }
}
""")


class TestDownloadJson:
    @pytest.mark.asyncio
    async def test_download_json_plain(
        self, ss_act: SimpleStreamActivities, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = b'{"foo": "bar"}'
        mocker.patch.object(ss_act.client, "get", return_value=mock_response)

        # Act
        result, signed = await ss_act._download_json(
            "http://test.url/streams/v1/index.json"
        )

        # Assert
        assert result == {"foo": "bar"}
        assert signed is False

    @pytest.mark.asyncio
    async def test_download_json_signed(
        self, ss_act: SimpleStreamActivities, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = b'"signed-content"'
        mocker.patch.object(ss_act.client, "get", return_value=mock_response)
        # Patch read_signed to return JSON string and True
        mocker.patch(
            "activities.simplestream.read_signed",
            AsyncMock(return_value=('{"foo": "bar"}', True)),
        )

        # Act
        result, signed = await ss_act._download_json(
            "http://test.url/streams/v1/index.sjson", keyring="keyring"
        )

        # Assert
        assert result == {"foo": "bar"}
        assert signed is True

    @pytest.mark.asyncio
    async def test_download_json_http_error(
        self, ss_act: SimpleStreamActivities, mocker: MockerFixture
    ) -> None:
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mocker.patch.object(ss_act.client, "get", return_value=mock_response)

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            await ss_act._download_json(
                "http://test.url/streams/v1/index.json"
            )
        assert "Failed to download JSON" in str(excinfo.value)


class TestParseSsIndexActivity:
    @pytest.mark.asyncio
    async def test_parse_ss_index_valid(
        self, ss_act: SimpleStreamActivities, mocker: MockerFixture
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        index_url = "http://example.com/streams/v1/index.sjson"
        mocker.patch.object(
            ss_act,
            "_download_json",
            return_value=(
                {
                    "index": {
                        "prod1": {
                            "format": "products:1.0",
                            "path": "streams/v1/prod1.json",
                        },
                        "prod2": {
                            "format": "products:1.0",
                            "path": "streams/v1/prod2.json",
                        },
                        "other": {
                            "format": "other:1.0",
                            "path": "streams/v1/other.json",
                        },
                    }
                },
                True,
            ),
        )
        params = FetchSsIndexesParams(
            index_url=index_url,
        )

        # Act
        result = await act_env.run(ss_act.parse_ss_index, params)

        # Assert
        assert result.base_url == "http://example.com"
        assert result.signed is True
        assert "http://example.com/streams/v1/prod1.json" in result.products
        assert "http://example.com/streams/v1/prod2.json" in result.products
        assert all("other.json" not in p for p in result.products)

    @pytest.mark.asyncio
    async def test_parse_ss_index_empty_index(
        self, ss_act: SimpleStreamActivities, mocker: MockerFixture
    ) -> None:
        act_env = ActivityEnvironment()
        mocker.patch.object(
            ss_act, "_download_json", return_value=({"index": {}}, False)
        )
        params = FetchSsIndexesParams(
            index_url="http://example.com/streams/v1/index.sjson",
        )

        result = await act_env.run(ss_act.parse_ss_index, params)
        assert result.base_url == "http://example.com"
        assert result.signed is False
        assert result.products == []

    @pytest.mark.asyncio
    async def test_parse_ss_index_missing_index(
        self, ss_act: SimpleStreamActivities, mocker: MockerFixture
    ) -> None:
        act_env = ActivityEnvironment()
        mocker.patch.object(ss_act, "_download_json", return_value=({}, False))
        params = FetchSsIndexesParams(
            index_url="http://example.com/streams/v1/index.sjson",
        )

        result = await act_env.run(ss_act.parse_ss_index, params)
        assert result.base_url == "http://example.com"
        assert result.products == []


class TestLoadProductMapActivity:
    @pytest.mark.asyncio
    async def test_load_product_map_valid(
        self,
        ss_act: SimpleStreamActivities,
        mocker: MockerFixture,
        ss_product_complex: typing.Any,
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        mocker.patch.object(
            ss_act, "_download_json", return_value=(ss_product_complex, False)
        )
        selections = [
            "ubuntu---noble---amd64",
            "ubuntu---plucky---s390x",
            "centos---centos70---amd64",
        ]

        params = LoadProductMapParams(
            index_url="http://example.com/streams/v1/index.sjson",
            selections=selections,
        )

        # Act
        result = await act_env.run(ss_act.load_product_map, params)

        # Assert
        assert isinstance(result, LoadProductMapResult)
        assert len(result.items) == 4

        assert result.items[0].os == "centos"
        assert result.items[1].os == "grub-efi-signed"
        assert result.items[2].os == "ubuntu"
        assert result.items[3].os == "ubuntu"

        item = result.items[2]
        assert isinstance(item, Product)
        assert item.arch == "amd64"
        assert item.os == "ubuntu"
        assert item.release == "noble"

        assert len(item.versions) == 1
        version, asset_list = item.versions.popitem()
        assert version == "20250805"
        item = asset_list[0]
        assert item.path == "noble/amd64/20250805/ga-24.04/generic/boot-initrd"
        assert item.file_size == 78333904
        assert item.ftype == "boot-initrd"
        assert item.source_package is None
        assert item.source_version is None
        assert item.source_release is None

    @pytest.mark.asyncio
    async def test_load_product_map_no_matching_selection(
        self,
        ss_act: SimpleStreamActivities,
        mocker: MockerFixture,
        ss_product_noble: typing.Any,
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        mocker.patch.object(
            ss_act, "_download_json", return_value=(ss_product_noble, False)
        )

        selections = ["ubuntu---oracular---amd64"]

        params = LoadProductMapParams(
            index_url="http://example.com/streams/v1/index.sjson",
            selections=selections,
        )

        # Act
        result = await act_env.run(ss_act.load_product_map, params)

        # Assert
        assert result.items == []


class TestFetchAsAssetListActivity:
    @pytest.mark.asyncio
    async def test_fetch_ss_asset_list(
        self,
        ss_act: SimpleStreamActivities,
        mocker: MockerFixture,
        ss_product_complex: typing.Any,
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        mocker.patch.object(
            ss_act, "_download_json", return_value=(ss_product_complex, False)
        )

        params = FetchAssetListParams(
            index_url="http://example.com/streams/v1/index.sjson",
        )

        # Act
        result = await act_env.run(ss_act.fetch_ss_asset_list, params)

        # Assert
        assert isinstance(result, FetchAssetListResult)
        assert len(result.assets) == 3

        assert result.assets[0].os == "centos"
        assert result.assets[0].release == "centos70"
        assert result.assets[0].arch == "amd64"

        assert result.assets[1].os == "ubuntu"
        assert result.assets[1].release == "noble"
        assert result.assets[1].arch == "amd64"

        assert result.assets[2].os == "ubuntu"
        assert result.assets[2].release == "plucky"
        assert result.assets[2].arch == "s390x"
