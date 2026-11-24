import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "flatpak-restore-repo.sh"
TAGS = ["v0.9.0", "v0.26.3", "v0.27.0", "v0.27.1", "v0.28.0"]

GIT_STUB = """#!/bin/bash
[ -n "$FAIL_GIT" ] && exit 128
for tag in $TAGS; do printf 'id\\trefs/tags/%s\\n' "$tag"; done
"""

CURL_STUB = """#!/bin/bash
url="${@: -1}"; prev=""
for arg in "$@"; do [ "$prev" = -o ] && out="$arg"; prev="$arg"; done
echo "curl $url" >> "$LOG"
case "$url" in
  *github.io*) printf '%s' "$PAGES_STATUS" ;;
  */releases/download/"$ARCHIVE_TAG"/*) cp "$ARCHIVE" "$out"; printf 200 ;;
  */releases/download/*) printf '%s' "$MISSING_STATUS" ;;
esac
"""

OSTREE_STUB = """#!/bin/bash
echo "ostree $*" >> "$LOG"
"""


def write_tool(folder: Path, name: str, text: str) -> None:
    path = folder / name
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def site_archive(root: Path, with_repo: bool = True) -> Path:
    site = root / "site"
    (site / "repo" / "objects").mkdir(parents=True)
    if with_repo:
        (site / "repo" / "config").write_text("[core]\n", encoding="utf-8")
    archive = root / "artifact.tar"
    with tarfile.open(archive, "w") as tar:
        tar.add(site, arcname=".")
    return archive


class FlatpakRestoreRepoTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for name, text in (("git", GIT_STUB), ("curl", CURL_STUB), ("ostree", OSTREE_STUB)):
            write_tool(self.bin, name, text)
        self.log = self.root / "log"
        self.log.touch()

    def restore(self, **environment: str) -> subprocess.CompletedProcess:
        values = {"GITHUB_REF_NAME": "v0.27.2", "PAGES_STATUS": "200", "MISSING_STATUS": "404",
                  "ARCHIVE_TAG": "none", "ARCHIVE": "", **environment}
        env = {**os.environ, **values, "PATH": f"{self.bin}:{os.environ['PATH']}",
               "LOG": str(self.log), "RUNNER_TEMP": str(self.root), "TAGS": " ".join(TAGS),
               "GITHUB_REPOSITORY": "owner/repo"}
        return subprocess.run(["bash", str(SCRIPT), "repo"], check=False, cwd=self.root,
                              env=env, capture_output=True, text=True)

    def calls(self) -> list[str]:
        return self.log.read_text(encoding="utf-8").splitlines()

    def test_restores_the_newest_older_release_with_an_archive(self):
        result = self.restore(ARCHIVE_TAG="v0.27.0", ARCHIVE=str(site_archive(self.root)))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / "repo" / "config").is_file())
        self.assertEqual([call.split("/")[-2] for call in self.calls()], ["v0.27.1", "v0.27.0"])

    def test_mirrors_pages_when_no_release_has_an_archive(self):
        result = self.restore()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ostree pull --repo=repo --mirror published", self.calls())

    def test_starts_empty_when_nothing_is_published(self):
        result = self.restore(PAGES_STATUS="404")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ostree init --mode=archive-z2 --repo=repo", self.calls())
        self.assertFalse(any("pull" in call for call in self.calls()))

    def test_fails_when_the_tags_cannot_be_listed(self):
        result = self.restore(FAIL_GIT="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_fails_on_an_unexpected_download_status(self):
        result = self.restore(MISSING_STATUS="500")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any("ostree" in call for call in self.calls()))

    def test_fails_when_the_archive_has_no_repository(self):
        archive = site_archive(self.root, with_repo=False)
        result = self.restore(ARCHIVE_TAG="v0.27.1", ARCHIVE=str(archive))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("holds no repo/", result.stdout)


if __name__ == "__main__":
    unittest.main()
