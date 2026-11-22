import io
import struct
import zipfile
from pathlib import Path

from kondor.widevine.crx import LIBRARY_ENTRY

HEADER = b"signed header bytes"
LIBRARY_BYTES = b"\x7fELF fake library"


def zip_bytes(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def crx_bytes(entries: dict[str, bytes], version: int = 3) -> bytes:
    prefix = b"Cr24" + struct.pack("<II", version, len(HEADER))
    return prefix + HEADER + zip_bytes(entries)


def module_entries() -> dict[str, bytes]:
    return {LIBRARY_ENTRY: LIBRARY_BYTES, "manifest.json": b"{}", "LICENSE": b"license"}


def write_crx(path: Path, entries: dict[str, bytes] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(crx_bytes(entries if entries is not None else module_entries()))
    return path
