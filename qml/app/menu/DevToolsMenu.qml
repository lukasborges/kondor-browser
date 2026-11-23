import QtQuick
import QtQuick.Controls
import Kondor

Menu {
    id: root

    required property var browserWindow

    readonly property var actions: root.browserWindow.actions
    readonly property var tab: root.browserWindow.tabModel.currentTab
    readonly property bool isOpen: root.tab ? root.tab.devToolsOpen : false
    readonly property string dockSide: root.isOpen ? root.tab.devTools.dockSide : Settings.devToolsDockSide

    function moveDevTools(side) {
        if (root.actions.hasPage)
            root.tab.devTools.moveTo(side)
        else
            Settings.devToolsDockSide = side
    }

    title: qsTr("Developer Tools")
    icon.name: "code-context"

    MenuKeyNavigation { menu: root }

    MenuItem { action: root.actions.devToolsAction }
    MenuItem { action: root.actions.responsiveModeAction }

    MenuSectionTitle {
        //: Section of the Developer Tools menu: where developer tools are shown
        text: qsTr("Position")
        iconName: "view-split-left-right"
    }

    DockSideMenuItem {
        //: Developer tools docked below the page
        text: qsTr("Bottom")
        side: "bottom"
        currentSide: root.dockSide
        onSideChosen: function(side) { root.moveDevTools(side) }
    }
    DockSideMenuItem {
        //: Developer tools docked on the left of the page
        text: qsTr("Left")
        side: "left"
        currentSide: root.dockSide
        onSideChosen: function(side) { root.moveDevTools(side) }
    }
    DockSideMenuItem {
        //: Developer tools docked on the right of the page
        text: qsTr("Right")
        side: "right"
        currentSide: root.dockSide
        onSideChosen: function(side) { root.moveDevTools(side) }
    }
    DockSideMenuItem {
        //: Developer tools shown in a window of their own
        text: qsTr("Separate Window")
        side: "undocked"
        currentSide: root.dockSide
        onSideChosen: function(side) { root.moveDevTools(side) }
    }
}
