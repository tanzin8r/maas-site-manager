import pytest

from tests.fixtures.bootassets import (
    boot_source,
    boot_source_custom,
    boot_source_grub,
    boot_source_low,
    centos,
    grub,
    items_grub,
    items_ubuntu_jammy_1,
    items_ubuntu_noble_1,
    items_ubuntu_noble_2,
    last_sync,
    prev_sync,
    sel_centos,
    sel_ubuntu_jammy,
    sel_ubuntu_noble,
    ubuntu_jammy,
    ubuntu_noble,
    ver_grub,
    ver_ubuntu_jammy_1,
    ver_ubuntu_noble_1,
    ver_ubuntu_noble_2,
    ver_ubuntu_noble_2_reloaded,
)
from tests.fixtures.db import (
    db,
    db_connection,
    db_setup,
    transaction_middleware_class,
)
from tests.fixtures.env import (
    settings_environ,
    unset_settings_environ,
)
from tests.fixtures.factory import factory

__all__ = [
    "boot_source_custom",
    "boot_source_grub",
    "boot_source_low",
    "boot_source",
    "centos",
    "db_connection",
    "db_setup",
    "db",
    "factory",
    "grub",
    "items_grub",
    "items_ubuntu_jammy_1",
    "items_ubuntu_noble_1",
    "items_ubuntu_noble_2",
    "last_sync",
    "prev_sync",
    "sel_centos",
    "sel_ubuntu_jammy",
    "sel_ubuntu_noble",
    "settings_environ",
    "transaction_middleware_class",
    "ubuntu_jammy",
    "ubuntu_noble",
    "unset_settings_environ",
    "ver_grub",
    "ver_ubuntu_jammy_1",
    "ver_ubuntu_noble_1",
    "ver_ubuntu_noble_2_reloaded",
    "ver_ubuntu_noble_2",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--sqlalchemy-debug",
        help="print out SQLALchemy queries",
        action="store_true",
    )
