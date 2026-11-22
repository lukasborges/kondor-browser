from pathlib import Path

from kondor.widevine.widevinestore import WidevineStore
from tests.widevine.crxfactory import write_crx


def installed(root: Path, version: str) -> WidevineStore:
    store = WidevineStore(root)
    write_crx(store.download_path())
    assert store.install(version)
    return store


def test_nothing_is_installed_at_first(tmp_path: Path) -> None:
    assert WidevineStore(tmp_path).installed_library() is None


def test_install_publishes_the_library(tmp_path: Path) -> None:
    store = installed(tmp_path, "4.10.1")
    assert store.installed_library() == tmp_path / "4.10.1" / "libwidevinecdm.so"


def test_install_removes_the_download(tmp_path: Path) -> None:
    store = installed(tmp_path, "4.10.1")
    assert not store.download_path().exists()


def test_new_version_replaces_the_old_one(tmp_path: Path) -> None:
    installed(tmp_path, "4.10.1")
    installed(tmp_path, "4.10.2")
    assert sorted(path.name for path in tmp_path.iterdir() if path.is_dir()) == ["4.10.2"]


def test_damaged_download_is_not_installed(tmp_path: Path) -> None:
    store = WidevineStore(tmp_path)
    store.download_path().parent.mkdir(parents=True, exist_ok=True)
    store.download_path().write_bytes(b"broken")
    assert not store.install("4.10.1")
    assert store.installed_library() is None


def test_missing_library_file_means_not_installed(tmp_path: Path) -> None:
    store = installed(tmp_path, "4.10.1")
    (tmp_path / "4.10.1" / "libwidevinecdm.so").unlink()
    assert store.installed_library() is None
