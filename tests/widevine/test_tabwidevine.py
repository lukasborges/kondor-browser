from PySide6.QtCore import QUrl

from kondor.widevine.tabwidevine import TabWidevine


def test_request_shows_the_offer(qapp: object) -> None:
    widevine = TabWidevine()
    widevine.mark_requested()
    assert widevine.isRequested


def test_dismissed_offer_stays_hidden_on_the_same_page(qapp: object) -> None:
    widevine = TabWidevine()
    widevine.dismiss()
    widevine.mark_requested()
    assert not widevine.isRequested


def test_next_page_can_show_the_offer_again(qapp: object) -> None:
    widevine = TabWidevine()
    widevine.dismiss()
    widevine.reset()
    widevine.mark_requested()
    assert widevine.isRequested


def test_host_follows_the_page(qapp: object) -> None:
    widevine = TabWidevine()
    widevine.update_for(QUrl("https://www.netflix.com/watch/1"))
    assert widevine.host == "www.netflix.com"
