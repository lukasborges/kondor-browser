import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import Kondor
import "../common/html.js" as Html

RowLayout {
    id: root

    required property string widevineState
    required property string host

    readonly property var iconNames: ({
        missing: "media-playback-start",
        downloading: "download",
        failed: "dialog-warning",
        ready: "view-refresh"
    })

    function downloadingText() {
        if (Widevine.totalMegabytes === 0)
            return qsTr("Downloading Widevine…")
        return qsTr("Downloading Widevine: %1 of %2 MB")
            .arg(Widevine.downloadedMegabytes).arg(Widevine.totalMegabytes)
    }

    function messageText() {
        switch (widevineState) {
        case "downloading": return downloadingText()
        case "failed": return qsTr("Could not download the Widevine module.")
        case "ready": return qsTr("Widevine is ready. Restart Kondor to play protected video.")
        }
        //: %1 is the site host, in bold
        return qsTr("<b>%1</b> needs Google's Widevine module to play protected video.")
            .arg(Html.escaped(host))
    }

    spacing: Kirigami.Units.smallSpacing

    Kirigami.Icon {
        source: root.iconNames[root.widevineState] ?? "media-playback-start"
        Layout.preferredWidth: Kirigami.Units.iconSizes.small
        Layout.preferredHeight: Kirigami.Units.iconSizes.small
    }

    Label {
        Layout.fillWidth: true
        elide: Text.ElideRight
        textFormat: Text.StyledText
        text: root.messageText()
    }
}
