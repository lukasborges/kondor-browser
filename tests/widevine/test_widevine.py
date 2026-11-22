import hashlib
import json
from pathlib import Path

import pytest
from PySide6.QtCore import QUrl
from pytestqt.qtbot import QtBot

from kondor.widevine import widevine as widevine_module
from kondor.widevine.release import PLATFORM, VENDOR
from kondor.widevine.widevine import Widevine
from kondor.widevine.widevinestore import WidevineStore
from tests.widevine.crxfactory import write_crx

TIMEOUT = 10000


def file_url(path: Path) -> str:
    return QUrl.fromLocalFile(str(path)).toString()


def write_manifest(folder: Path, urls: list[str], digest: str) -> Path:
    entry = {"fileUrl": urls[0], "mirrorUrls": urls[1:], "filesize": 2_000_000, "hashValue": digest}
    vendor = {"version": "4.10.1", "platforms": {PLATFORM: entry}}
    path = folder / "widevinecdm.json"
    path.write_text(json.dumps({"hashFunction": "sha512", "vendors": {VENDOR: vendor}}))
    return path


def served(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, urls: list[str] | None = None) -> str:
    crx = write_crx(tmp_path / "server" / "widevine.crx3")
    digest = hashlib.sha512(crx.read_bytes()).hexdigest()
    manifest = write_manifest(crx.parent, urls or [file_url(crx)], digest)
    monkeypatch.setattr(widevine_module, "MANIFEST_URL", file_url(manifest))
    return file_url(crx)


def finished(widevine: Widevine, qtbot: QtBot) -> str:
    qtbot.waitUntil(lambda: widevine.state != "downloading", timeout=TIMEOUT)
    return str(widevine.state)


def test_starts_missing_without_a_module(tmp_path: Path, qapp: object) -> None:
    assert Widevine(WidevineStore(tmp_path / "data")).state == "missing"


def test_download_installs_the_module(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, qtbot: QtBot
) -> None:
    served(tmp_path, monkeypatch)
    store = WidevineStore(tmp_path / "data")
    widevine = Widevine(store)
    widevine.download()
    assert finished(widevine, qtbot) == "ready"
    assert store.installed_library() is not None


def test_wrong_hash_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, qtbot: QtBot) -> None:
    crx = served(tmp_path, monkeypatch)
    write_manifest(tmp_path / "server", [crx], "0" * 128)
    widevine = Widevine(WidevineStore(tmp_path / "data"))
    widevine.download()
    assert finished(widevine, qtbot) == "failed"


def test_mirror_is_tried_when_the_first_address_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, qtbot: QtBot
) -> None:
    crx = served(tmp_path, monkeypatch)
    served(tmp_path, monkeypatch, [file_url(tmp_path / "missing.crx3"), crx])
    widevine = Widevine(WidevineStore(tmp_path / "data"))
    widevine.download()
    assert finished(widevine, qtbot) == "ready"


def test_missing_manifest_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, qtbot: QtBot
) -> None:
    monkeypatch.setattr(widevine_module, "MANIFEST_URL", file_url(tmp_path / "none.json"))
    widevine = Widevine(WidevineStore(tmp_path / "data"))
    widevine.download()
    assert finished(widevine, qtbot) == "failed"


def test_cancel_removes_the_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, qapp: object
) -> None:
    served(tmp_path, monkeypatch)
    store = WidevineStore(tmp_path / "data")
    widevine = Widevine(store)
    widevine.download()
    widevine.cancel()
    assert widevine.state == "missing"
    assert not store.download_path().exists()
