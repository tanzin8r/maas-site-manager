import os
from typing import Any

import pytest

from msm.temporal.management.utils import (
    PGP_SIGNATURE_FOOTER,
    PGP_SIGNATURE_HEADER,
    PGP_SIGNED_MESSAGE_HEADER,
    SignatureInvalidException,
    SignatureMissingException,
    UnsafeFilePathException,
    assert_safe_path,
    check_tree_paths,
    read_signed,
    walk_products,
)


class TestAssertSafePath:
    @pytest.mark.parametrize(
        "path",
        [
            None,
            "",
            "file.txt",
            "folder/file.txt",
            "folder\\file.txt",
            "subdir/another/file.txt",
        ],
    )
    def test_assert_safe_path_valid(self, path: str) -> None:
        # Should not raise for safe paths
        assert_safe_path(path)

    @pytest.mark.parametrize(
        "path",
        [
            "/absolute/path/file.txt",
            "../file.txt",
            "../../file.txt",
            "folder/../file.txt",
            "folder/.../file.txt",
            f"..{os.path.sep}file.txt",
            f"...{os.path.sep}file.txt",
            f"{os.path.sep}..{os.path.sep}file.txt",
            f"{os.path.sep}...{os.path.sep}file.txt",
        ],
    )
    def test_assert_safe_path_invalid(self, path: str) -> None:
        with pytest.raises(UnsafeFilePathException):
            assert_safe_path(path)


class TestReadSigned:
    @pytest.mark.asyncio
    async def test_missing_signature(self) -> None:
        content = "This is not signed"
        with pytest.raises(SignatureMissingException):
            await read_signed(content)

    @pytest.mark.asyncio
    async def test_valid_signed_content(self) -> None:
        # Minimal valid signed message (not actually verifiable)
        content = (
            f"{PGP_SIGNED_MESSAGE_HEADER}\n"
            "Hash: SHA256\n"
            "\n"
            "hello world\n"
            f"{PGP_SIGNATURE_HEADER}\n"
            "fake-signature\n"
            f"{PGP_SIGNATURE_FOOTER}\n"
        )
        body, signed_by_cpc = await read_signed(content, check=False)
        assert "hello world" in body
        assert not signed_by_cpc

    @pytest.mark.asyncio
    async def test_dash_escaped_body(self) -> None:
        content = (
            f"{PGP_SIGNED_MESSAGE_HEADER}\n"
            "Hash: SHA256\n"
            "\n"
            "- -dash-escaped line\n"
            "normal line\n"
            f"{PGP_SIGNATURE_HEADER}\n"
            "fake-signature\n"
            f"{PGP_SIGNATURE_FOOTER}\n"
        )
        body, _ = await read_signed(content, check=False)
        assert "-dash-escaped line" in body
        assert "normal line" in body

    @pytest.mark.asyncio
    async def test_signature_invalid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Patch subprocess to simulate gpgv failure
        class DummyProc:
            returncode = 1

            async def communicate(
                self, input: Any = None
            ) -> tuple[bytes, bytes]:
                return (b"", b"bad signature")

        async def dummy_subprocess_exec(*a: Any, **kw: Any) -> DummyProc:
            return DummyProc()

        monkeypatch.setattr(
            "asyncio.create_subprocess_exec", dummy_subprocess_exec
        )

        content = (
            f"{PGP_SIGNED_MESSAGE_HEADER}\n"
            "Hash: SHA256\n"
            "\n"
            "hello world\n"
            f"{PGP_SIGNATURE_HEADER}\n"
            "fake-signature\n"
            f"{PGP_SIGNATURE_FOOTER}\n"
        )
        with pytest.raises(SignatureInvalidException):
            await read_signed(content, keyring="dummy", check=True)


class TestWalkProducts:
    def test_walk_products_callbacks(self) -> None:
        tree: dict[str, Any] = {
            "products": {
                "prodA": {
                    "versions": {
                        "v1": {
                            "items": {
                                "item1": {"foo": 1},
                                "item2": {"foo": 2},
                            }
                        },
                        "v2": {"items": {"item3": {"foo": 3}}},
                    }
                },
                "prodB": {
                    "versions": {"v3": {"items": {"item4": {"foo": 4}}}}
                },
            }
        }

        seen_products: list[str] = []
        seen_versions: list[tuple[str, str]] = []
        seen_items: list[tuple[str, str, str]] = []

        def cb_product(proddata: dict[str, Any], prodname: str) -> None:
            seen_products.append(prodname)

        def cb_version(
            verdata: dict[str, Any], prodname: str, vername: str
        ) -> None:
            seen_versions.append((prodname, vername))

        def cb_item(
            itemdata: dict[str, Any],
            prodname: str,
            vername: str,
            itemname: str,
        ) -> None:
            seen_items.append((prodname, vername, itemname))

        walk_products(
            tree,
            cb_product=cb_product,
            cb_version=cb_version,
            cb_item=cb_item,
        )

        assert set(seen_products) == {"prodA", "prodB"}
        assert ("prodA", "v1") in seen_versions
        assert ("prodA", "v2") in seen_versions
        assert ("prodB", "v3") in seen_versions
        assert ("prodA", "v1", "item1") in seen_items
        assert ("prodA", "v1", "item2") in seen_items
        assert ("prodA", "v2", "item3") in seen_items
        assert ("prodB", "v3", "item4") in seen_items

    def test_walk_products_ret_finished(self) -> None:
        tree: dict[str, Any] = {
            "products": {
                "prodA": {
                    "versions": {
                        "v1": {
                            "items": {
                                "item1": {"foo": 1},
                            }
                        }
                    }
                }
            }
        }
        called: dict[str, bool] = {
            "product": False,
            "version": False,
            "item": False,
        }

        def cb_product(proddata: dict[str, Any], prodname: str) -> str:
            called["product"] = True
            return "stop"

        walk_products(tree, cb_product=cb_product, ret_finished="stop")
        assert called["product"] is True

        called = {"product": False, "version": False, "item": False}

        def cb_version(
            verdata: dict[str, Any], prodname: str, vername: str
        ) -> str:
            called["version"] = True
            return "stop"

        walk_products(tree, cb_version=cb_version, ret_finished="stop")
        assert called["version"] is True

        called = {"product": False, "version": False, "item": False}

        def cb_item(
            itemdata: dict[str, Any],
            prodname: str,
            vername: str,
            itemname: str,
        ) -> str:
            called["item"] = True
            return "stop"

        walk_products(tree, cb_item=cb_item, ret_finished="stop")
        assert called["item"] is True

    def test_walk_products_no_versions_or_items(self) -> None:
        tree: dict[str, Any] = {
            "products": {
                "prodA": {},
                "prodB": {"versions": {}},
            }
        }
        seen_products: list[str] = []
        walk_products(
            tree,
            cb_product=lambda proddata, prodname: seen_products.append(
                prodname
            ),
        )
        assert set(seen_products) == {"prodA", "prodB"}


class TestCheckTreePaths:
    def test_products_format_valid_paths(self) -> None:
        tree: dict[str, Any] = {
            "products": {
                "prodA": {
                    "versions": {
                        "v1": {
                            "items": {
                                "item1": {"path": "foo/bar.txt"},
                                "item2": {"path": "baz/qux.txt"},
                            }
                        }
                    }
                }
            }
        }
        # Should not raise
        check_tree_paths(tree, format="products:1.0")

    def test_products_format_invalid_path(self) -> None:
        tree: dict[str, Any] = {
            "products": {
                "prodA": {
                    "versions": {
                        "v1": {
                            "items": {
                                "item1": {"path": "../evil.txt"},
                            }
                        }
                    }
                }
            }
        }
        with pytest.raises(UnsafeFilePathException):
            check_tree_paths(tree, format="products:1.0")

    def test_index_format_valid_paths(self) -> None:
        tree: dict[str, Any] = {
            "index": {
                "entry1": {"path": "foo/bar.txt"},
                "entry2": {"path": "baz/qux.txt"},
            }
        }
        # Should not raise
        check_tree_paths(tree, format="index:1.0")

    def test_index_format_invalid_path(self) -> None:
        tree: dict[str, Any] = {
            "index": {
                "entry1": {"path": "/abs/path.txt"},
            }
        }
        with pytest.raises(UnsafeFilePathException):
            check_tree_paths(tree, format="index:1.0")

    def test_unknown_format(self) -> None:
        tree: dict[str, Any] = {"products": {}}
        with pytest.raises(ValueError):
            check_tree_paths(tree, format="unknown:1.0")
