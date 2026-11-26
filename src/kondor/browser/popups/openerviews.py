import shiboken6
from PySide6.QtCore import QObject, Slot

from kondor.browser.favicons.faviconstore import FaviconStore

DISCARDED = 2


def address(item: QObject) -> int:
    return int(shiboken6.getCppPointer(item)[0])


def discard(view: QObject) -> None:
    view.setProperty("visible", False)
    view.setProperty("parent", None)
    view.setProperty("lifecycleState", DISCARDED)


# A page that another page opened keeps a pointer to the opener's view, and Qt WebEngine crashes
# on the next mouse event once that view is gone, so the view outlives its tab:
# https://github.com/lukasborges/kondor-browser/issues/460
class OpenerViews(QObject):
    _instance: "OpenerViews | None" = None

    def __init__(self) -> None:
        super().__init__()
        self._pending: dict[int, QObject] = {}
        self._openers: dict[int, int] = {}
        self._retired: dict[int, QObject] = {}

    @classmethod
    def instance(cls) -> "OpenerViews":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @Slot(QObject, QObject)
    def noteOpener(self, request: QObject, openerView: QObject) -> None:  # noqa: N802, N803
        key = address(request)
        self._pending[key] = openerView
        request.destroyed.connect(lambda: self._pending.pop(key, None))

    @Slot(QObject, QObject)
    def noteAdopter(self, request: QObject, adopterView: QObject) -> None:  # noqa: N802, N803
        opener = self._pending.pop(address(request), None)
        if opener is None or not shiboken6.isValid(opener):
            return
        key = address(adopterView)
        self._openers[key] = address(opener)
        adopterView.destroyed.connect(lambda: self.forget_adopter(key))

    def opens_live_pages(self, view: QObject) -> bool:
        return address(view) in self._openers.values()

    @Slot(QObject)
    def retire(self, view: QObject | None) -> None:
        if view is None or not self.opens_live_pages(view):
            return
        self._retired[address(view)] = view
        view.setParent(self)
        FaviconStore.instance().markDiscarded(view, view.property("icon"))
        discard(view)

    def forget_adopter(self, adopter_key: int) -> None:
        opener_key = self._openers.pop(adopter_key, None)
        if opener_key is None or opener_key in self._openers.values():
            return
        retired = self._retired.pop(opener_key, None)
        if retired is not None and shiboken6.isValid(retired):
            retired.deleteLater()

    def release_all(self) -> None:
        self._retired.clear()
        for view in self.children():
            if shiboken6.isValid(view):
                shiboken6.delete(view)
