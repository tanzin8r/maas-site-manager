import typing
from unittest.mock import AsyncMock, MagicMock

from activities.simplestream import (  # type: ignore
    FetchSsIndexesParams,
    GetBootSourceParams,
    LoadProductMapParams,
    SimpleStreamActivities,
)
from httpx import AsyncClient, Response
import pytest
from pytest_mock import MockerFixture
from temporalio.testing import ActivityEnvironment


class AsyncIterator:
    """
    Class for mocking async iterators, namely httpx Request.aiter_bytes()
    """

    def __init__(self, seq: list[typing.Any]) -> None:
        self.iter = iter(seq)

    def __aiter__(self) -> "AsyncIterator":
        return self

    async def __anext__(self) -> typing.Any:
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


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


class TestGetBootSourceActivity:
    @pytest.mark.asyncio
    async def test_get_boot_source_success(
        self, mocker: MockerFixture, ss_act: SimpleStreamActivities
    ) -> None:
        act_env = ActivityEnvironment()

        params = GetBootSourceParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            boot_source_id=42,
        )

        # Mock responses for boot source and selections
        boot_source_response = mocker.Mock()
        boot_source_response.status_code = 200
        boot_source_response.json.return_value = {
            "id": 42,
            "name": "test-source",
            "url": "http://test.source.url/streams/v1/index.sjson",
            "keyring": "test-keyring",
        }

        selections_response = mocker.Mock()
        selections_response.status_code = 200
        selections_response.json.return_value = {
            "items": [
                {
                    "os": "ubuntu",
                    "release": "oracular",
                    "arches": "amd64,arm64",
                },
                {"os": "ubuntu", "release": "questing", "arches": "amd64"},
            ]
        }

        # Patch the client.get method to return the correct response in order
        ss_act.client.get.side_effect = [
            boot_source_response,
            selections_response,
        ]

        # Act
        result = await act_env.run(ss_act.get_boot_source, params)

        # Assert
        assert result["boot_source"] == {
            "id": 42,
            "name": "test-source",
            "url": "http://test.source.url/streams/v1/index.sjson",
            "keyring": "test-keyring",
        }
        assert "selections" in result
        assert result["selections"]["ubuntu---oracular"] == ["amd64", "arm64"]
        assert result["selections"]["ubuntu---questing"] == ["amd64"]

    @pytest.mark.asyncio
    async def test_get_boot_source_failure(
        self, mocker: MockerFixture, ss_act: SimpleStreamActivities
    ) -> None:
        act_env = ActivityEnvironment()

        params = GetBootSourceParams(
            msm_base_url="http://test.msm.url",
            msm_jwt="test.jwt",
            boot_source_id=42,
        )

        # Simulate failure on first call
        fail_response = mocker.Mock()
        fail_response.status_code = 404
        fail_response.text = "Not found"
        ss_act.client.get.return_value = fail_response

        with pytest.raises(Exception):
            await act_env.run(ss_act.get_boot_source, params)


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
        base_url, signed, products = await act_env.run(
            ss_act.parse_ss_index, params
        )

        # Assert
        assert base_url == "http://example.com/"
        assert signed is True
        assert "http://example.com/streams/v1/prod1.json" in products
        assert "http://example.com/streams/v1/prod2.json" in products
        assert all("other.json" not in p for p in products)

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

        base_url, signed, products = await act_env.run(
            ss_act.parse_ss_index, params
        )
        assert base_url == "http://example.com/"
        assert signed is False
        assert products == []

    @pytest.mark.asyncio
    async def test_parse_ss_index_missing_index(
        self, ss_act: SimpleStreamActivities, mocker: MockerFixture
    ) -> None:
        act_env = ActivityEnvironment()
        mocker.patch.object(ss_act, "_download_json", return_value=({}, False))
        params = FetchSsIndexesParams(
            index_url="http://example.com/streams/v1/index.sjson",
        )

        base_url, _, products = await act_env.run(
            ss_act.parse_ss_index, params
        )
        assert base_url == "http://example.com/"
        assert products == []


class TestLoadProductMapActivity:
    @pytest.mark.asyncio
    async def test_load_product_map_valid(
        self, ss_act: SimpleStreamActivities, mocker: MockerFixture
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        products = {
            "products": {
                "prod1": {
                    "arch": "amd64",
                    "os": "ubuntu",
                    "release": "oracular",
                    "versions": {
                        "20250601": {
                            "items": {
                                "item1": {
                                    "sha256": "abc123",
                                    "path": "prod1/item1.img",
                                    "size": 12345,
                                    "ftype": "kernel",
                                    "source_package": "linux-image",
                                    "source_version": "1.0",
                                    "source_release": "24.04",
                                }
                            }
                        }
                    },
                }
            }
        }
        mocker.patch.object(
            ss_act, "_download_json", return_value=(products, False)
        )
        selections = {"ubuntu---oracular": ["amd64"]}

        params = LoadProductMapParams(
            index_url="http://example.com/streams/v1/index.sjson",
            selections=selections,
        )

        # Act
        result = await act_env.run(ss_act.load_product_map, params)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        item = result[0]
        assert item["arch"] == "amd64"
        assert item["os"] == "ubuntu"
        assert item["release"] == "oracular"
        assert item["sha256"] == "abc123"
        assert item["path"] == "prod1/item1.img"
        assert item["file_size"] == 12345
        assert item["ftype"] == "kernel"
        assert item["source_package"] == "linux-image"
        assert item["source_version"] == "1.0"
        assert item["source_release"] == "24.04"

    @pytest.mark.asyncio
    async def test_load_product_map_no_matching_selection(
        self, ss_act: SimpleStreamActivities, mocker: MockerFixture
    ) -> None:
        # Arrange
        act_env = ActivityEnvironment()
        products = {
            "products": {
                "prod1": {
                    "arch": "arm64",
                    "os": "ubuntu",
                    "release": "noble",
                    "versions": {
                        "20250601": {
                            "items": {
                                "item1": {
                                    "sha256": "abc123",
                                    "path": "prod1/item1.img",
                                    "size": 12345,
                                    "ftype": "kernel",
                                }
                            }
                        }
                    },
                }
            }
        }
        mocker.patch.object(
            ss_act, "_download_json", return_value=(products, False)
        )

        selections = {"ubuntu---noble": ["amd64"]}

        params = LoadProductMapParams(
            index_url="http://example.com/streams/v1/index.sjson",
            selections=selections,
        )

        # Act
        result = await act_env.run(ss_act.load_product_map, params)

        # Assert
        assert result == []
