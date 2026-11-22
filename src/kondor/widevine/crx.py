import io
import struct
import zipfile
from pathlib import Path

CRX_MAGIC = b"Cr24"
CRX_VERSION = 3
PREFIX_BYTES = 12
LIBRARY_ENTRY = "_platform_specific/linux_x64/libwidevinecdm.so"
LIBRARY_NAME = "libwidevinecdm.so"
MODULE_ENTRIES = {
    LIBRARY_ENTRY: LIBRARY_NAME,
    "manifest.json": "manifest.json",
    "LICENSE": "LICENSE",
}


def zip_payload(data: bytes) -> bytes | None:
    if len(data) < PREFIX_BYTES or data[:4] != CRX_MAGIC:
        return None
    version, header_length = struct.unpack("<II", data[4:PREFIX_BYTES])
    if version != CRX_VERSION:
        return None
    return data[PREFIX_BYTES + header_length :]


def open_archive(crx: Path) -> zipfile.ZipFile | None:
    payload = zip_payload(crx.read_bytes())
    try:
        return zipfile.ZipFile(io.BytesIO(payload)) if payload is not None else None
    except zipfile.BadZipFile:
        return None


def extract_module(crx: Path, destination: Path) -> bool:
    archive = open_archive(crx)
    if archive is None or LIBRARY_ENTRY not in archive.namelist():
        return False
    destination.mkdir(parents=True, exist_ok=True)
    for entry, name in MODULE_ENTRIES.items():
        if entry in archive.namelist():
            (destination / name).write_bytes(archive.read(entry))
    return True
