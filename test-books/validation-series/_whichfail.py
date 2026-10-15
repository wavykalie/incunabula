# --- paths derived from this file, not from the machine that ran it ----------------
# The run happened at C:/Users/screa/incunabula; a clone is somewhere else, so walk up
# until the repository root (the directory holding tools/prose/) is found.
import os


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isdir(os.path.join(d, "tools", "prose")):
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return d


REPO = _repo_root()
import io, os, subprocess, glob

INC = REPO + "/tools/prose/deslop-check.sh"
for book in ("book-1", "book-2"):
    B = REPO + "/test-books/validation-series/%s/manuscript/chapters" % book
    print("##########", book)
    for f in sorted(glob.glob(B + "/chapter-*.md")):
        out = subprocess.run(["bash", INC, f], capture_output=True, text=True).stdout
        fails = [l.strip() for l in out.splitlines() if "FAIL" in l]
        if fails:
            print("  %-14s %s" % (os.path.basename(f), " | ".join(
                x.split(None, 1)[1][:70] for x in fails)))
