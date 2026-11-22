from pathlib import Path
from typing import ClassVar

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply

from kondor.core.download.jsonfetch import fetch_json
from kondor.widevine.release import MANIFEST_URL, parse_release
from kondor.widevine.widevinedownload import WidevineDownload
from kondor.widevine.widevineflag import loaded_library
from kondor.widevine.widevinestore import WidevineStore

STATE_MISSING = "missing"
STATE_DOWNLOADING = "downloading"
STATE_FAILED = "failed"
STATE_READY = "ready"
STATE_LOADED = "loaded"
BYTES_PER_MEGABYTE = 1_000_000


def initial_state(store: WidevineStore) -> str:
    if loaded_library() and Path(loaded_library()).is_file():
        return STATE_LOADED
    return STATE_READY if store.installed_library() is not None else STATE_MISSING


class Widevine(QObject):
    _instance: ClassVar["Widevine | None"] = None
    stateChanged = Signal()
    progressChanged = Signal()

    def __init__(self, store: WidevineStore | None = None) -> None:
        super().__init__()
        self._store = store or WidevineStore()
        self._manager = QNetworkAccessManager(self)
        self._download = WidevineDownload(self._manager, self._store, self)
        self._download.progressed.connect(self._set_received)
        self._download.finished.connect(self._on_downloaded)
        self._state = initial_state(self._store)
        self._received = self._total = 0
        self._version = ""
        self._manifest_reply: QNetworkReply | None = None

    @classmethod
    def instance(cls) -> "Widevine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    state = Property(str, lambda self: self._state, notify=stateChanged)
    downloadedMegabytes = Property(
        int, lambda self: self._received // BYTES_PER_MEGABYTE, notify=progressChanged
    )
    totalMegabytes = Property(
        int, lambda self: self._total // BYTES_PER_MEGABYTE, notify=progressChanged
    )

    @Slot()
    def download(self) -> None:
        if self._state not in (STATE_MISSING, STATE_FAILED):
            return
        self._set_received(0)
        self._set_state(STATE_DOWNLOADING)
        self._manifest_reply = fetch_json(self._manager, MANIFEST_URL, self._on_manifest)

    @Slot()
    def cancel(self) -> None:
        if self._state != STATE_DOWNLOADING:
            return
        self._set_state(STATE_MISSING)
        self._stop_manifest()
        self._download.cancel()
        self._store.discard_download()

    def _stop_manifest(self) -> None:
        if self._manifest_reply is not None:
            self._manifest_reply.abort()

    def _on_manifest(self, document: object | None) -> None:
        self._manifest_reply = None
        release = parse_release(document)
        if self._state != STATE_DOWNLOADING:
            return
        if release is None:
            self._set_state(STATE_FAILED)
            return
        self._version, self._total = release.version, release.size
        self._download.start(release)

    def _on_downloaded(self, ok: bool) -> None:
        if self._state != STATE_DOWNLOADING:
            return
        installed = ok and self._store.install(self._version)
        if not installed:
            self._store.discard_download()
        self._set_state(STATE_READY if installed else STATE_FAILED)

    def _set_received(self, received: int) -> None:
        self._received = received
        self.progressChanged.emit()

    def _set_state(self, state: str) -> None:
        if state != self._state:
            self._state = state
            self.stateChanged.emit()
