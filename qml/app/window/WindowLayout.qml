import QtQuick
import Kondor

QtObject {
    property bool areToolbarsHidden: false
    property bool isBookmarksBarShown: false
    property bool isSideBarCollapsed: false

    function setToolbarsHidden(hidden) {
        areToolbarsHidden = hidden
        Settings.hideToolbars = hidden
    }

    function setBookmarksBarShown(shown) {
        isBookmarksBarShown = shown
        Settings.showBookmarksBar = shown
    }

    function toggleBookmarksBar() {
        setBookmarksBarShown(!isBookmarksBarShown)
    }

    function toggleSideBar() {
        isSideBarCollapsed = !isSideBarCollapsed
        Settings.sideBarCollapsed = isSideBarCollapsed
    }

    Component.onCompleted: {
        areToolbarsHidden = Settings.hideToolbars
        isBookmarksBarShown = Settings.showBookmarksBar
        isSideBarCollapsed = Settings.sideBarCollapsed
    }
}
