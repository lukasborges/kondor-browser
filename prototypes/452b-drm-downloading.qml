// #452 Protected content (DRM), state "downloading": see common/DrmBarMock.qml.
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import "common"

BrowserFrame {
    address: "https://www.netflix.com/watch/70171996"
    tabs: [{ title: "Netflix", icon: "internet-web-browser" }]
    addressLeft: [
        ToolButton { icon.name: "security-high"; display: AbstractButton.IconOnly; flat: true; implicitWidth: 28; implicitHeight: 28 }
    ]
    belowHeader: [ DrmBarMock { state: "downloading" } ]
    Rectangle {
        anchors.fill: parent
        color: "#141414"
        Column {
            anchors.centerIn: parent
            spacing: 18
            Text { text: "Sorry for the interruption"; color: "#ffffff"; font.pixelSize: 34; font.bold: true; anchors.horizontalCenter: parent.horizontalCenter }
            Text { text: "Error code M7701-1003"; color: "#b3b3b3"; font.pixelSize: 18; anchors.horizontalCenter: parent.horizontalCenter }
        }
    }
}
