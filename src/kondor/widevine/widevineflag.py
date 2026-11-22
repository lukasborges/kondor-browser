import os

from kondor.widevine.widevinestore import WidevineStore

CHROMIUM_FLAGS_VARIABLE = "QTWEBENGINE_CHROMIUM_FLAGS"
WIDEVINE_FLAG = "--widevine-path="


def with_widevine_path(flags: list[str], library: str) -> list[str]:
    kept = [flag for flag in flags if not flag.startswith(WIDEVINE_FLAG)]
    return [*kept, WIDEVINE_FLAG + library]


def current_flags() -> list[str]:
    return os.environ.get(CHROMIUM_FLAGS_VARIABLE, "").split()


def load_installed_widevine(store: WidevineStore | None = None) -> None:
    library = (store or WidevineStore()).installed_library()
    if library is not None:
        flags = with_widevine_path(current_flags(), str(library))
        os.environ[CHROMIUM_FLAGS_VARIABLE] = " ".join(flags)


def loaded_library() -> str:
    flags = current_flags()
    paths = [flag.removeprefix(WIDEVINE_FLAG) for flag in flags if flag.startswith(WIDEVINE_FLAG)]
    return paths[-1] if paths else ""
