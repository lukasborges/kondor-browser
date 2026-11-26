import QtQuick
import Kondor

Item {
    id: root

    required property TabModel tabModel
    required property var browserActions

    function closeView(view) {
        OpenerViews.retire(view.pageView)
        view.destroy()
    }

    // A Repeater clears its delegate's QML context before deleting it, and a page script result
    // arriving in between crashes Qt WebEngine, so each view lives outside the delegate context
    // and is a child of this item, which deletes it together with that context:
    // https://github.com/lukasborges/kondor-browser/issues/458
    Component {
        id: viewComponent

        WebViewTab {
            anchors.fill: parent
            visible: tabModel.currentTab === tab
        }
    }

    Repeater {
        model: root.tabModel

        delegate: Item {
            id: slot

            required property Tab tab
            property WebViewTab view: null

            Component.onCompleted: slot.view = viewComponent.createObject(root, {
                tab: slot.tab, tabModel: root.tabModel, browserActions: root.browserActions
            })
            Component.onDestruction: {
                if (slot.view)
                    root.closeView(slot.view)
            }
        }
    }
}
