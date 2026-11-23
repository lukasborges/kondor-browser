import QtQuick
import QtQuick.Controls

MenuItem {
    id: root

    required property string side
    required property string currentSide

    signal sideChosen(string side)

    checkable: true
    autoExclusive: true
    checked: root.side === root.currentSide
    onTriggered: root.sideChosen(root.side)
}
