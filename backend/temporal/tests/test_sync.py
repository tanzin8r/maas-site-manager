from datetime import timedelta
import typing
import uuid

from activities.images import S3Params  # type: ignore
from activities.simplestream import (  # type: ignore
    FETCH_SS_INDEXES,
    GET_BOOT_SOURCE_ACTIVITY,
    LOAD_PRODUCT_MAP_ACTIVITY,
    FetchSsIndexesParams,
    FetchSsIndexesResult,
    GetBootSourceParams,
    GetBootSourceResult,
    LoadProductMapParams,
    LoadProductMapResult,
)
import pytest
from pytest_mock import MockerFixture
from temporalio import activity
from temporalio.exceptions import ApplicationError
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal.resources.workflows.sync import (
    SyncUpstreamSourceParams,
    SyncUpstreamSourceWorkflow,
)

TEST_WF_TIMEOUT = timedelta(seconds=30)


@pytest.fixture
def s3_params() -> S3Params:
    return S3Params(
        endpoint="https://radosgw.ceph.example.com",
        access_key="test-access",
        secret_key="test-secret",
        bucket="test-bucket",
        path="images/",
    )


@pytest.fixture
def sync_params(s3_params: S3Params) -> SyncUpstreamSourceParams:
    return SyncUpstreamSourceParams(
        msm_url="http://msm.example.com",
        msm_jwt="jwt-token",
        boot_source_id=1,
        s3_params=s3_params,
    )


@pytest.fixture
def boot_source_data() -> dict[str, typing.Any]:
    return {
        "boot-source": {
            "url": "http://upstream.example.com/streams/v1/index.sjson",
            "keyring": None,
        },
        "selections": {"ubuntu---noble": ["amd64"]},
    }


@pytest.fixture
def product_list() -> list[dict[str, typing.Any]]:
    return [
        {
            "label": "stable",
            "bootloader-type": "uefi",
            "arch": "amd64",
            "os": "grub-efi-signed",
            "sha256": "9d4a3a826ed55c46412613d2f7caf3185da4d6b18f35225f4f6a5b86b2bccfe3",
            "path": "bootloaders/uefi/amd64/20210819.0/grub2-signed.tar.xz",
            "file_size": 375316,
            "ftype": "archive.tar.xz",
            "source_package": None,
            "source_version": None,
            "source_release": None,
        },
        {
            "label": "stable",
            "bootloader-type": "uefi",
            "arch": "amd64",
            "os": "grub-efi-signed",
            "sha256": "07b42d0aa2540b6999c726eacf383e2c8f172378c964bdefab6d71410e2b72db",
            "path": "bootloaders/uefi/amd64/20210819.0/shim-signed.tar.xz",
            "file_size": 322336,
            "ftype": "archive.tar.xz",
            "source_package": None,
            "source_version": None,
            "source_release": None,
        },
        {
            "release_codename": "Oracular Oriole",
            "label": "stable",
            "release": "oracular",
            "support_esm_eol": "2025-07-10",
            "release_title": "24.10",
            "support_eol": "2025-07-10",
            "subarch": "ga-24.10",
            "kflavor": "generic",
            "arch": "s390x",
            "subarches": "generic,hwe-p,hwe-q,hwe-r,hwe-s,hwe-t,hwe-u,hwe-v,hwe-w,ga-16.04,ga-16.10,ga-17.04,ga-17.10,ga-18.04,ga-18.10,ga-19.04,ga-19.10,ga-20.04,ga-20.10,ga-21.04,ga-21.10,ga-22.04,ga-22.10,ga-23.04,ga-23.10,ga-24.04,ga-24.10",
            "os": "ubuntu",
            "sha256": "406e8ad24a6e7c13df29bcc1eb722ad7c45983958e6f9fb4116e0e223f65ba6a",
            "path": "oracular/s390x/20250325/ga-24.10/generic/boot-initrd",
            "file_size": 28415859,
            "ftype": "boot-initrd",
            "source_package": None,
            "source_version": None,
            "source_release": None,
        },
        {
            "release_codename": "Oracular Oriole",
            "label": "stable",
            "release": "oracular",
            "support_esm_eol": "2025-07-10",
            "release_title": "24.10",
            "support_eol": "2025-07-10",
            "subarch": "ga-24.10",
            "kflavor": "generic",
            "arch": "s390x",
            "subarches": "generic,hwe-p,hwe-q,hwe-r,hwe-s,hwe-t,hwe-u,hwe-v,hwe-w,ga-16.04,ga-16.10,ga-17.04,ga-17.10,ga-18.04,ga-18.10,ga-19.04,ga-19.10,ga-20.04,ga-20.10,ga-21.04,ga-21.10,ga-22.04,ga-22.10,ga-23.04,ga-23.10,ga-24.04,ga-24.10",
            "os": "ubuntu",
            "sha256": "78c9fd47c71d66d9423c3e0406e239fcc1fe1f39b2eda788efa9755215cb47b2",
            "path": "oracular/s390x/20250325/ga-24.10/generic/boot-kernel",
            "file_size": 10498616,
            "ftype": "boot-kernel",
            "source_package": None,
            "source_version": None,
            "source_release": None,
        },
        {
            "release_codename": "Oracular Oriole",
            "label": "stable",
            "release": "oracular",
            "support_esm_eol": "2025-07-10",
            "release_title": "24.10",
            "support_eol": "2025-07-10",
            "subarch": "ga-24.10",
            "kflavor": "generic",
            "arch": "s390x",
            "subarches": "generic,hwe-p,hwe-q,hwe-r,hwe-s,hwe-t,hwe-u,hwe-v,hwe-w,ga-16.04,ga-16.10,ga-17.04,ga-17.10,ga-18.04,ga-18.10,ga-19.04,ga-19.10,ga-20.04,ga-20.10,ga-21.04,ga-21.10,ga-22.04,ga-22.10,ga-23.04,ga-23.10,ga-24.04,ga-24.10",
            "os": "ubuntu",
            "sha256": "5ba4c5c37516a965b155466d03aca69102c0254478a8aac0677b5dcb43845d55",
            "path": "oracular/s390x/20250325/squashfs.manifest",
            "file_size": 17298,
            "ftype": "manifest",
            "source_package": None,
            "source_version": None,
            "source_release": None,
        },
        {
            "release_codename": "Oracular Oriole",
            "label": "stable",
            "release": "oracular",
            "support_esm_eol": "2025-07-10",
            "release_title": "24.10",
            "support_eol": "2025-07-10",
            "subarch": "ga-24.10",
            "kflavor": "generic",
            "arch": "s390x",
            "subarches": "generic,hwe-p,hwe-q,hwe-r,hwe-s,hwe-t,hwe-u,hwe-v,hwe-w,ga-16.04,ga-16.10,ga-17.04,ga-17.10,ga-18.04,ga-18.10,ga-19.04,ga-19.10,ga-20.04,ga-20.10,ga-21.04,ga-21.10,ga-22.04,ga-22.10,ga-23.04,ga-23.10,ga-24.04,ga-24.10",
            "os": "ubuntu",
            "sha256": "e7be50c1c74c5924c74ecfc9f7add55691dace0ee956d958562073236d71dc41",
            "path": "oracular/s390x/20250325/squashfs",
            "file_size": 268091392,
            "ftype": "squashfs",
            "source_package": None,
            "source_version": None,
            "source_release": None,
        },
    ]


class TestSyncUpstreamSourceWorkflow:
    @pytest.mark.asyncio
    async def test_sync_upstream_source_success(
        self,
        sync_params: SyncUpstreamSourceParams,
        boot_source_data: dict[str, typing.Any],
        product_list: list[dict[str, typing.Any]],
        mocker: MockerFixture,
    ) -> None:
        # Mock activities
        @activity.defn(name=GET_BOOT_SOURCE_ACTIVITY)
        async def get_boot_source_data_mock(
            params: GetBootSourceParams,
        ) -> GetBootSourceResult:
            return GetBootSourceResult(
                index_url=boot_source_data["boot-source"]["url"],
                keyring=boot_source_data["boot-source"]["keyring"],
                selections=boot_source_data["selections"],
            )

        @activity.defn(name=FETCH_SS_INDEXES)
        async def parse_ss_index_mock(
            params: FetchSsIndexesParams,
        ) -> FetchSsIndexesResult:
            assert (
                params.index_url
                == "http://upstream.example.com/streams/v1/index.sjson"
            )
            return FetchSsIndexesResult(
                "http://upstream.example.com/",
                True,
                ["http://upstream.example.com/streams/v1/prod1.json"],
            )

        @activity.defn(name=LOAD_PRODUCT_MAP_ACTIVITY)
        async def load_product_map_mock(
            params: LoadProductMapParams,
        ) -> LoadProductMapResult:
            if (
                params.index_url
                == "http://upstream.example.com/streams/v1/prod1.json"
            ):
                return LoadProductMapResult(product_list)
            raise ApplicationError("Unexpected URL", non_retryable=True)

        mock_store = mocker.patch(
            "temporal.resources.workflows.sync.MSMImageStore", autospec=True
        )

        # Act
        async with await WorkflowEnvironment.start_time_skipping() as env:
            async with Worker(
                env.client,
                task_queue="abcd:region",
                workflows=[SyncUpstreamSourceWorkflow],
                activities=[
                    get_boot_source_data_mock,
                    parse_ss_index_mock,
                    load_product_map_mock,
                ],
            ) as worker:
                result = await env.client.execute_workflow(
                    SyncUpstreamSourceWorkflow.run,
                    sync_params,
                    id=f"workflow-{uuid.uuid4()}",
                    task_queue=worker.task_queue,
                    run_timeout=TEST_WF_TIMEOUT,
                )

        # Assert
        assert result is True
        assert len(mock_store.mock_calls) == len(product_list) + 2
