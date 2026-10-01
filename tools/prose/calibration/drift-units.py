#!/usr/bin/env python3
"""drift-units.py - does the drift step depend on how many chapters a book has?

`check-drift.py` splits a book in half **by chapter count** and takes the RMS Cohen's d
between the two halves. Its cap (1.40) was calibrated on three published volumes of 13,
17 and 18 chapters, and its own docstring already concedes the sample is too small for a
tight line.

The unit question is the same one the density caps got wrong, cutting the other way. A
step between two halves estimated from 3 chapters each is noisier than one estimated
from 8: the same underlying book reads higher purely by having fewer chapters. If that
holds, a fixed cap converts a small sample into an accusation of voice change - and the
remedy the docstring names is rewriting the book.

This runs the gate's OWN `check()` over published chapters at several chapter counts, so
the number reported is the number the gate computes, not a re-derivation of it. It
imports check-drift.py rather than copying its features, because a copy would be free to
drift from the thing it is auditing.

usage:  python drift-units.py <corpus-dir> [--max N] [--counts 4,6,8,12,16,20]
"""

import importlib.util
import os
import re
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_spec = importlib.util.spec_from_file_location(
    "check_drift",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "check-drift.py"))
drift = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drift)

FAIL, WARN = drift.DRIFT_FAIL, drift.DRIFT_WARN

# Chapter sizes to test. 4 is drift's own MIN_CHAPTERS; the rest bracket the 13/17/18
# the cap was calibrated on.
DEFAULT_COUNTS = (4, 6, 8, 10, 12, 16, 20)


def slice_chapters(text, want, min_words=300):
    """Split a novel into `want` roughly equal chapter-sized pieces.

    Deliberately blunt. Real chapter boundaries are not evenly spaced, but the question
    here is about sample size, and a uniform split holds the text fixed so the only
    thing varying between arms is how many chapters the step is estimated from.
    """
    pieces = re.split(r"(?<=[.!?])\s+", text)
    sizes = [len(p.split()) for p in pieces]
    total = sum(sizes)
    if total < min_words * want:
        return None
    out, acc, n = [], [], 0
    per = total / want
    for piece, size in zip(pieces, sizes):
        acc.append(piece)
        n += size
        if n >= per and len(out) < want - 1:
            out.append(" ".join(acc))
            acc, n = [], 0
    if acc:
        out.append(" ".join(acc))
    return [c for c in out if len(c.split()) >= min_words] or None


def score(chapters):
    """The gate's own arithmetic, without its printing."""
    per_feature = {}
    for _, text in chapters:
        for key, value in drift.features(text).items():
            per_feature.setdefault(key, []).append(value)
    steps = {key: drift.step_and_trend(series)[0]
             for key, series in per_feature.items()}
    return (sum(v * v for v in steps.values()) / len(steps)) ** 0.5


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    corpus = sys.argv[1]
    limit = 40
    if "--max" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--max") + 1])
    counts = DEFAULT_COUNTS
    if "--counts" in sys.argv:
        counts = tuple(int(x) for x in
                       sys.argv[sys.argv.index("--counts") + 1].split(","))

    files = sorted(f for f in os.listdir(corpus) if f.lower().endswith(".txt"))[:limit]
    results = {c: [] for c in counts}
    for name in files:
        with open(os.path.join(corpus, name), encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        if hasattr(drift, "strip_gutenberg"):
            text = drift.strip_gutenberg(text)
        words = len(text.split())
        for c in counts:
            ch = slice_chapters(text, c)
            if not ch or len(ch) < c:
                continue
            results[c].append(score([(f"{name}-ch{i}", t) for i, t in enumerate(ch)]))

    print("=" * 78)
    print(f"## drift-units   {len(files)} published books, sliced to fixed chapter counts")
    print("=" * 78)
    print()
    print(f"  DRIFT_FAIL {FAIL:.2f}   DRIFT_WARN {WARN:.2f}   (published 0.49-0.80)")
    print()
    print("  Same text, same author, same author-voice throughout. Only the number of")
    print("  chapters the half-to-half step is estimated from changes.")
    print()
    print("  chapters   n books   median    mean     max    over cap   over warn")
    for c in counts:
        xs = results[c]
        if not xs:
            continue
        over_f = sum(1 for v in xs if v > FAIL)
        over_w = sum(1 for v in xs if v > WARN)
        print(f"  {c:>8}   {len(xs):>7}   {st.median(xs):6.2f} {st.mean(xs):6.2f} "
              f"{max(xs):7.2f}   {over_f:>3} ({100*over_f/len(xs):4.1f}%)"
              f"   {over_w:>3} ({100*over_w/len(xs):4.1f}%)")

    usable = [(c, st.median(results[c])) for c in counts if len(results[c]) >= 3]
    if len(usable) >= 3:
        xs = [p[0] for p in usable]
        ys = [p[1] for p in usable]
        mx, my = st.mean(xs), st.mean(ys)
        num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** .5
        r = num / den if den else 0.0
        print()
        print(f"  correlation, chapter count vs median drift: r = {r:+.3f}")
        print("  A strongly NEGATIVE r is the unit error: fewer chapters, higher reading.")
        if len(usable) >= 2:
            lo, hi = usable[0], usable[-1]
            print(f"  {lo[0]} chapters -> {lo[1]:.2f}   vs   {hi[0]} chapters -> {hi[1]:.2f}"
                  f"   ({(hi[1] - lo[1]):+.2f})")
    print()
    print("=" * 78)
    print("Read: if the short-book arm sits materially higher, DRIFT_FAIL is calibrated")
    print("on 13-18 chapter volumes and applied to books with half that.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
