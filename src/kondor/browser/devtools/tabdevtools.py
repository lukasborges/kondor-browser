from PySide6.QtCore import Property, QObject, Signal, Slot

from kondor.browser.tabs.assignandnotify import assign_and_notify

BOTTOM = "bottom"
DOCK_SIDES = (BOTTOM, "left", "right", "undocked")


def known_dock_side(side: str) -> str:
    return side if side in DOCK_SIDES else BOTTOM


class TabDevTools(QObject):
    dockSideChanged = Signal()
    moveRequested = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._dock_side = BOTTOM

    dockSide = Property(str, lambda self: self._dock_side, notify=dockSideChanged)

    @Slot(str)
    def setDockSide(self, side: str) -> None:
        assign_and_notify((self, "_dock_side"), known_dock_side(side), self.dockSideChanged)

    @Slot(str)
    def moveTo(self, side: str) -> None:
        self.moveRequested.emit(known_dock_side(side))
