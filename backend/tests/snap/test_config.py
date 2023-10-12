from pathlib import Path
from typing import Iterator

import pytest

from msm.snap._config import NginxConfig


@pytest.fixture
def config() -> Iterator[NginxConfig]:
    yield NginxConfig(
        base_dir=Path("/path/base"),
        data_dir=Path("/path/data"),
        port=1234,
        api_socket=Path("/path/api.socket"),
    )


class TestNginxConfig:
    def test_template_data(self, config: NginxConfig) -> None:
        assert config.template_data() == {
            "base_dir": Path("/path/base"),
            "data_dir": Path("/path/data"),
            "port": 1234,
            "api_socket": Path("/path/api.socket"),
        }

    def test_render(self, config: NginxConfig) -> None:
        content = config.render()
        assert f"root {config.base_dir}/static;" in content
        assert "listen 1234;" in content
        assert "listen [::]:1234;" in content
        assert f"server unix:{config.api_socket};" in content

    def test_write(self, tmp_path: Path, config: NginxConfig) -> None:
        outfile = tmp_path / "nginx.conf"
        content = config.render()
        config.write(outfile)
        assert outfile.read_text() == content
