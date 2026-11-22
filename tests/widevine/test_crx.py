from pathlib import Path

from kondor.widevine.crx import extract_module, zip_payload
from tests.widevine.crxfactory import LIBRARY_BYTES, crx_bytes, module_entries, write_crx


def test_payload_skips_the_signed_header() -> None:
    payload = zip_payload(crx_bytes(module_entries()))
    assert payload is not None and payload.startswith(b"PK")


def test_other_crx_versions_are_refused() -> None:
    assert zip_payload(crx_bytes(module_entries(), version=2)) is None


def test_plain_zip_is_refused() -> None:
    assert zip_payload(b"PK\x03\x04 not a crx") is None


def test_extracts_only_the_module_files(tmp_path: Path) -> None:
    entries = {**module_entries(), "_metadata/verified_contents.json": b"[]"}
    destination = tmp_path / "module"
    assert extract_module(write_crx(tmp_path / "w.crx3", entries), destination)
    assert sorted(path.name for path in destination.iterdir()) == [
        "LICENSE",
        "libwidevinecdm.so",
        "manifest.json",
    ]
    assert (destination / "libwidevinecdm.so").read_bytes() == LIBRARY_BYTES


def test_archive_without_the_library_is_refused(tmp_path: Path) -> None:
    crx = write_crx(tmp_path / "w.crx3", {"manifest.json": b"{}"})
    assert not extract_module(crx, tmp_path / "module")
