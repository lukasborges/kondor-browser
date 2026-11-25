#!/usr/bin/env bash
# Restore the Flatpak repository of the latest published release into a directory, so the new
# release keeps its commits and static deltas (docs/specs/0098-flatpak-repository.md).
# The source is the site archive attached to that release, not GitHub Pages: mirroring the site
# over HTTP made Pages answer 429 to release runs (v0.26.0, v0.26.1, v0.27.1).
#
# Usage: scripts/flatpak-restore-repo.sh <repo dir>
# GITHUB_REPOSITORY names the repository; GITHUB_REF_NAME, when it is a v* tag, is the release
# being built, and only older releases are used.
set -euo pipefail
shopt -s inherit_errexit

repo="$1"
archive_name="flatpak-repository.tar"
github="https://github.com/${GITHUB_REPOSITORY:?GITHUB_REPOSITORY must be set}"
current="${GITHUB_REF_NAME:-}"
pages_repo="https://lukasborges.github.io/kondor-browser/repo/"
max_releases=10
work="$(mktemp -d "${RUNNER_TEMP:-/tmp}/flatpak-restore.XXXXXX")"
trap 'rm -rf "$work"' EXIT

is_older_than_current() {
    [[ "$current" == v* ]] || return 0
    [ "$1" != "$current" ] && [ "$(printf '%s\n%s\n' "$1" "$current" | sort -V | head -n 1)" = "$1" ]
}

previous_tags() {
    local refs tag count=0
    refs="$(git ls-remote --tags --refs "$github" 'v*')"
    for tag in $(sed 's|.*refs/tags/||' <<<"$refs" | sort -V -r); do
        is_older_than_current "$tag" || continue
        echo "$tag"
        count=$((count + 1))
        [ "$count" -lt "$max_releases" ] || return 0
    done
}

# Prints the HTTP status; curl retries timeouts, 429 and 5xx on its own, never 404.
download_archive() {
    curl -sSL --retry 5 -o "$work/site.tar" -w '%{http_code}' \
        "$github/releases/download/$1/$archive_name"
}

extract_repo() {
    mkdir "$work/site"
    tar -xf "$work/site.tar" -C "$work/site"
    rm "$work/site.tar"
    test -f "$work/site/repo/config" || { echo "::error::$archive_name holds no repo/ directory"; exit 1; }
    rm -rf "$repo"
    mv "$work/site/repo" "$repo"
}

restored_tag=""

restore_from_release() {
    local status
    status="$(download_archive "$1")"
    case "$status" in
        200) extract_repo; restored_tag="$1"; echo "Restored the Flatpak repository of $1" ;;
        404) echo "$1 has no $archive_name (its Flatpak was not published)" ;;
        *) echo "::error::HTTP $status while downloading $archive_name of $1"; exit 1 ;;
    esac
}

# Used only until a release carries the archive: mirror the site once, as releases did before.
mirror_pages() {
    local attempt
    ostree remote add --repo="$repo" --no-gpg-verify published "$pages_repo"
    for attempt in 1 2 3 4 5; do
        ostree pull --repo="$repo" --mirror published && break
        [ "$attempt" = 5 ] && exit 1
        echo "::warning::Mirroring the published repository failed (attempt $attempt), retrying in $((attempt * 60)) s"
        sleep $((attempt * 60))
    done
    ostree remote delete --repo="$repo" published
}

restore_without_archive() {
    local status
    ostree init --mode=archive-z2 --repo="$repo"
    status="$(curl -sS --retry 3 --retry-all-errors -o /dev/null -w '%{http_code}' --head "${pages_repo}summary")"
    case "$status" in
        200) echo "::warning::No release carries $archive_name yet: mirroring GitHub Pages once"; mirror_pages ;;
        404) echo "::notice::Nothing is published yet: starting from an empty repository" ;;
        *) echo "::error::Unexpected HTTP status $status while checking the published repository"; exit 1 ;;
    esac
}

main() {
    local tags tag
    tags="$(previous_tags)"
    for tag in $tags; do
        restore_from_release "$tag"
        [ -z "$restored_tag" ] || return 0
    done
    restore_without_archive
}

main
