import QtQuick
import Kondor

Item {
    id: root

    function restartNow() {
        if (DownloadManager.hasActiveDownloads)
            restartDialog.open()
        else
            AppRestart.restart()
    }

    ConfirmDialog {
        id: restartDialog
        //: %1 is the application name
        title: qsTr("Restart %1").arg(Qt.application.displayName)
        message: qsTr("Downloads are still in progress. Restart anyway?")
        acceptText: qsTr("Restart")
        acceptIcon: "view-refresh"
        destructive: false
        onAccepted: AppRestart.restart()
    }
}
