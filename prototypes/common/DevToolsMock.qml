// Chromium DevTools drawn by hand (only a visual imitation: it is a web page in the app).
// `dockSide`: "bottom", "left", "right" or "undocked" (the selected icon of the Dock side row).
// `menuOpen` shows DevTools' own ⋮ menu with its "Dock side" row.
import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    property string dockSide: "bottom"
    property bool menuOpen: false
    readonly property bool isNarrow: width < 600

    color: "#ffffff"
    clip: true

    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 30; color: "#f1f3f4"
            Row {
                anchors.verticalCenter: parent.verticalCenter; x: 10; spacing: 18
                Repeater {
                    model: root.isNarrow ? ["Elements", "Console", "»"] : ["Elements", "Console", "Sources", "Network", "Performance", "Application"]
                    Text { text: modelData; font.pixelSize: 12; color: index === 0 ? "#1a73e8" : "#3c4043" }
                }
            }
            Row {
                anchors.right: parent.right; anchors.rightMargin: 10; anchors.verticalCenter: parent.verticalCenter
                spacing: 14
                Text { text: "⚙"; color: "#5f6368"; font.pixelSize: 13 }
                Rectangle {
                    width: 18; height: 18; radius: 9; anchors.verticalCenter: parent.verticalCenter
                    color: root.menuOpen ? "#dfe1e5" : "transparent"
                    Text { anchors.centerIn: parent; text: "⋮"; color: "#5f6368"; font.pixelSize: 14 }
                }
                Text { text: "✕"; color: "#5f6368" }
            }
        }
        Text {
            Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: 10
            font.family: "monospace"; font.pixelSize: 12; color: "#3c4043"; textFormat: Text.RichText
            wrapMode: Text.WrapAnywhere
            text: "&lt;<span style='color:#881280'>body</span>&gt;<br>&nbsp;&nbsp;&lt;<span style='color:#881280'>header</span> <span style='color:#994500'>class</span>=<span style='color:#1a1aa6'>\"site-header\"</span>&gt;…&lt;/<span style='color:#881280'>header</span>&gt;<br>" +
                  "&nbsp;&nbsp;&lt;<span style='color:#881280'>main</span>&gt;<br>&nbsp;&nbsp;&nbsp;&nbsp;<span style='background-color:#cfe8fc'>&lt;<span style='color:#881280'>h1</span>&gt;Plasma 6&lt;/<span style='color:#881280'>h1</span>&gt; == $0</span><br>" +
                  "&nbsp;&nbsp;&nbsp;&nbsp;&lt;<span style='color:#881280'>p</span>&gt;…&lt;/<span style='color:#881280'>p</span>&gt;<br>&nbsp;&nbsp;&lt;/<span style='color:#881280'>main</span>&gt;<br>&lt;/<span style='color:#881280'>body</span>&gt;"
        }
    }

    Rectangle {
        visible: root.menuOpen
        anchors.right: parent.right; anchors.rightMargin: 8; y: 28
        width: 236; height: menuColumn.implicitHeight + 12
        radius: 8; color: "#ffffff"; border.color: "#dadce0"
        Column {
            id: menuColumn
            x: 0; y: 6; width: parent.width
            Item {
                width: parent.width; height: 32
                Text { x: 14; anchors.verticalCenter: parent.verticalCenter; text: "Dock side"; font.pixelSize: 12; color: "#3c4043" }
                Row {
                    anchors.right: parent.right; anchors.rightMargin: 10; anchors.verticalCenter: parent.verticalCenter
                    spacing: 4
                    Repeater {
                        model: [["undocked", "⧉"], ["left", "▏▢"], ["bottom", "▁"], ["right", "▢▕"]]
                        Rectangle {
                            width: 26; height: 22; radius: 4
                            color: modelData[0] === root.dockSide ? "#d3e3fd" : "transparent"
                            Rectangle {
                                anchors.centerIn: parent; width: 14; height: 12; radius: 2
                                color: "transparent"; border.width: 1.5
                                border.color: modelData[0] === root.dockSide ? "#1a73e8" : "#5f6368"
                                Rectangle {
                                    visible: modelData[0] !== "undocked"
                                    color: parent.border.color
                                    x: modelData[0] === "right" ? parent.width - width : 0
                                    y: modelData[0] === "bottom" ? parent.height - height : 0
                                    width: modelData[0] === "bottom" ? parent.width : 5
                                    height: modelData[0] === "bottom" ? 5 : parent.height
                                }
                                Rectangle {
                                    visible: modelData[0] === "undocked"
                                    x: 4; y: -4; width: 14; height: 12; radius: 2; color: "#ffffff"
                                    border.width: 1.5; border.color: parent.border.color
                                }
                            }
                        }
                    }
                }
            }
            Rectangle { width: parent.width; height: 1; color: "#dadce0" }
            Repeater {
                model: [["Show console drawer", "Esc"], ["Search", "Ctrl+Shift+F"], ["Run command", "Ctrl+Shift+P"], ["Open file", "Ctrl+P"], ["More tools", "›"]]
                Item {
                    width: menuColumn.width; height: 26
                    Text { x: 14; anchors.verticalCenter: parent.verticalCenter; text: modelData[0]; font.pixelSize: 12; color: "#3c4043" }
                    Text { anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; text: modelData[1]; font.pixelSize: 12; color: "#5f6368" }
                }
            }
        }
    }
}
