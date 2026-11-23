import pytest
from PySide6.QtCore import QUrl
from PySide6.QtQuick import QQuickWindow
from pytestqt.exceptions import TimeoutError as WaitTimeoutError
from pytestqt.qtbot import QtBot

from kondor.browser.tabs.tab import Tab
from kondor.browser.tabs.tabmodel import TabModel
from kondor.core.settings.settings import Settings
from tests.browser.responsive.conftest import (
    LOAD_TIMEOUT,
    PAGE_URL,
    call_scene,
    console_log,
)

pytestmark = pytest.mark.no_qt_log
READY_MESSAGE = "kondor:devtools-dock-ready"
SCREENCAST_SHOWN = "kondor-test:screencast-shown"
REPORT_SCREENCAST = """(() => {
    const walk = (root) => [...root.querySelectorAll('*')].some((element) =>
        (element.localName === 'devtools-button' && element.textContent === ''
            && (element.getAttribute('aria-label') || '').includes('screencast')
            && element.getBoundingClientRect().width > 0)
        || (element.shadowRoot && walk(element.shadowRoot)));
    if (walk(document)) console.log('kondor-test:screencast-shown');
})()"""


@pytest.fixture(autouse=True)
def bottom_dock_side(qapp: object, isolated_profile: object) -> None:
    Settings.instance().setProperty("devToolsDockSide", "bottom")


def saved_dock_side() -> str:
    return str(Settings.instance().property("devToolsDockSide"))


def wait_until_ready(window: QQuickWindow, qtbot: QtBot) -> None:
    try:
        qtbot.waitUntil(lambda: READY_MESSAGE in console_log(window), timeout=LOAD_TIMEOUT)
    except WaitTimeoutError as error:
        raise AssertionError(f"DevTools console:\n{console_log(window)}") from error


def test_side_chosen_in_dev_tools_moves_them_and_is_saved(
    tab_with_dev_tools: Tab, window: QQuickWindow
) -> None:
    call_scene(window, "sendConsoleMessage", "kondor:devtools-dock:right")

    assert tab_with_dev_tools.devTools.dockSide == "right"
    assert saved_dock_side() == "right"


def test_side_chosen_in_the_menu_opens_dev_tools_there(
    model: TabModel, window: QQuickWindow, qtbot: QtBot
) -> None:
    tab: Tab = model.addTab()
    tab.navigateTo(QUrl(PAGE_URL))
    qtbot.waitUntil(lambda: tab.title == "page", timeout=LOAD_TIMEOUT)

    tab.devTools.moveTo("left")

    qtbot.waitUntil(lambda: tab.devToolsOpen, timeout=LOAD_TIMEOUT)
    assert tab.devTools.dockSide == "left"
    assert saved_dock_side() == "left"


def test_dev_tools_open_on_the_saved_side(
    model: TabModel, window: QQuickWindow, qtbot: QtBot
) -> None:
    Settings.instance().setProperty("devToolsDockSide", "undocked")
    tab: Tab = model.addTab()
    tab.navigateTo(QUrl(PAGE_URL))
    qtbot.waitUntil(lambda: tab.title == "page", timeout=LOAD_TIMEOUT)

    tab.toggleDevTools()

    qtbot.waitUntil(lambda: tab.devToolsOpen, timeout=LOAD_TIMEOUT)
    assert tab.devTools.dockSide == "undocked"


def test_dock_side_row_reports_the_chosen_side(
    tab_with_dev_tools: Tab, window: QQuickWindow, qtbot: QtBot
) -> None:
    wait_until_ready(window, qtbot)

    call_scene(window, "probe", "kondorShowDockSide('left')")

    qtbot.waitUntil(lambda: tab_with_dev_tools.devTools.dockSide == "left", timeout=LOAD_TIMEOUT)


def test_screencast_toggle_is_hidden(
    tab_with_dev_tools: Tab, window: QQuickWindow, qtbot: QtBot
) -> None:
    wait_until_ready(window, qtbot)

    call_scene(window, "probe", REPORT_SCREENCAST)
    qtbot.wait(1000)

    assert SCREENCAST_SHOWN not in console_log(window)
