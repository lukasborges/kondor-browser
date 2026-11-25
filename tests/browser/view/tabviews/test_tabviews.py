import time
from collections.abc import Iterator

import pytest
from PySide6.QtCore import Q_RETURN_ARG, QCoreApplication, QMetaObject, Qt, QUrl
from PySide6.QtQml import QQmlEngine
from PySide6.QtQuick import QQuickItem, QQuickWindow
from pytestqt.qtbot import QtBot

from kondor.browser.tabs.tab import Tab
from kondor.browser.tabs.tabmodel import TabModel
from tests.qmlsupport import error_text, load_component

LOAD_TIMEOUT = 30000
LONGER_THAN_PENDING_SCRIPT_SECONDS = 1
PAGE_URL = "data:text/html,<title>%s</title>hello"
SCENE_QML = """
import QtQuick
import Kondor

TabViews {
    id: scene
    width: 300
    height: 300
    tabModel: testTabModel
    browserActions: ({})
    function pageViews(item) {
        const own = item.objectName === "pageView" ? [item] : []
        return own.concat(...item.children.map(pageViews))
    }
    function runPendingScript() {
        pageViews(scene)[0].runJavaScript("new Promise(done => setTimeout(done, 300))",
                                          function() {})
    }
    function visibleTitles() {
        return pageViews(scene).filter(view => view.visible).map(view => view.title).join()
    }
}
"""


@pytest.fixture
def model(qapp: object, isolated_profile: object) -> Iterator[TabModel]:
    tab_model = TabModel()
    yield tab_model
    tab_model.deleteLater()


@pytest.fixture
def scene(model: TabModel, kondor_engine: QQmlEngine) -> Iterator[QQuickItem]:
    kondor_engine.rootContext().setContextProperty("testTabModel", model)
    component = load_component(kondor_engine, SCENE_QML)
    item = component.create()
    assert isinstance(item, QQuickItem), error_text(component)
    window = QQuickWindow()
    item.setParentItem(window.contentItem())
    window.show()
    yield item
    window.close()
    item.deleteLater()


def open_page(model: TabModel, qtbot: QtBot, title: str = "page") -> Tab:
    tab: Tab = model.addTab()
    tab.navigateTo(QUrl(PAGE_URL % title))
    qtbot.waitUntil(lambda: tab.title == title and not tab.loading, timeout=LOAD_TIMEOUT)
    return tab


def process_events_before_deferred_deletions(seconds: float) -> None:
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        QCoreApplication.processEvents()


def visible_titles(scene: QQuickItem) -> str:
    return str(
        QMetaObject.invokeMethod(
            scene, "visibleTitles", Qt.ConnectionType.DirectConnection, Q_RETURN_ARG("QVariant")
        )
    )


def test_closing_a_tab_with_a_pending_script_result_keeps_running(
    model: TabModel, scene: QQuickItem, qtbot: QtBot
) -> None:
    tab = open_page(model, qtbot)
    QMetaObject.invokeMethod(scene, "runPendingScript", Qt.ConnectionType.DirectConnection)

    model.closeTabObject(tab)
    process_events_before_deferred_deletions(LONGER_THAN_PENDING_SCRIPT_SECONDS)

    assert model.rowCount() == 0


def test_only_the_current_tab_view_is_visible(
    model: TabModel, scene: QQuickItem, qtbot: QtBot
) -> None:
    open_page(model, qtbot, "first")
    open_page(model, qtbot, "second")

    model.setCurrentIndex(0)

    assert visible_titles(scene) == "first"
