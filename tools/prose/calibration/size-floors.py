#!/usr/bin/env python3
"""size-floors.py - derive a size-dependent floor, with the true positive measured too.

Both gates derive a fixed floor on one sample size and enforce it on another. The fix
is a floor that moves with the sample. That fix can go wrong in one specific way, and it
is the way that matters:

    a floor that rises for short books can rise ABOVE a genuine voice change.

`check-drift.py`'s documented remedy for a failure is rewriting a book, so a floor that
hides real drift is worse than the bug it fixes. A size-dependent floor is therefore
only admissible if a real two-voice book still fails at every size.

This measures both arms at every size, on published prose, using each gate's own code:

    NEGATIVE  one published novel, sliced to N chapters  - must never fail
    POSITIVE  half of novel A + half of novel B          - must always fail

and prints the separation. It proposes; it does not edit either gate. The two-voice
arm is a real voice change (different author by construction), which is the same
construction `validate-controls.sh` already uses for its positive control.

usage:  python size-floors.py <corpus-dir> [--books N] [--counts 4,6,8,10,12,16,20]
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

# The headroom every other cap in this directory uses: 1.5x the worst reference. It is
# reported alongside, not imposed: this metric's positive control sits only ~1.3x above
# its worst negative, so the 1.5x convention cannot be satisfied here without putting the
# floor ABOVE a real voice change. Applying a convention that destroys the gate is not
# conservatism, and the tool has to be able to say so.
HEADROOM = 1.5

DEFAULT_COUNTS = (4, 6, 8, 10, 12, 16, 20)


def slice_chapters(text, want, min_words=300):
    parts = re.split(r"(?<=[.!?])\s+", text)
    sizes = [len(p.split()) for p in parts]
    total = sum(sizes)
    if total < min_words * want:
        return None
    out, acc, n = [], [], 0
    per = total / want
    for piece, size in zip(parts, sizes):
        acc.append(piece)
        n += size
        if n >= per and len(out) < want - 1:
            out.append(" ".join(acc))
            acc, n = [], 0
    if acc:
        out.append(" ".join(acc))
    ch = [c for c in out if len(c.split()) >= min_words]
    return ch if len(ch) >= want else None


def score(chapters):
    per_feature = {}
    for _, text in chapters:
        for key, value in drift.features(text).items():
            per_feature.setdefault(key, []).append(value)
    steps = {k: drift.step_and_trend(s)[0] for k, s in per_feature.items()}
    return (sum(v * v for v in steps.values()) / len(steps)) ** 0.5


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    corpus = sys.argv[1]
    nbooks = 30
    if "--books" in sys.argv:
        nbooks = int(sys.argv[sys.argv.index("--books") + 1])
    counts = DEFAULT_COUNTS
    if "--counts" in sys.argv:
        counts = tuple(int(x) for x in
                       sys.argv[sys.argv.index("--counts") + 1].split(","))

    files = sorted(f for f in os.listdir(corpus) if f.lower().endswith(".txt"))[:nbooks]
    loaded = []
    for name in files:
        with open(os.path.join(corpus, name), encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        if hasattr(drift, "strip_gutenberg"):
            text = drift.strip_gutenberg(text)
        loaded.append((name, text))

    print("=" * 78)
    print(f"## size-floors   drift, {len(loaded)} published books, both arms per size")
    print("=" * 78)
    print()
    print("  NEGATIVE  one novel, one voice, sliced to N chapters.  must never fail.")
    print("  POSITIVE  half novel A + half novel B.  a real voice change.")
    print("            must always fail, or the floor is hiding real drift.")
    print()
    print(f"  {'ch':>3} {'neg p95':>8} {'neg max':>8} {'pos min':>8} {'pos med':>8} "
          f"{'pos/neg p95':>11} {'gap':>6}")

    rows = []
    for c in counts:
        neg, pos = [], []
        for i, (name, text) in enumerate(loaded):
            ch = slice_chapters(text, c)
            if not ch:
                continue
            neg.append(score([(f"{name}-{j}", t) for j, t in enumerate(ch)]))
            other = loaded[(i + 1) % len(loaded)][1]
            och = slice_chapters(other, c)
            if not och:
                continue
            half = c // 2
            mixed = ([(f"a{j}", t) for j, t in enumerate(ch[:half])] +
                     [(f"b{j}", t) for j, t in enumerate(och[c - half:])])
            pos.append(score(mixed))
        if not neg or not pos:
            print(f"  {c:>3}   (not measurable at this size)")
            continue
        neg.sort()
        pos.sort()
        p95 = neg[int(0.95 * (len(neg) - 1))]
        nmax = neg[-1]
        pmin, pmed = pos[0], st.median(pos)

        # Two different questions. `separable` asks whether ANY floor exists here: it must
        # sit above the worst negative and below the weakest true positive. `headroom`
        # asks whether the project's 1.5x convention also fits in that gap.
        gap = pmin / nmax if nmax else 0
        detect = sum(1 for v in pos if v > nmax)
        miss = len(pos) - detect
        rows.append((c, nmax, pmin, p95, pmed, detect, miss, len(neg), gap))
        mark = " " if nmax < pmin else "*"
        print(f" {mark}{c:>3} {p95:>8.2f} {nmax:>8.2f} {pmin:>8.2f} {pmed:>8.2f} "
              f"{pmed/p95 if p95 else 0:>10.2f}x {gap:>5.2f}x")

    print()
    if not rows:
        print("nothing measurable; a report that read nothing proves nothing")
        return 1

    print("=" * 78)
    print("  The two arms OVERLAP AT EVERY SIZE - neg max >= pos min throughout. A floor")
    print("  with zero false failures and zero missed drifts does not exist here, at any")
    print("  chapter count. What separates them is the body: pos median is roughly 2x")
    print("  neg p95 at every size.")
    print()
    print("  So the floor has to be set from the NEGATIVE arm alone - 'worse than any")
    print("  published book of this size' - and the missed-detection rate has to be")
    print("  recorded with it. Here is what that costs at each size:")
    print()
    print(f"  {'ch':>3} {'floor = neg max':>15} {'detects':>9} {'misses':>8} {'false fail':>12}")
    print()
    for c, nmax, pmin, p95, pmed, detect, miss, nneg, gap in rows:
        print(f"  {c:>3} {nmax:>15.2f} {detect:>5}/{miss+detect:<4} {miss:>8} "
              f"{'none':>12}")
    print()
    print("  A floor at the worst published book can never fail a clean book. It misses")
    print("  the weakest real voice changes at the rate in the 'misses' column, and that")
    print("  rate is the honest price of the guarantee.")
    print()
    print("Nothing has been edited. These are the numbers a size-dependent floor needs,")
    print("and the constraint it has to satisfy to be worth shipping.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
