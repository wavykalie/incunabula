# Normalise the Merope chapter files from \r\r\n to LF.
#
# This is the OTHER half of the Freeze 7 fix. The gate now strips CR in its read path,
# so it reports the same numbers either way - but the files themselves should not be
# carrying a stray CR, and \r\r\n is what defeated the sentence split in the first
# place. Writing them back as plain LF also makes them survive a clone byte-exactly,
# the same property demo-magician already has.
#
# Nothing but line endings changes. The check below proves it: the text with every CR
# and LF removed must be IDENTICAL before and after, and the word count must not move.

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
import glob, io, os, re, subprocess

INC = REPO + "/tools/prose/deslop-check.sh"
KEEP = ("A25", "A6", "P1", "P2", "P3")


def rows(path):
    r = subprocess.run(["bash", INC, path], capture_output=True, text=True).stdout
    out = {}
    for line in r.splitlines():
        m = re.match(r"\s+(FAIL|ok|warn|--)\s+(\S+)\s+(.*)$", line)
        if m and m.group(2) in KEEP:
            out[m.group(2)] = m.group(1) + " " + m.group(3).strip()
    return out


total = changed = 0
for book in ("book-1", "book-2"):
    for f in sorted(glob.glob(REPO + "/test-books/validation-series/%s/manuscript/chapters/*.md" % book)):
        raw = io.open(f, encoding="utf-8", newline="").read()
        total += 1
        if "\r" not in raw:
            continue
        before = raw.replace("\r", "").replace("\n", "")
        r_before = rows(f)
        io.open(f, "w", encoding="utf-8", newline="\n").write(raw.replace("\r", ""))
        after = io.open(f, encoding="utf-8", newline="").read().replace("\n", "")
        assert before == after, "CONTENT CHANGED in %s" % f
        assert "\r" not in io.open(f, encoding="utf-8", newline="").read()
        r_after = rows(f)
        same = all(r_before.get(k) == r_after.get(k) for k in KEEP)
        changed += 1
        print("%-46s content identical: yes | gate rows unchanged: %s"
              % (book + "/" + os.path.basename(f), "yes" if same else "NO"))
        if not same:
            for k in KEEP:
                if r_before.get(k) != r_after.get(k):
                    print("      %s  %r -> %r" % (k, r_before.get(k), r_after.get(k)))
print("\n%d of %d files rewritten; all content verified identical"
      % (changed, total))
