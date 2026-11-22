// Developer tools position from Kondor's menu: a "Developer Tools" submenu of its own, after
// More Tools (maintainer's request), with Show Developer Tools, Responsive Design Mode and a
// "Position" section: an exclusive choice of Bottom, Left, Right or Separate Window. Here DevTools
// is docked on the left. Choosing a position moves the open DevTools (or opens it there) and is
// remembered. More Tools keeps Save as PDF…, Take Screenshot… and Site Permissions….
import QtQuick
import QtQuick.Controls
import "common"

BrowserFrame {
    height: 720
    SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal
        DevToolsMock {
            SplitView.preferredWidth: 420
            dockSide: "left"
        }
        Item {
            SplitView.fillWidth: true
            clip: true
            FakePage {}
        }
    }
    MainMenuMock {
        openSubmenu: "devtools"
        devToolsPosition: "left"
    }
}
