from collections.abc import Iterator

import pytest
from PySide6.QtCore import Q_ARG, QMetaObject, QObject
from PySide6.QtQml import QQmlComponent, QQmlEngine

from kondor.core.settings.settings import Settings
from tests.qmlsupport import error_text, load_component

LAYOUT_QML = "import QtQuick\nimport Kondor\nWindowLayout {}\n"
KEPT_COMPONENTS: list[QQmlComponent] = []
OPTIONS = ("hideToolbars", "showBookmarksBar", "sideBarCollapsed")


@pytest.fixture(autouse=True)
def restored_settings(kondor_types: None) -> Iterator[None]:
    settings = Settings.instance()
    previous = {name: settings.property(name) for name in OPTIONS}
    yield
    for name, value in previous.items():
        settings.setProperty(name, value)


def new_layout(engine: QQmlEngine) -> QObject:
    component = load_component(engine, LAYOUT_QML)
    KEPT_COMPONENTS.append(component)
    layout = component.create()
    assert layout is not None, error_text(component)
    return layout


def call(layout: QObject, function: str, *arguments: object) -> None:
    holders = [Q_ARG("QVariant", argument) for argument in arguments]
    QMetaObject.invokeMethod(layout, function, *holders)


def test_hiding_toolbars_leaves_other_windows_alone(kondor_engine: QQmlEngine) -> None:
    Settings.instance().setProperty("hideToolbars", False)
    first, second = new_layout(kondor_engine), new_layout(kondor_engine)
    call(first, "setToolbarsHidden", True)
    assert first.property("areToolbarsHidden") is True
    assert second.property("areToolbarsHidden") is False


def test_new_window_starts_with_the_last_choice(kondor_engine: QQmlEngine) -> None:
    first = new_layout(kondor_engine)
    call(first, "setBookmarksBarShown", False)
    call(first, "toggleSideBar")
    second = new_layout(kondor_engine)
    assert second.property("isBookmarksBarShown") is False
    assert second.property("isSideBarCollapsed") == first.property("isSideBarCollapsed")
