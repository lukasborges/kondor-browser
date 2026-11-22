from typing import Protocol

from PySide6.QtCore import QObject, Slot


class MissingReportOwner(Protocol):
    def receive_missing(self) -> None: ...


class WidevinePageApi(QObject):
    def __init__(self, bridge: QObject, owner: MissingReportOwner) -> None:
        super().__init__(bridge)
        self._owner = owner

    @Slot()
    def reportMissing(self) -> None:
        self._owner.receive_missing()
