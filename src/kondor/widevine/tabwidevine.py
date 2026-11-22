from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot


class TabWidevine(QObject):
    requestedChanged = Signal()
    hostChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._is_requested = False
        self._is_dismissed = False
        self._host = ""

    isRequested = Property(bool, lambda self: self._is_requested, notify=requestedChanged)
    host = Property(str, lambda self: self._host, notify=hostChanged)

    def update_for(self, url: QUrl) -> None:
        host = url.host()
        if host != self._host:
            self._host = host
            self.hostChanged.emit()

    def mark_requested(self) -> None:
        self._set_requested(not self._is_dismissed)

    def reset(self) -> None:
        self._is_dismissed = False
        self._set_requested(False)

    @Slot()
    def dismiss(self) -> None:
        self._is_dismissed = True
        self._set_requested(False)

    def _set_requested(self, is_requested: bool) -> None:
        if is_requested != self._is_requested:
            self._is_requested = is_requested
            self.requestedChanged.emit()
