from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QNetworkAccessManager

from kondor.core.download.filedownloader import FileDownloader, FileTask
from kondor.widevine.release import WidevineRelease
from kondor.widevine.widevinestore import WidevineStore


class WidevineDownload(QObject):
    progressed = Signal(int)
    finished = Signal(bool)

    def __init__(
        self, manager: QNetworkAccessManager, store: WidevineStore, parent: QObject
    ) -> None:
        super().__init__(parent)
        self._store = store
        self._downloader = FileDownloader(manager, self)
        self._downloader.progressed.connect(self.progressed)
        self._downloader.finished.connect(self._on_file_finished)
        self._remaining: list[str] = []
        self._release: WidevineRelease | None = None

    def start(self, release: WidevineRelease) -> None:
        self._release = release
        self._remaining = list(release.urls)
        self._try_next_url()

    def cancel(self) -> None:
        self._remaining = []
        self._downloader.cancel()

    def _try_next_url(self) -> None:
        release = self._release
        if release is None or not self._remaining:
            self.finished.emit(False)
            return
        url = self._remaining.pop(0)
        path = self._store.download_path()
        self._downloader.start(FileTask(url, path, release.hash, release.size, release.algorithm))

    def _on_file_finished(self, ok: bool) -> None:
        if ok:
            self.finished.emit(True)
        else:
            self._try_next_url()
