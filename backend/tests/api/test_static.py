from collections.abc import Generator
import os
from pathlib import Path

from bs4 import BeautifulSoup as bs
import pytest
from pytest_mock import MockerFixture

from msm.api import _update_resource_paths
from tests.fixtures.client import Client

test_html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <script>
      globalThis.__ROOT_PATH__ = "";
      globalThis.__assetsPath__ = (path) => [globalThis.__ROOT_PATH__, "/ui/", path].filter(Boolean).join("/").replace(/([^:])(\/\/+)/g, '$1/');
    </script>
    <link rel="icon" type="image/png" href="/ui/maas-favicon-32px.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MAAS Site Manager</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""


@pytest.fixture(scope="session")
def static_file_dir(
    tmp_path_factory: pytest.TempPathFactory
) -> Generator[Path, None, None]:
    tmp_file_dir = tmp_path_factory.mktemp("static")
    tmp_valid_path = tmp_file_dir / "valid.js"
    tmp_index_path = tmp_file_dir / "index.html"
    with open(tmp_valid_path, "w") as f:
        f.write("const message = 'Hello world'")
    with open(tmp_index_path, "w") as f:
        f.write(test_html)
    yield tmp_file_dir
    print("Removing image...")
    os.remove(tmp_valid_path)
    os.remove(tmp_index_path)


@pytest.mark.asyncio
class TestStatic:
    @pytest.mark.parametrize("url", ["/", "/ui"])
    async def test_redirect(self, app_client: Client, url: str) -> None:
        response = await app_client.request("GET", url)
        assert response.status_code == 307

    @pytest.mark.parametrize("url", ["/ui/unknown", "/ui/index.html"])
    async def test_index(
        self,
        app_client: Client,
        url: str,
        mocker: MockerFixture,
        static_file_dir: Path,
    ) -> None:
        mocker.patch(
            "msm.api.Settings.static_dir",
            return_value=str(static_file_dir),
            new_callable=mocker.PropertyMock,
        )
        response = await app_client.request("GET", url)
        with open(static_file_dir / "index.html") as f:
            soup = bs(f, features="html.parser")
        _update_resource_paths(soup, "")
        assert response.status_code == 200
        assert response.text == str(soup)

    async def test_valid(
        self, app_client: Client, mocker: MockerFixture, static_file_dir: Path
    ) -> None:
        mocker.patch(
            "msm.api.Settings.static_dir",
            return_value=str(static_file_dir),
            new_callable=mocker.PropertyMock,
        )
        response = await app_client.request("GET", "/ui/valid.js")
        assert response.status_code == 200
        assert response.text == "const message = 'Hello world'"
