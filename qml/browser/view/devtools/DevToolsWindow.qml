import QtQuick
import QtQuick.Controls
import org.kde.kirigami as Kirigami
import Kondor

ApplicationWindow {
    id: root

    required property Tab tab

    signal closeRequested()

    function pageName() {
        return root.tab.title !== "" ? root.tab.title : root.tab.url.toString()
    }

    //: Title of the window that holds undocked developer tools; %1 is the inspected page
    title: qsTr("%1 — Developer Tools").arg(root.pageName())
    width: Kirigami.Units.gridUnit * 50
    height: Kirigami.Units.gridUnit * 35
    onClosing: function(close) {
        close.accepted = false
        root.closeRequested()
    }
    onVisibleChanged: {
        if (visible)
            root.requestActivate()
    }
}
