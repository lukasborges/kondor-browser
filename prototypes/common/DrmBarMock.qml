// #452 Protected content (DRM): the bar shown when a page asks for Widevine and the module is
// missing. state: "offer" (first request), "downloading" (module being fetched), "restart"
// (module ready, Kondor must restart to load it).
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

ColumnLayout {
    id: root
    property string state: "offer"
    Layout.fillWidth: true
    spacing: 0

    Kirigami.InlineMessage {
        Layout.fillWidth: true
        position: Kirigami.InlineMessage.Position.Header
        visible: root.state === "offer"
        type: Kirigami.MessageType.Information
        icon.name: "media-playback-start"
        showCloseButton: true
        text: "<b>www.netflix.com</b> needs Google's Widevine module to play protected video."
        actions: [
            Kirigami.Action { text: "Download Widevine"; icon.name: "download" }
        ]
    }

    Kirigami.InlineMessage {
        Layout.fillWidth: true
        position: Kirigami.InlineMessage.Position.Header
        visible: root.state === "downloading"
        type: Kirigami.MessageType.Information
        icon.name: "download"
        text: "Downloading Widevine: 9 of 21 MB"
        actions: [
            Kirigami.Action { text: "Cancel"; icon.name: "dialog-cancel" }
        ]
    }

    Kirigami.InlineMessage {
        Layout.fillWidth: true
        position: Kirigami.InlineMessage.Position.Header
        visible: root.state === "restart"
        type: Kirigami.MessageType.Positive
        icon.name: "view-refresh"
        text: "Widevine is ready. Restart Kondor to play protected video."
        actions: [
            Kirigami.Action { text: "Restart Now"; icon.name: "view-refresh" }
        ]
    }
}
