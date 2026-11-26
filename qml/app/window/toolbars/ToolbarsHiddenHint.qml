import QtQuick
import org.kde.kirigami as Kirigami
import Kondor

FullScreenHint {
    id: root

    required property bool isWindowFullScreen
    required property bool areToolbarsHidden

    y: Kirigami.Units.gridUnit * 2
    iconName: ""
    //: Shown for a few seconds after the toolbars get hidden
    text: qsTr("Toolbars hidden")
    actionText: qsTr("Show Toolbars")
    actionIconName: "view-visible"
    actionToolTip: isWindowFullScreen
        ? qsTr("F11, or move the pointer to the top")
        : qsTr("Ctrl+Shift+F, or move the pointer to the top")
    duration: 5000
    shownOpacity: 0.95
    isOutlined: true

    onAreToolbarsHiddenChanged: {
        if (areToolbarsHidden)
            announce(qsTr("Toolbars hidden. Move the pointer to the top edge or press Ctrl+L to show them."))
    }
}
