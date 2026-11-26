from collections.abc import Iterator

import pytest
import shiboken6
from PySide6.QtCore import QCoreApplication, QEvent, QObject, QUrl
from PySide6.QtQuick import QQuickItem

from kondor.browser.popups.openerviews import DISCARDED, OpenerViews


@pytest.fixture
def keeper(qapp: object) -> Iterator[OpenerViews]:
    views = OpenerViews()
    yield views
    views.release_all()


def make_view(parent: QQuickItem | None = None) -> QQuickItem:
    view = QQuickItem(parent)
    view.setProperty("icon", QUrl())
    return view


def open_from(keeper: OpenerViews, opener: QQuickItem) -> QQuickItem:
    request, adopter = QObject(), make_view()
    keeper.noteOpener(request, opener)
    keeper.noteAdopter(request, adopter)
    return adopter


def process_deferred_deletes() -> None:
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_retire_keeps_the_opener_of_a_live_page(keeper: OpenerViews) -> None:
    tab_item = QQuickItem()
    opener = make_view(tab_item)
    adopter = open_from(keeper, opener)
    keeper.retire(opener)
    shiboken6.delete(tab_item)
    assert shiboken6.isValid(opener) and shiboken6.isValid(adopter)
    assert opener.property("lifecycleState") == DISCARDED
    assert opener.parentItem() is None


def test_retire_ignores_a_view_that_opened_nothing(keeper: OpenerViews) -> None:
    tab_item = QQuickItem()
    view = make_view(tab_item)
    keeper.retire(view)
    shiboken6.delete(tab_item)
    assert not shiboken6.isValid(view)


def test_closing_the_opened_page_releases_the_kept_opener(keeper: OpenerViews) -> None:
    opener = make_view()
    adopter = open_from(keeper, opener)
    keeper.retire(opener)
    shiboken6.delete(adopter)
    process_deferred_deletes()
    assert not shiboken6.isValid(opener)


def test_opener_stays_while_another_opened_page_lives(keeper: OpenerViews) -> None:
    opener = make_view()
    first, second = open_from(keeper, opener), open_from(keeper, opener)
    keeper.retire(opener)
    shiboken6.delete(first)
    process_deferred_deletes()
    assert shiboken6.isValid(opener)
    shiboken6.delete(second)


def test_adoption_without_a_noted_opener_keeps_nothing(keeper: OpenerViews) -> None:
    opener, adopter = make_view(), make_view()
    keeper.noteAdopter(QObject(), adopter)
    assert not keeper.opens_live_pages(opener)


def test_release_all_deletes_kept_views(keeper: OpenerViews) -> None:
    opener = make_view()
    adopter = open_from(keeper, opener)
    keeper.retire(opener)
    keeper.release_all()
    assert not shiboken6.isValid(opener) and shiboken6.isValid(adopter)
