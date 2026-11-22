import QtQuick
import QtQuick.Controls
import Kondor

Item {
    id: root

    required property Tab tab

    default property alias page: pageSlot.data
    readonly property alias view: devToolsView

    readonly property string dockSide: root.tab.devTools.dockSide
    readonly property bool isUndocked: dockSide === "undocked"
    readonly property bool isSideways: dockSide === "left" || dockSide === "right"
    readonly property bool isDockOpen: root.tab.devToolsOpen && !isUndocked

    signal openRequested()
    signal closeRequested()

    function moveTo(side) {
        Settings.devToolsDockSide = side
        root.tab.devTools.setDockSide(side)
        devToolsView.showDockSide(root.dockSide)
        if (!root.tab.devToolsOpen)
            root.openRequested()
    }

    function placeDockSlot() {
        const wantedIndex = root.dockSide === "left" ? 0 : 1
        if (split.itemAt(wantedIndex) !== dockSlot)
            split.moveItem(1 - wantedIndex, wantedIndex)
    }

    function recallDockSide() {
        if (root.tab.devToolsOpen)
            root.tab.devTools.setDockSide(Settings.devToolsDockSide)
    }

    SplitView {
        id: split
        anchors.fill: parent
        orientation: root.isSideways ? Qt.Horizontal : Qt.Vertical

        Item {
            id: pageSlot
            SplitView.fillWidth: true
            SplitView.fillHeight: true
        }

        Item {
            id: dockSlot
            visible: root.isDockOpen
            SplitView.preferredWidth: root.width * 0.4
            SplitView.preferredHeight: root.height * 0.4
            SplitView.minimumWidth: 100
            SplitView.minimumHeight: 100
        }
    }

    DevToolsWindow {
        id: devToolsWindow
        tab: root.tab
        visible: root.tab.devToolsOpen && root.isUndocked
        onCloseRequested: root.closeRequested()
    }

    DevToolsView {
        id: devToolsView
        tab: root.tab
        parent: root.isUndocked ? devToolsWindow.contentItem : dockSlot
        anchors.fill: parent
        visible: root.tab.devToolsOpen
        onCloseRequested: root.closeRequested()
        onDockSideChosen: function(side) { root.moveTo(side) }
    }

    Connections {
        target: root.tab.devTools
        function onMoveRequested(side) { root.moveTo(side) }
    }

    Connections {
        target: root.tab
        function onDevToolsOpenChanged() { root.recallDockSide() }
    }

    onDockSideChanged: placeDockSlot()
}
