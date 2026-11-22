from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QMetaObject, QObject, Qt, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine

from kondor.browser.profile.profilemanager import ProfileManager
from kondor.browser.tabs.tab import Tab
from tests.qmlsupport import error_text, load_component

BAR_QML = "import QtQuick\nimport Kondor\nWidevineBar {}\n"
TEXT_FINDER_QML = """import QtQuick
QtObject {
    function texts(root) {
        const own = root.visible !== false && root.text !== undefined ? [root.text] : []
        return own.concat(root.children.map(texts)).join(" ")
    }
}
"""
KEPT: list[QQmlComponent] = []


def created(engine: QQmlEngine, source: str, properties: dict[str, object]) -> QObject:
    component = load_component(engine, source)
    item = component.createWithInitialProperties(properties)
    assert item is not None, error_text(component)
    QQmlEngine.setObjectOwnership(item, QQmlEngine.ObjectOwnership.CppOwnership)
    KEPT.append(component)
    return item


def shown_texts(engine: QQmlEngine, root: QObject) -> str:
    finder = created(engine, TEXT_FINDER_QML, {})
    result = Q_RETURN_ARG("QVariant")
    connection = Qt.ConnectionType.DirectConnection
    return str(
        QMetaObject.invokeMethod(finder, "texts", connection, result, Q_ARG("QVariant", root))
    )


def tab_on_netflix() -> Tab:
    tab = Tab(ProfileManager.instance().defaultProfile())
    tab.setUrl(QUrl("https://www.netflix.com/watch/1"))
    return tab


def test_bar_is_hidden_until_a_page_asks(kondor_engine: QQmlEngine) -> None:
    bar = created(kondor_engine, BAR_QML, {"tab": tab_on_netflix()})
    assert bar.property("visible") is False


def test_bar_offers_the_download_with_the_host(kondor_engine: QQmlEngine) -> None:
    tab = tab_on_netflix()
    tab.widevine.mark_requested()
    bar = created(kondor_engine, BAR_QML, {"tab": tab})
    text = shown_texts(kondor_engine, bar)
    assert bar.property("visible") is True
    assert "www.netflix.com" in text
    assert "Download Widevine" in text
    assert "Restart Now" not in text


def test_closing_the_bar_hides_it(kondor_engine: QQmlEngine) -> None:
    tab = tab_on_netflix()
    tab.widevine.mark_requested()
    bar = created(kondor_engine, BAR_QML, {"tab": tab})
    tab.widevine.dismiss()
    assert bar.property("visible") is False
