# Did fixing the tic re-clump the books?
#
# This is the actual test of DRAFTING_FRAMEWORK.md. The claim is that chapters are not
# SIZED, they END - so a book with no length targets should still show a wide spread
# after a prose repair. If the spread collapsed, then the old spread was coming from
# targets rather than from content, and the framework's premise is wrong.
#
# Baseline before the rewrite, measured on the same instrument:
#   Merope 1   478 - 2304   4.8x   CV 40.9%
#   Merope 2   519 - 2406   4.6x   CV 40.0%
#   The Trick  1460 - 3442  2.4x   CV 23.7%   <- the book that HAD targets
#
# Word count is the gate's own (wc -w over the normalised file), so the number here is
# the one the gates use, not a Python approximation of it.

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
import glob, io, os, statistics as st, subprocess

BOOKS = [
    ("Merope 1", REPO + "/test-books/validation-series/book-1/manuscript/chapters", 478, 2304, 40.9),
    ("Merope 2", REPO + "/test-books/validation-series/book-2/manuscript/chapters", 519, 2406, 40.0),
    ("The Trick", REPO + "/test-books/demo-magician/manuscript/chapters", 1460, 3442, 23.7),
]

print("%-11s %6s %6s %7s %7s  %-15s %-15s %s"
      % ("book", "ch", "total", "min", "max", "range (before)", "CV (before)", "now"))
for name, path, b_lo, b_hi, b_cv in BOOKS:
    counts = []
    for f in sorted(glob.glob(path + "/chapter-*.md")):
        # wc -w counts whitespace-delimited runs, so bytes.split() is the same count.
        # (Piping through tr returned empty on this platform, which is why this is
        # done in Python - a measurement that silently returns 0 is worse than none.)
        data = io.open(f, "rb").read().replace(b"\r", b"")
        counts.append(len(data.split()))
    lo, hi = min(counts), max(counts)
    ratio = hi / lo
    cv = 100.0 * st.pstdev(counts) / st.mean(counts)
    print("%-11s %6d %6d %7d %7d  %4d-%-4d %4.1f%%   %4d-%-4d  %.1fx  CV %.1f%%  (was %.1fx, CV %.1f%%)"
          % (name, len(counts), sum(counts), lo, hi, b_lo, b_hi, b_cv,
             lo, hi, ratio, cv, b_hi / b_lo, b_cv))
    print("            %s" % " ".join(str(c) for c in counts))
    gaps = [b - a for a, b in zip(counts, counts[1:])]
    print("            gaps: %s" % " ".join(str(g) for g in gaps))
