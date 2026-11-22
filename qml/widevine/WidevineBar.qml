import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Kondor

InlineBar {
    id: root

    property Tab tab: null

    readonly property string widevineState: Widevine.state
    readonly property bool isDownloading: widevineState === "downloading"
    readonly property bool isFailed: widevineState === "failed"
    readonly property bool isReady: widevineState === "ready"

    visible: tab !== null && tab.widevine.isRequested && widevineState !== "loaded"

    WidevineBarMessage {
        Layout.fillWidth: true
        widevineState: root.widevineState
        host: root.tab ? root.tab.widevine.host : ""
    }

    Button {
        visible: root.widevineState === "missing"
        text: qsTr("Download Widevine")
        icon.name: "download"
        onClicked: Widevine.download()
    }

    Button {
        visible: root.isDownloading
        text: qsTr("Cancel")
        icon.name: "dialog-cancel"
        onClicked: Widevine.cancel()
    }

    Button {
        visible: root.isFailed
        text: qsTr("Try Again")
        icon.name: "view-refresh"
        onClicked: Widevine.download()
    }

    Button {
        visible: root.isReady
        text: qsTr("Restart Now")
        icon.name: "view-refresh"
        onClicked: restartGuard.restartNow()
    }

    ToolButton {
        visible: !root.isDownloading
        display: AbstractButton.IconOnly
        icon.name: "window-close"
        text: qsTr("Close")
        Accessible.name: text
        ToolTip.visible: hovered
        ToolTip.text: text
        ToolTip.delay: 600
        onClicked: root.tab.widevine.dismiss()
    }

    RestartGuard {
        id: restartGuard
    }
}
