from collections.abc import Iterator

import pytest
from PySide6.QtQml import QQmlEngine
from PySide6.QtQuick import QQuickItem, QQuickWindow
from pytestqt.qtbot import QtBot

from kondor.browser.tabs.tab import Tab
from kondor.browser.tabs.tabmodel import TabModel
from tests.extensions.pageserver import PageServer
from tests.qmlsupport import error_text, load_component, release

pytestmark = pytest.mark.usefixtures("window")
LOAD_TIMEOUT = 30000
SETTLE_MS = 1500
REQUEST = (
    "navigator.requestMediaKeySystemAccess('KEY', [{initDataTypes: ['cenc'],"
    " videoCapabilities: [{contentType: 'video/mp4; codecs=\"avc1.42E01E\"'}]}])"
    ".then(() => document.title = 'granted', () => document.title = 'refused')"
)
SCENE_QML = """
import QtQuick
import Kondor

Item {
    width: 300
    height: 300
    TabViews {
        width: 300
        height: 300
        tabModel: testTabModel
        browserActions: ({})
    }
}
"""


def page_asking_for(key_system: str) -> bytes:
    script = REQUEST.replace("KEY", key_system)
    page = f"<html><head><title>page</title></head><body><script>{script}</script></body></html>"
    return page.encode()


@pytest.fixture
def model(qapp: object, isolated_profile: object) -> Iterator[TabModel]:
    tab_model = TabModel()
    yield tab_model
    tab_model.deleteLater()


@pytest.fixture
def window(model: TabModel, kondor_engine: QQmlEngine) -> Iterator[QQuickWindow]:
    kondor_engine.rootContext().setContextProperty("testTabModel", model)
    component = load_component(kondor_engine, SCENE_QML)
    item = component.create()
    assert item is not None, error_text(component)
    assert isinstance(item, QQuickItem)
    quick_window = QQuickWindow()
    quick_window.resize(300, 300)
    item.setParentItem(quick_window.contentItem())
    quick_window.show()
    yield quick_window
    quick_window.close()
    item.deleteLater()


@pytest.fixture
def server() -> Iterator[PageServer]:
    pages = {
        "/widevine": page_asking_for("com.widevine.alpha"),
        "/clearkey": page_asking_for("org.w3.clearkey"),
    }
    page_server = PageServer(pages)
    yield page_server
    release(page_server)


def open_page(model: TabModel, server: PageServer, path: str) -> Tab:
    tab: Tab = model.addTab()
    tab.navigateTo(server.url(path))
    return tab


def test_page_asking_for_widevine_shows_the_offer(
    model: TabModel, server: PageServer, qtbot: QtBot
) -> None:
    tab = open_page(model, server, "/widevine")
    qtbot.waitUntil(lambda: tab.widevine.isRequested, timeout=LOAD_TIMEOUT)
    qtbot.waitUntil(lambda: tab.title == "refused", timeout=LOAD_TIMEOUT)


def test_other_key_systems_do_not_show_the_offer(
    model: TabModel, server: PageServer, qtbot: QtBot
) -> None:
    tab = open_page(model, server, "/clearkey")
    qtbot.waitUntil(lambda: tab.title in ("granted", "refused"), timeout=LOAD_TIMEOUT)
    qtbot.wait(SETTLE_MS)
    assert not tab.widevine.isRequested
