# Play protected content (DRM) with Widevine (#452)

> **Issue:** [#452](https://github.com/lukasborges/kondor-browser/issues/452) · **Priority:** P2 (medium) · **State:** see the issue's label (`to-spec` / `to-dev` / `in-review`).
> This file is the source of truth for the issue.

## Objective

Netflix, Disney+, Spotify and other streaming sites need a DRM module (Encrypted Media
Extensions with Google's **Widevine**). Kondor has none, so they fail (Netflix: "M7701-1003").
Like Firefox, Kondor offers to download Google's Widevine module when a page asks for it, then
restarts to load it. The module cannot be shipped with Kondor (Google's license does not allow
redistribution), so it is downloaded from Google only after the user clicks.

## Context

- Qt WebEngine is built with Widevine support (the Flatpak's `libQt6WebEngineCore.so` has the
  `--widevine-path` switch and the `com.widevine.alpha` key system). It loads the module given by
  the Chromium flag `--widevine-path=<file>` at startup, so a new module needs a restart.
- Chromium flags are set in `src/kondor/app/startup/environment.py`
  (`QTWEBENGINE_CHROMIUM_FLAGS`).
- Restart with windows and tabs back: `src/kondor/app/restart/apprestart.py` (`AppRestart`,
  #419), used by `qml/settings/pages/RemoteControlRestartMessage.qml`.
- Bars at the top of the page: `qml/common/InlineBar.qml`, `qml/common/bars/`.
- Page scripts and the isolated-world bridge: extensions (#218) and the translator (#441).
- App data downloads with a hash check: the translator's model downloads (#441).

## Design / behavior

Prototypes: `452-drm-offer`, `452b-drm-downloading`, `452c-drm-restart` (approved; shared mock
`prototypes/common/DrmBarMock.qml`).

### 1. When the offer shows (`452-drm-offer`)

- A main-world page script wraps `navigator.requestMediaKeySystemAccess`. When a page asks for
  `com.widevine.alpha` (or any `com.widevine.*` key system) and the call is rejected because the
  key system is not available, the script tells Kondor (DOM event read by the isolated-world
  bridge). The page's own call is not changed: it still gets the rejection.
- If the module is not installed, the tab shows a bar (`Kirigami.InlineMessage`, Information,
  icon `media-playback-start`, close button):
  "**<host>** needs Google's Widevine module to play protected video." with the action
  **Download Widevine** (`download`).
- The bar shows once per page load; closing it hides it until the next load. It never shows when
  the module is installed and loaded, or while a download is in progress in another tab (that tab
  shows the downloading bar instead, item 2).
- In private tabs the bar shows too: the module is not data about the site, and nothing about the
  site is written.

### 2. Download (`452b-drm-downloading`)

- **Download Widevine** fetches the manifest Firefox uses, from Firefox's repository:
  `https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/content/gmp-sources/widevinecdm.json`
  (`vendors["gmp-widevinecdm"]`, platform `Linux_x86_64-gcc3`, which may be an `alias` of another
  entry). It gives the `version`, `fileUrl` (a Google CRX3 file), `mirrorUrls`, `filesize`,
  `hashFunction` (`sha512`) and `hashValue`.
- The file is downloaded from `fileUrl` (then each mirror on failure) with
  `QNetworkAccessManager`; the bar shows "Downloading Widevine: N of M MB" with **Cancel**
  (`dialog-cancel`). Every tab with the offer bar shows the same progress.
- The file is checked against `hashValue` before use. CRX3 is a header (`Cr24`, version 3, header
  length, header) followed by a ZIP; Kondor skips the header and extracts
  `_platform_specific/linux_x64/libwidevinecdm.so` and `manifest.json` to
  `AppDataLocation/widevine/<version>/`, writes `AppDataLocation/widevine/current` with the
  version, and deletes older versions. Nothing else from the archive is kept.
- **Cancel** stops the download and deletes the partial file. A failure (offline, hash mismatch,
  missing file in the archive) turns the bar into a Warning: "Could not download the Widevine
  module." with **Try Again**.
- Architectures other than x86_64 get no offer (Mozilla's manifest has no Linux ARM entry).

### 3. Restart (`452c-drm-restart`)

- When the module is in place, the bar becomes Positive (`view-refresh`): "Widevine is ready.
  Restart Kondor to play protected video." with **Restart Now** (`view-refresh`), which calls the
  same restart as #419 (downloads guard, session saved, every window and tab back).
- At startup, if `AppDataLocation/widevine/current` names an installed version, Kondor adds
  `--widevine-path=<that folder>/libwidevinecdm.so` to `QTWEBENGINE_CHROMIUM_FLAGS` (keeping the
  flags already there).
- After the restart, the page that asked can play: `requestMediaKeySystemAccess("com.widevine.alpha", …)`
  resolves.

### 4. Flatpak and AppImage

- The module lives in Kondor's own data folder, which both packages can read; no new Flatpak
  permission is needed.
- The Flatpak's WebEngine already supports Widevine; the AppImage's WebEngine must be checked
  (Fedora's `qt6-qtwebengine`); if it lacks Widevine, the offer is not shown there (feature test:
  the key system list of the running WebEngine).

## Acceptance criteria

- [ ] On a page that asks for Widevine, with no module installed, the offer bar shows with the
      host; a page that does not use DRM never shows it.
- [ ] Download Widevine fetches the manifest, downloads the CRX3 with progress, checks SHA-512,
      extracts only the library and its manifest, and shows Restart Now.
- [ ] Cancel removes the partial file; a wrong hash or no network shows the warning with Try Again.
- [ ] After Restart Now, every tab is back and `navigator.requestMediaKeySystemAccess("com.widevine.alpha", …)`
      resolves; the bar does not show again.
- [ ] Kondor starts normally when the module folder is missing or damaged (no flag added).
- [ ] Netflix plays a title in the Flatpak (manual test); note the resolution reached in the PR.
- [ ] Matches the three prototypes in Breeze and Breeze Dark; strings in `qsTr()`, translations
      complete; README: one "Protected content" bullet.
- [ ] Python checks pass (`ruff`, `mypy --strict`, `scripts/run-pytests.sh`,
      `check-code-quality.py --changed origin/main`); pytest covers manifest parsing (with
      aliases), the CRX3 header skip, the hash check and the startup flag.

## Manual test

Separate instance with isolated XDG folders under `~/kondor-test`, `--new-instance`.

1. Open `https://bitmovin.com/demos/drm` (or another Widevine test page): the offer shows.
2. Download Widevine: progress, then Restart Now; the test page plays.
3. Sign in to Netflix and play a title.
4. Delete the module folder and start again: Kondor starts, the offer shows again.

## Out of scope

- Other DRM systems (PlayReady, ClearKey beyond what Qt has), hardware-backed Widevine (L1),
  automatic updates of the module (a new version is offered only if the installed one stops
  working: future issue), a settings page to remove the module, ARM.

## Dependencies

- #419 (Restart Now, merged).

## Prototype

- [`452-drm-offer.qml`](../../prototypes/452-drm-offer.qml) →
  [screenshot](../../prototypes/screenshots/452-drm-offer.png)
- [`452b-drm-downloading.qml`](../../prototypes/452b-drm-downloading.qml) →
  [screenshot](../../prototypes/screenshots/452b-drm-downloading.png)
- [`452c-drm-restart.qml`](../../prototypes/452c-drm-restart.qml) →
  [screenshot](../../prototypes/screenshots/452c-drm-restart.png)

## Decisions

| Question | Decision |
| --- | --- |
| Ship the module? | No: Google's license does not allow redistribution. Download it from Google on the user's click, like Firefox. |
| Where does the download address come from? | Firefox's `widevinecdm.json`: Mozilla keeps it current with the version, Google's file address and its SHA-512. Google's old `dl.google.com/widevine-cdm/versions.txt` is gone (404). |
| Ask first or download on its own? | Ask, with the bar, only when a page needs it (KDE HIG: no surprise downloads); no setting is needed. |
| Progress bar in the bar? | No: the InlineMessage has no room for it without covering the text; the text shows N of M MB (prototype review). |
| Restart? | Required: Qt WebEngine reads `--widevine-path` only at startup; reuse Restart Now (#419). |
