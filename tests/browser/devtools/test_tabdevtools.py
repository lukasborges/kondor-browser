from pytestqt.qtbot import QtBot

from kondor.browser.devtools.tabdevtools import TabDevTools


def test_new_dev_tools_dock_at_the_bottom(qapp: object) -> None:
    assert TabDevTools().dockSide == "bottom"


def test_known_dock_side_is_kept(qapp: object) -> None:
    dev_tools = TabDevTools()
    dev_tools.setDockSide("undocked")
    assert dev_tools.dockSide == "undocked"


def test_unknown_dock_side_falls_back_to_the_bottom(qapp: object) -> None:
    dev_tools = TabDevTools()
    dev_tools.setDockSide("left")
    dev_tools.setDockSide("top")
    assert dev_tools.dockSide == "bottom"


def test_same_dock_side_does_not_notify(qapp: object, qtbot: QtBot) -> None:
    dev_tools = TabDevTools()
    with qtbot.assertNotEmitted(dev_tools.dockSideChanged):
        dev_tools.setDockSide("bottom")


def test_move_requests_a_known_side(qapp: object, qtbot: QtBot) -> None:
    dev_tools = TabDevTools()
    with qtbot.waitSignal(dev_tools.moveRequested) as moved:
        dev_tools.moveTo("sideways")
    assert moved.args == ["bottom"]
