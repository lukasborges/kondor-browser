from typing import NamedTuple

MANIFEST_URL = (
    "https://raw.githubusercontent.com/mozilla-firefox/firefox/main/"
    "toolkit/content/gmp-sources/widevinecdm.json"
)
VENDOR = "gmp-widevinecdm"
PLATFORM = "Linux_x86_64-gcc3"


class WidevineRelease(NamedTuple):
    version: str
    urls: list[str]
    size: int
    hash: str
    algorithm: str


def mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def platform_entry(platforms: dict[str, object]) -> dict[str, object]:
    entry = mapping(platforms.get(PLATFORM))
    alias = entry.get("alias")
    return mapping(platforms.get(alias)) if isinstance(alias, str) else entry


def download_urls(entry: dict[str, object]) -> list[str]:
    mirrors = entry.get("mirrorUrls")
    extra = [url for url in mirrors if isinstance(url, str)] if isinstance(mirrors, list) else []
    first = entry.get("fileUrl")
    return [first, *extra] if isinstance(first, str) else extra


def parse_release(document: object) -> WidevineRelease | None:
    vendor = mapping(mapping(mapping(document).get("vendors")).get(VENDOR))
    entry = platform_entry(mapping(vendor.get("platforms")))
    release = WidevineRelease(
        str(vendor.get("version", "")),
        download_urls(entry),
        int(str(entry.get("filesize", 0))),
        str(entry.get("hashValue", "")),
        str(mapping(document).get("hashFunction", "")),
    )
    return release if is_complete(release) else None


def is_complete(release: WidevineRelease) -> bool:
    return bool(release.version and release.urls and release.hash and release.algorithm)
