from pathlib import Path

import pytest

from kondor.widevine.widevineflag import (
    CHROMIUM_FLAGS_VARIABLE,
    load_installed_widevine,
    loaded_library,
    with_widevine_path,
)
from kondor.widevine.widevinestore import WidevineStore
from tests.widevine.crxfactory import write_crx


def test_flag_is_added_after_the_existing_ones() -> None:
    flags = with_widevine_path(["--disable-features=X"], "/w/lib.so")
    assert flags == ["--disable-features=X", "--widevine-path=/w/lib.so"]


def test_flag_replaces_an_older_path() -> None:
    assert with_widevine_path(["--widevine-path=/old.so"], "/new.so") == ["--widevine-path=/new.so"]


def test_installed_module_is_loaded_at_startup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(CHROMIUM_FLAGS_VARIABLE, "--disable-features=X")
    store = WidevineStore(tmp_path)
    write_crx(store.download_path())
    store.install("4.10.1")
    load_installed_widevine(store)
    assert loaded_library() == str(tmp_path / "4.10.1" / "libwidevinecdm.so")


def test_no_module_adds_no_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(CHROMIUM_FLAGS_VARIABLE, "--disable-features=X")
    load_installed_widevine(WidevineStore(tmp_path))
    assert loaded_library() == ""
