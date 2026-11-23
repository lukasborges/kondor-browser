// Developer tools position: DevTools docked on the right, with DevTools' own ⋮ menu open.
// Its "Dock side" row (undock, left, bottom, right) moves DevTools in Kondor, like in Chrome.
// The last choice is remembered for the next DevTools that opens.
import QtQuick
import QtQuick.Controls
import "common"

BrowserFrame {
    SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal
        Item {
            SplitView.fillWidth: true
            clip: true
            FakePage {}
        }
        DevToolsMock {
            SplitView.preferredWidth: 480
            dockSide: "right"
            menuOpen: true
        }
    }
}
