# Diff my locator against the real gate, chapter by chapter.
# Any disagreement is a bug in _locate.py, not a fact about the manuscript.
# Nothing gets patched until the two agree.

import glob, io, os, re, subprocess, sys

INC = "C:/Users/screa/incunabula/tools/prose/deslop-check.sh"
sys.path.insert(0, "C:/Users/screa/incunabula/test-books/validation-series")
import _locate as L


def gate_rows(f):
    out = subprocess.run(["bash", INC, f], capture_output=True, text=True).stdout
    rows = {}
    for line in out.splitlines():
        m = re.match(r"\s+(FAIL|ok|warn|--)\s+(\S+)\s+(.*)$", line)
        if m:
            rows.setdefault(m.group(2), []).append((m.group(1), m.group(3).strip()))
    return rows


bad = 0
for book in ("book-1", "book-2"):
    B = "C:/Users/screa/incunabula/test-books/validation-series/%s/manuscript/chapters/" % book
    for f in sorted(glob.glob(B + "chapter-*.md")):
        t = L.load(f)
        name = os.path.basename(f)
        nw = L.words(t)
        mine = {}
        a25 = list(L.A25.finditer(t))
        if len(a25) * 2000 > 3 * nw:
            mine["A25"] = "FAIL %d hits" % len(a25)
        a6 = list(L.A6.finditer(t))
        if len(a6) * 1000 > 2 * nw:
            mine["A6"] = "FAIL %d hits" % len(a6)
        key, n, nsent = L.top_opener(t)
        share = 100.0 * n / max(1, nsent)
        if n * 1000 > 6 * nw or share > 15.0:
            mine["P1"] = 'FAIL "%s" x%d of %d (%.1f%%)' % (key, n, nsent, share)

        rows = gate_rows(f)
        theirs = {}
        for rid, entries in rows.items():
            if any(s == "FAIL" for s, _ in entries):
                theirs[rid] = "FAIL " + entries[0][1][:56]
            elif rid in ("P1", "A25", "A6"):
                theirs[rid] = "ok   " + entries[0][1][:56]

        gate_fails = set(k for k, v in theirs.items() if v.startswith("FAIL"))
        if set(mine) != gate_fails:
            bad += 1
            print("\n%s  <-- DIVERGENCE" % name)
            print("   mine  : %s" % (mine or "no failures"))
            print("   gate  : %s" % ({k: v for k, v in theirs.items()
                                     if v.startswith("FAIL")} or "no failures"))
            for rid in ("A25", "A6", "P1"):
                if rid in rows:
                    print("   gate %-4s: %s" % (rid, rows[rid][0][1][:70]))
            if rid in ("P1",) and rid in rows:
                key2, n2, ns2 = L.top_opener(t)
                print("   mine P1  : nsent=%d top=%r x%d  words=%d" % (nsent, key2, n2, nw))

print("\n%d divergences" % bad)
