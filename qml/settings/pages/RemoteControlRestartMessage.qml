import QtQuick
import org.kde.kirigami as Kirigami
import Kondor

Kirigami.InlineMessage {
    id: root

    readonly property bool isSavedOn: Settings.remoteControlEnabled
    readonly property bool isPortChanged: isSavedOn && RemoteControl.active
        && Settings.remoteControlPort !== RemoteControl.port
    readonly property bool isHiddenForCommandLine: RemoteControl.requestedOnCommandLine && !isSavedOn

    type: Kirigami.MessageType.Information
    visible: !isHiddenForCommandLine && (isSavedOn !== RemoteControl.active || isPortChanged)
    text: qsTr("Restart Kondor to apply the remote control change.")
    actions: Kirigami.Action {
        text: qsTr("Restart Now")
        icon.name: "view-refresh"
        onTriggered: restartGuard.restartNow()
    }

    RestartGuard {
        id: restartGuard
    }
}
