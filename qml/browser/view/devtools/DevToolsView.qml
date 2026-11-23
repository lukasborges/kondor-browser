import QtQuick
import QtWebEngine
import Kondor

WebEngineView {
    id: root

    required property Tab tab

    readonly property string dockSidePrefix: "kondor:devtools-dock:"

    signal closeRequested()
    signal dockSideChosen(string side)

    function showDockSide(side) {
        runJavaScript("globalThis.kondorShowDockSide?.(" + JSON.stringify(side) + ")")
    }

    function routeConsoleMessage(message) {
        if (message === "kondor:toggle-responsive-mode")
            root.tab.responsive.toggle()
        else if (message === "kondor:devtools-dock-ready")
            root.showDockSide(root.tab.devTools.dockSide)
        else if (message.startsWith(root.dockSidePrefix))
            root.dockSideChosen(message.slice(root.dockSidePrefix.length))
    }

    objectName: "devTools"
    profile: root.tab.profile
    onWindowCloseRequested: root.closeRequested()
    onJavaScriptConsoleMessage: function(level, message) { root.routeConsoleMessage(message) }
}
