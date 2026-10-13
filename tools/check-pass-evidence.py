#!/usr/bin/env python3
"""check-pass-evidence.py — hygiene, not a gate.

A chapter-level pass (register, catchword, quoin, composing, proof-panel) that
leaves no artifact is a wish. This script checks that every chapter file has
its evidence file, and reports gated words (words in evidenced chapters) as
the progress number. It reads no prose and measures nothing.

Not a prose gate and deliberately absent from GATE_FREEZE.md's manifest:
same exemption class as init-book.py, check-registry.py, preflight.sh.
Make-ready layer. A FAIL here means the bookkeeping is behind the drafting,
never that the prose is bad.

Convention: manuscript/chapters/chapter-NN.md is evidenced by
evaluations/*chNN*pass*.md (e.g. evaluations/v2-ch01-passes.md).

check-registry.py imports evidence_report() from this file so that its
status-claim check and this check can never disagree about what "evidenced"
means. The convention lives HERE and nowhere else.

Usage:
    python tools/check-pass-evidence.py <book-root>

Exit codes:
    0  every chapter evidenced
    1  at least one chapter missing its evidence file
    2  no chapters found (nothing to check — never a pass)

Non-retroactivity: finished books keep their verdicts. A catalogue book without
pass files has a record-keeping gap, not a manuscript failure; this check governs
runs from its introduction forward and never re-judges a delivered book.
"""

import glob
import os
import re
import sys

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)", re.I)


def evidence_report(root):
    """The evidence state of one book. Single source of truth.

    Returns {"error": ...} when there is nothing to check (no chapters dir, or
    no chapter files), else {chapters, total_words, gated_words, missing} where
    missing is [(chapter-name, words), ...]. check-registry.py consumes exactly
    this structure to refuse a `complete`/`published` claim the files do not
    support, so the two checkers share one convention.
    """
    chdir = os.path.join(root, "manuscript", "chapters")
    evdir = os.path.join(root, "evaluations")
    try:
        names = sorted(os.listdir(chdir))
    except FileNotFoundError:
        return {"error": f"no manuscript/chapters under {root}"}
    chapters = [n for n in names if CHAPTER.search(n)]
    if not chapters:
        return {"error": f"no chapter files under {chdir} — nothing checked, nothing passed."}
    evfiles = []
    try:
        evfiles = os.listdir(evdir)
    except FileNotFoundError:
        pass
    missing = []
    gated_words = 0
    total_words = 0
    for n in chapters:
        num = CHAPTER.search(n).group(1)
        path = os.path.join(chdir, n)
        with open(path, encoding="utf-8", errors="ignore") as fh:
            words = len(fh.read().split())
        total_words += words
        ev = [e for e in evfiles
              if re.search(r"ch0*" + num + r"\b", e, re.I) and "pass" in e.lower()]
        if ev:
            gated_words += words
        else:
            missing.append((n, words))
    return {"chapters": len(chapters), "total_words": total_words,
            "gated_words": gated_words, "missing": missing}


def main():
    if len(sys.argv) != 2:
        print("usage: python tools/check-pass-evidence.py <book-root>")
        return 2
    root = sys.argv[1]
    rep = evidence_report(root)
    if "error" in rep:
        print(f"check-pass-evidence: {rep['error']}")
        return 2
    chapters = rep["chapters"]
    total_words = rep["total_words"]
    gated_words = rep["gated_words"]
    missing = rep["missing"]
    print(f"## check-pass-evidence   {root}")
    print(f"   chapters: {chapters}   gated words: {gated_words} / {total_words}")
    if missing:
        print("   MISSING evidence for:")
        for n, w in missing:
            print(f"     - {n} ({w} words) - draft without passes is quarry, not manuscript")
        print("   EVIDENCE FAIL - write the pass files; do not advance phases on claims.")
        return 1
    print("   EVIDENCE OK - every chapter carries its passes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
