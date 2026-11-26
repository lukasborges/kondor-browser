import QtQuick
import Kondor

Item {
    id: root

    required property TabModel tabModel
    required property var browserActions

    // A Repeater clears its delegate's QML context before deleting it, and a page script result
    // arriving in between crashes Qt WebEngine, so each view lives outside the delegate context:
    // https://github.com/lukasborges/kondor-browser/issues/458
    Component {
        id: viewComponent

        WebViewTab {
            anchors.fill: parent
        }
    }

    Repeater {
        model: root.tabModel

        delegate: Item {
            id: slot

            required property Tab tab
            property WebViewTab view: null

            anchors.fill: parent
            visible: root.tabModel.currentTab === slot.tab
            Component.onCompleted: slot.view = viewComponent.createObject(slot, {
                tab: slot.tab, tabModel: root.tabModel, browserActions: root.browserActions
            })
            Component.onDestruction: {
                if (slot.view)
                    OpenerViews.retire(slot.view.pageView)
            }
        }
    }
}
