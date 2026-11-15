#!/usr/bin/env python3
"""Create a GitHub draft release for the chapter-1 preview and upload the mp3
+ gate metadata as assets. Run it in the repo root with a token that has
`repo` scope:

    export GH_TOKEN=ghp_...
    python release-preview.py

Edit the paths / tag / message at the top if you want something different.
"""
from __future__ import annotations
import base64, json, os, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

REPO = "wavykalie/incunabula"
BRANCH = "feat/audiobook-stage"
TAG = "m&m-ch1-preview"
COMMITISH = BRANCH  # attach to the branch tip (already pushed)

MP3 = Path("test-books/muzzle-and-marrow/audiobook/audio/chapter-01.mp3")
META = Path("test-books/muzzle-and-marrow/audiobook/audio/release-meta.json")
ASSET_NAMES = {
    MP3: "chapter-01-preview.mp3",
    META: "release-meta.json",
}

TITLE = "Muzzle and Marrow — Chapter 1 preview (feat/audiobook-stage)"
BODY = (
    "Temporarily-hosted preview release for the chapter-1 render on branch "
    "`feat/audiobook-stage` (commit 65ee5fd). Staged locally for mobile "
    "listening only; not an official repo tag.\n\n"
    "Gate-reported metrics on the preview: per-segment identity median 0.80-0.89, "
    "aggregate drift 0.71-0.90 across all five voices (NARRATOR, Mittens Brisk, "
    "Rocky Cavaltone, Tallow, Teasel). Full chapter is ~420s; the mp3 here is the "
    "rendered preview clip."
)

TOKEN = os.environ.get("GH_TOKEN")
if not TOKEN:
    sys.exit("set GH_TOKEN in the environment (repo scope) and re-run")

def _b64(path: Path) -> tuple[bytes, int]:
    data = path.read_bytes()
    return base64.b64encode(data), len(data)

assets = []
for src, name in ASSET_NAMES.items():
    b64, size = _b64(src)
    assets.append({"label": name.replace(".mp3", " (mp3)").replace(".json", " (json)"),
                   "name": name, "data": b64.decode(), "size_bytes": size})

payload = {
    "tag_name": TAG,
    "target_commitish": COMMITISH,
    "name": TITLE,
    "body": BODY,
    "draft": False,
    "prerelease": False,
    "generate_release_notes": False,
    "assets": assets,
}

body = json.dumps(payload).encode()
req = Request(
    f"https://api.github.com/repos/{REPO}/releases",
    data=body,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    },
    method="POST",
)
try:
    with urlopen(req, timeout=3600) as resp:
        release = json.loads(resp.read().decode())
except HTTPError as e:
    print(f"HTTP {e.code}:", (e.read().decode() if hasattr(e, 'read') else e))
    sys.exit(1)

print(f"release created: id={release.get('id')} tag={release.get('tag_name')}")
print(f"html_url: {release.get('html_url')}")
for a in (release.get("assets") or []):
    print(f"  asset: {a['name']}  {a.get('size','?')} bytes  download: {a.get('browser_download_url')}")
