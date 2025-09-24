import asyncio
from collections.abc import Callable
import os
import tempfile
from typing import Any

PGP_SIGNED_MESSAGE_HEADER = "-----BEGIN PGP SIGNED MESSAGE-----"
PGP_SIGNATURE_HEADER = "-----BEGIN PGP SIGNATURE-----"
PGP_SIGNATURE_FOOTER = "-----END PGP SIGNATURE-----"

UBUNTU_CLOUDIMG_KEYRING = "/usr/share/keyrings/ubuntu-cloudimage-keyring.gpg"


class SignatureMissingException(Exception):
    pass


class SignatureInvalidException(Exception):
    pass


class UnsafeFilePathException(Exception):
    pass


def assert_safe_path(path: str | None) -> None:
    if path == "" or path is None:
        return
    path = str(path)
    if os.path.isabs(path):
        raise UnsafeFilePathException(f"Path '{path}' is absolute path")

    for tok in (".." + os.path.sep, "..." + os.path.sep):
        if path.startswith(tok):
            raise UnsafeFilePathException(f"Path '{path}' starts with '{tok}'")

    for tok in (
        os.path.sep + ".." + os.path.sep,
        os.path.sep + "..." + os.path.sep,
    ):
        if tok in path:
            raise UnsafeFilePathException(f"Path '{path}' contains '{tok}'")


async def read_signed(
    content: str, keyring: str | None = None, check: bool = True
) -> tuple[str, bool]:
    # ensure that content is signed by a key in keyring.
    # if no keyring given use default.
    signed_by_cpc = False

    if not content.startswith(PGP_SIGNED_MESSAGE_HEADER):
        raise SignatureMissingException("No signature found")

    if check:
        with tempfile.NamedTemporaryFile(mode="w+t") as key_file:
            if keyring:
                key_file.write(keyring)
                keypath = key_file.name
            else:
                keypath = UBUNTU_CLOUDIMG_KEYRING
                signed_by_cpc = True

            cmd = ["gpgv", f"--keyring={keypath}", "-"]
            sh = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await sh.communicate(input=content.encode())
            if sh.returncode != 0:
                raise SignatureInvalidException(stderr)

    output: list[str] = []
    mode = "garbage"
    for line in content.splitlines():
        if line == PGP_SIGNED_MESSAGE_HEADER:
            mode = "header"
        elif mode == "header":
            if line != "":
                mode = "body"
        elif line == PGP_SIGNATURE_HEADER:
            mode = "signature"
        elif line == PGP_SIGNATURE_FOOTER:
            mode = "garbage"
        elif mode == "body":
            # dash-escaped content in body
            if line.startswith("- "):
                output.append(line[2:])
            else:
                output.append(line)

    output.append("")  # need empty line at end
    return "\n".join(output), signed_by_cpc


_UNSET = object()


def walk_products(
    tree: dict[str, Any],
    cb_product: Callable[[dict[str, Any], str], Any] | None = None,
    cb_version: Callable[[dict[str, Any], str, str], Any] | None = None,
    cb_item: Callable[[dict[str, Any], str, str, str], Any] | None = None,
    ret_finished: object = _UNSET,
) -> None:
    for prodname, proddata in tree["products"].items():
        if cb_product:
            ret = cb_product(proddata, prodname)
            if ret_finished != _UNSET and ret == ret_finished:
                return

        if (not cb_version and not cb_item) or "versions" not in proddata:
            continue

        for vername, verdata in proddata["versions"].items():
            if cb_version:
                ret = cb_version(verdata, prodname, vername)
                if ret_finished != _UNSET and ret == ret_finished:
                    return

            if not cb_item or "items" not in verdata:
                continue

            for itemname, itemdata in verdata["items"].items():
                ret = cb_item(itemdata, prodname, vername, itemname)
                if ret_finished != _UNSET and ret == ret_finished:
                    return


def check_tree_paths(tree: dict[str, Any], format: str) -> None:
    format = format or tree.get("format", "products:1.0")

    if format == "products:1.0":
        walk_products(
            tree,
            cb_item=lambda item, x, y, z: assert_safe_path(item.get("path")),
        )
    elif format == "index:1.0":
        for entry in tree.get("index", {}).values():
            assert_safe_path(entry.get("path"))
    else:
        raise ValueError(
            f"Unknown format {format} for tree {tree.get('name', 'unknown')}"
        )
