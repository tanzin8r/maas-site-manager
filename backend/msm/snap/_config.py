import dataclasses
from pathlib import Path
from typing import (
    Any,
    ClassVar,
)

from jinja2 import (
    Environment,
    FileSystemLoader,
)
from jinja2.environment import Template

TEMPLATES_DIR = Path(__file__).parent / "templates"
TEMPLATES = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


@dataclasses.dataclass
class ConfigRenderer:
    """Render a configuration template to file."""

    template_name: ClassVar[str]

    @property
    def template(self) -> Template:
        return TEMPLATES.get_template(self.template_name)

    def template_data(self) -> dict[str, Any]:
        """Return data to render the config template."""
        return dataclasses.asdict(self)

    def render(self) -> str:
        """Return the rendered template."""
        return self.template.render(self.template_data())

    def write(self, path: Path) -> None:
        """Write the configuration to file."""
        path.write_text(self.render())


@dataclasses.dataclass
class NginxConfig(ConfigRenderer):
    base_dir: Path
    data_dir: Path
    port: int
    api_socket: Path

    template_name = "nginx.conf"
