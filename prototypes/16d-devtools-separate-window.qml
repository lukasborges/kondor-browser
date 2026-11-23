// Developer tools position: "Separate Window". The page gets the whole tab, and DevTools
// opens in its own window, titled "<page title> — Developer Tools" (KDE: document first). Closing that window closes DevTools.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import "common"

Item {
    width: 1100
    height: 760

    Rectangle { anchors.fill: parent; color: Kirigami.ColorUtils.linearInterpolation(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, 0.15) }

    BrowserFrame {
        width: 1000
        height: 640
        FakePage {}
    }

    Rectangle {
        x: 380; y: 330
        width: 700; height: 420
        color: Kirigami.Theme.backgroundColor
        border.color: Kirigami.ColorUtils.linearInterpolation(Kirigami.Theme.backgroundColor, Kirigami.Theme.textColor, 0.3)
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 1
            spacing: 0
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 32
                Kirigami.Theme.colorSet: Kirigami.Theme.Header
                Kirigami.Theme.inherit: false
                color: Kirigami.Theme.backgroundColor
                Kirigami.Icon {
                    source: "kondor"; fallback: "internet-web-browser"
                    width: 16; height: 16
                    x: Kirigami.Units.largeSpacing; anchors.verticalCenter: parent.verticalCenter
                }
                Label {
                    anchors.centerIn: parent
                    text: "KDE Community — Developer Tools"
                }
                Row {
                    anchors.right: parent.right; anchors.rightMargin: Kirigami.Units.smallSpacing
                    anchors.verticalCenter: parent.verticalCenter
                    ToolButton { icon.name: "window-minimize"; display: AbstractButton.IconOnly; flat: true }
                    ToolButton { icon.name: "window-maximize"; display: AbstractButton.IconOnly; flat: true }
                    ToolButton { icon.name: "window-close"; display: AbstractButton.IconOnly; flat: true }
                }
            }
            DevToolsMock {
                Layout.fillWidth: true
                Layout.fillHeight: true
                dockSide: "undocked"
            }
        }
    }
}
