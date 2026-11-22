import shutil
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from kondor.widevine.crx import LIBRARY_NAME, extract_module

CURRENT_FILE = "current"
DOWNLOAD_FILE = "widevine.crx3.partial"
STAGING_SUFFIX = ".staging"


def default_root() -> Path:
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    return Path(base) / "widevine"


class WidevineStore:
    def __init__(self, root: Path | None = None) -> None:
        self._root = root if root is not None else default_root()

    def download_path(self) -> Path:
        return self._root / DOWNLOAD_FILE

    def installed_library(self) -> Path | None:
        current = self._root / CURRENT_FILE
        version = current.read_text().strip() if current.is_file() else ""
        library = self._root / version / LIBRARY_NAME
        return library if version and library.is_file() else None

    def install(self, version: str) -> bool:
        staging = self._root / (version + STAGING_SUFFIX)
        shutil.rmtree(staging, ignore_errors=True)
        if not extract_module(self.download_path(), staging):
            return False
        self._publish(version, staging)
        return True

    def discard_download(self) -> None:
        self.download_path().unlink(missing_ok=True)

    def _publish(self, version: str, staging: Path) -> None:
        shutil.rmtree(self._root / version, ignore_errors=True)
        staging.rename(self._root / version)
        (self._root / CURRENT_FILE).write_text(version)
        self.discard_download()
        self._remove_all_but(version)

    def _remove_all_but(self, version: str) -> None:
        for path in self._root.iterdir():
            if path.is_dir() and path.name != version:
                shutil.rmtree(path, ignore_errors=True)
