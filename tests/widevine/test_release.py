from kondor.widevine.release import PLATFORM, VENDOR, WidevineRelease, parse_release

SIZE = 123
ENTRY = {
    "fileUrl": "https://example.com/widevine.crx3",
    "mirrorUrls": ["https://mirror.example.com/widevine.crx3"],
    "filesize": SIZE,
    "hashValue": "abc",
}


def manifest(platforms: dict[str, object]) -> dict[str, object]:
    vendor = {"version": "4.10.1", "platforms": platforms}
    return {"hashFunction": "sha512", "vendors": {VENDOR: vendor}}


def test_reads_the_linux_entry() -> None:
    release = parse_release(manifest({PLATFORM: ENTRY}))
    assert release == WidevineRelease(
        "4.10.1",
        ["https://example.com/widevine.crx3", "https://mirror.example.com/widevine.crx3"],
        SIZE,
        "abc",
        "sha512",
    )


def test_follows_an_alias() -> None:
    release = parse_release(manifest({PLATFORM: {"alias": "Linux_x86_64"}, "Linux_x86_64": ENTRY}))
    assert release is not None and release.size == SIZE


def test_missing_platform_gives_no_release() -> None:
    assert parse_release(manifest({"WINNT_x86_64-msvc": ENTRY})) is None


def test_garbage_gives_no_release() -> None:
    assert parse_release(["not", "a", "manifest"]) is None
