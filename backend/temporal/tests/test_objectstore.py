from datetime import datetime
from unittest.mock import call

from activities.download_upstream_activities import (  # type: ignore
    BootAsset,
    BootAssetItem,
    BootAssetKind,
    BootAssetLabel,
    BootAssetVersion,
    S3Params,
)
from management.objectstore import MSMImageStore  # type: ignore
import pytest
from pytest_mock import MockerFixture
from temporalio import workflow
from temporalio.common import WorkflowIDReusePolicy
from temporalio.exceptions import ApplicationError
from temporalio.workflow import ParentClosePolicy
from workflows.download_upstream import (  # type: ignore
    DOWNLOAD_UPSTREAM_IMAGE_WF_NAME,
    GET_OR_CREATE_PRODUCT_WF_NAME,
    DownloadUpstreamImageParams,
    GetOrCreateProductParams,
)


class TestMSMImageStore:
    def test_start_download_workflow(self, mocker: MockerFixture) -> None:
        mock_start = mocker.patch.object(workflow, "execute_child_workflow")
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="accesskey",
            secret_key="secretkey",
            path="test/path",
            bucket="test-bucket",
        )
        image_store = MSMImageStore(
            "http://base.url",
            "test.jwt",
            s3_params,
        )
        test_item = {
            "ss_url": "http://test.ss.url",
            "id": 2,
        }
        image_store._start_download_workflow(test_item)
        mock_start.assert_called_once_with(
            DOWNLOAD_UPSTREAM_IMAGE_WF_NAME,
            DownloadUpstreamImageParams(
                test_item["ss_url"],
                "http://base.url/api/v1/bootasset-items/2",
                "test.jwt",
                2,
                s3_params,
            ),
            id="download-item-2",
            id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
            parent_close_policy=ParentClosePolicy.ABANDON,
        )

    async def test_get_asset_from_product_bootloader(
        self, mocker: MockerFixture
    ) -> None:
        product = {
            "bootloader-type": "uefi",
            "label": "stable",
            "os": "grub-efi-signed",
            "arch": "amd64",
        }
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="accesskey",
            secret_key="secretkey",
            path="test/path",
            bucket="test-bucket",
        )
        image_store = MSMImageStore("http://base.url", "test.jwt", s3_params)
        test_bootsource_id = 2
        returned_asset = image_store._get_asset_from_product(
            product, test_bootsource_id
        )

        expected_asset = BootAsset(
            boot_source_id=test_bootsource_id,
            kind=BootAssetKind.BOOTLOADER,
            label=BootAssetLabel.STABLE,
            os="grub-efi-signed",
            arch="amd64",
        )

        assert expected_asset == returned_asset

    async def test_get_asset_from_product_os(
        self, mocker: MockerFixture
    ) -> None:
        product = {
            "arch": "amd64",
            "kflavor": "generic",
            "krel": "precise",
            "label": "candidate",
            "os": "ubuntu",
            "release": "precise",
            "release_codename": "Precise Pangolin",
            "release_title": "12.04 LTS",
            "subarch": "hwe-p",
            "subarches": "generic,hwe-p",
            "support_eol": "2017-04-26",
            "support_esm_eol": "2019-04-26",
        }
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="accesskey",
            secret_key="secretkey",
            path="test/path",
            bucket="test-bucket",
        )
        image_store = MSMImageStore("http://base.url", "test.jwt", s3_params)
        test_bootsource_id = 2
        returned_asset = image_store._get_asset_from_product(
            product, test_bootsource_id
        )
        expected_asset = BootAsset(
            boot_source_id=test_bootsource_id,
            kind=BootAssetKind.OS,
            label=BootAssetLabel.CANDIDATE,
            os="ubuntu",
            arch="amd64",
            release="precise",
            codename="Precise Pangolin",
            title="12.04 LTS",
            subarch="hwe-p",
            compatibility=["generic", "hwe-p"],
            flavor="generic",
            eol=datetime.strptime("2017-04-26+0000", "%Y-%m-%d%z"),
            esm_eol=datetime.strptime("2019-04-26+0000", "%Y-%m-%d%z"),
        )
        assert expected_asset == returned_asset

    async def test_get_version_from_product(
        self, mocker: MockerFixture
    ) -> None:
        product = {"version": "20170417"}
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="accesskey",
            secret_key="secretkey",
            path="test/path",
            bucket="test-bucket",
        )
        image_store = MSMImageStore("http://base.url", "test.jwt", s3_params)
        returned_version = image_store._get_version_from_product(product)
        expected_version = BootAssetVersion(
            boot_asset_id=0, version="20170417"
        )
        assert expected_version == returned_version

    async def test_get_or_create_product(self, mocker: MockerFixture) -> None:
        expected_returned_id = 3
        mock_execute = mocker.patch.object(
            workflow,
            "execute_child_workflow",
            return_value=expected_returned_id,
        )
        product = {
            "bootloader-type": "uefi",
            "label": "stable",
            "os": "grub-efi-signed",
            "arch": "amd64",
            "version": "20170417",
            "ftype": "boot-initrd",
            "path": "precise/amd64/20170417/hwe-p/generic/boot-initrd",
            "sha256": "1d87c3e76b8ffd8ec724a2ca2c29bbf840981b615ee76060d851d546d218ed7d",
            "size": 19150429,
        }
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="accesskey",
            secret_key="secretkey",
            path="test/path",
            bucket="test-bucket",
        )
        test_bootsource_id = 2
        expected_asset = BootAsset(
            boot_source_id=test_bootsource_id,
            kind=BootAssetKind.BOOTLOADER,
            label=BootAssetLabel.STABLE,
            os="grub-efi-signed",
            arch="amd64",
        )
        expected_version = BootAssetVersion(
            boot_asset_id=0, version="20170417"
        )
        expected_item = BootAssetItem(
            boot_asset_version_id=0,
            ftype="boot-initrd",
            sha256="1d87c3e76b8ffd8ec724a2ca2c29bbf840981b615ee76060d851d546d218ed7d",
            path="precise/amd64/20170417/hwe-p/generic/boot-initrd",
            file_size=19150429,
        )
        mock_get_asset = mocker.patch.object(
            MSMImageStore,
            "_get_asset_from_product",
            return_value=expected_asset,
        )
        mock_get_version = mocker.patch.object(
            MSMImageStore,
            "_get_version_from_product",
            return_value=expected_version,
        )
        mock_get_item = mocker.patch.object(
            MSMImageStore, "_get_item_from_product", return_value=expected_item
        )

        image_store = MSMImageStore("http://base.url", "test.jwt", s3_params)
        result_id = await image_store._get_or_create_product(
            product, test_bootsource_id
        )
        mock_execute.assert_called_once_with(
            GET_OR_CREATE_PRODUCT_WF_NAME,
            GetOrCreateProductParams(
                msm_base_url="http://base.url",
                msm_jwt="test.jwt",
                asset=expected_asset,
                version=expected_version,
                item=expected_item,
            ),
            id=f"get-or-create-product-{product['sha256']}",
            id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
            parent_close_policy=ParentClosePolicy.TERMINATE,
        )
        assert result_id == expected_returned_id
        mock_get_asset.assert_called_once_with(
            product,
            test_bootsource_id,
        )
        mock_get_version.assert_called_once_with(product)
        mock_get_item.assert_called_once_with(product)

    async def test_insert(self, mocker: MockerFixture) -> None:
        mock_create_product = mocker.patch.object(
            MSMImageStore, "_get_or_create_product", return_value=1
        )
        product = {
            "bootloader-type": "uefi",
            "label": "stable",
            "os": "grub-efi-signed",
            "arch": "amd64",
            "version": "20170417",
            "ftype": "boot-initrd",
            "path": "precise/amd64/20170417/hwe-p/generic/boot-initrd",
            "sha256": "1d87c3e76b8ffd8ec724a2ca2c29bbf840981b615ee76060d851d546d218ed7d",
            "size": 19150429,
        }
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="accesskey",
            secret_key="secretkey",
            path="test/path",
            bucket="test-bucket",
        )
        image_store = MSMImageStore("http://base.url", "test.jwt", s3_params)
        await image_store.insert(product, "http://test.ss.url", 4)
        mock_create_product.assert_called_once_with(product, 4)
        assert image_store._files_to_download == {
            product["sha256"]: {"ss_url": "http://test.ss.url", "id": 1}
        }

    async def test_finalize(self, mocker: MockerFixture) -> None:
        async def start() -> bool:
            return True

        mock_start_wf = mocker.patch.object(
            MSMImageStore, "_start_download_workflow", return_value=start()
        )
        mocker.patch.object(workflow.logger, "info")
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="accesskey",
            secret_key="secretkey",
            path="test/path",
            bucket="test-bucket",
        )
        image_store = MSMImageStore("http://base.url", "test.jwt", s3_params)
        image_store._files_to_download = {
            "1": {"ss_url": "test-ss-url-1", "id": 1},
            "3": {"ss_url": "test-ss-url-2", "id": 2},
            "3": {"ss_url": "test-ss-url-3", "id": 3},
        }
        await image_store.finalize()
        mock_start_wf.assert_has_calls(
            [call(x) for x in image_store._files_to_download.values()]
        )

    async def test_finalize_wf_failed(self, mocker: MockerFixture) -> None:
        async def start() -> bool:
            return False

        mock_start_wf = mocker.patch.object(
            MSMImageStore, "_start_download_workflow", return_value=start()
        )
        mocker.patch.object(workflow.logger, "info")
        s3_params = S3Params(
            endpoint="http://s3",
            access_key="accesskey",
            secret_key="secretkey",
            path="test/path",
            bucket="test-bucket",
        )
        image_store = MSMImageStore("http://base.url", "test.jwt", s3_params)
        image_store._files_to_download = {
            "1": {"ss_url": "test-ss-url-1", "id": 1},
            "3": {"ss_url": "test-ss-url-2", "id": 2},
            "3": {"ss_url": "test-ss-url-3", "id": 3},
        }
        with pytest.raises(ApplicationError):
            await image_store.finalize()
        mock_start_wf.assert_has_calls(
            [call(x) for x in image_store._files_to_download.values()]
        )
