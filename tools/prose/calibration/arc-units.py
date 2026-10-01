#!/usr/bin/env python3
"""arc-units.py - is A1's floor derived on the unit it is enforced on?

`check-arc.py` computes the arc PER 4,000-WORD WINDOW and then takes the **mean over
windows**, and A1's floor (0.45) comes from the distribution of those means across
140 published novels - a mean over roughly 15 windows each.

A book with one or two windows is not the same measurement. The per-window values
scatter much more widely than the per-novel means do, so a short book can land under a
floor that no published *novel* has ever landed under. This is the same class of error
as the density caps: a threshold derived on an average, enforced on a single sample.

It measures the per-window distribution directly on the published corpus, using
check-arc.py's own POSITIVE/NEGATIVE lexicons, sentence splitter, window() and shape()
so the numbers cannot disagree with the gate.

usage:  python arc-units.py <corpus-dir-of-txt> [--max N]
"""

import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# The gate's module name is hyphenated, so it cannot be imported by name. Load it from
# its path with importlib rather than re-implementing its lexicons here: a copy would
# be free to drift, and a drifted copy measures something the gate does not measure.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "check_arc",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "check-arc.py"))
arc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(arc)

TURN_FAIL, TURN_WARN = arc.TURN_FAIL, arc.TURN_WARN
NULL = arc.RANDOM_WALK_NULL


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    corpus = sys.argv[1]
    limit = 40
    if "--max" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--max") + 1])

    files = sorted(f for f in os.listdir(corpus) if f.lower().endswith(".txt"))[:limit]

    per_novel = []      # (name, mean-over-windows, n_windows, min_window, max_window)
    all_windows = []
    unmeasurable = 0

    for name in files:
        with open(os.path.join(corpus, name), encoding="utf-8", errors="ignore") as fh:
            text = arc.strip_gutenberg(fh.read())
        wins = arc.windows(text)
        vals = []
        for w in wins:
            s = arc.shape(arc.curve(arc.sentences(w)))
            if s:
                vals.append(s["turns"])
        if not vals:
            unmeasurable += 1
            continue
        per_novel.append((name, st.mean(vals), len(vals), min(vals), max(vals)))
        all_windows.extend(vals)

    if not per_novel:
        print("no measurable text. A report that read nothing proves nothing.")
        return 1

    print("=" * 78)
    print(f"## arc-units   {len(per_novel)} published novels, {len(all_windows)} windows")
    print("=" * 78)
    print()
    print("A1's floor is derived from the MEAN over windows, per novel. It is enforced")
    print("on a book, which may contribute a single window. Those are not the same")
    print("quantity, and the gap between them is what this measures.")
    print()

    m = [r[1] for r in per_novel]
    w = all_windows
    print(f"  {'':<18}{'mean':>8}{'sd':>8}{'min':>8}{'p25':>8}{'median':>8}{'max':>8}")
    for label, xs in (("per-NOVEL mean", m), ("per-WINDOW", w)):
        xs = sorted(xs)
        q = lambda p: xs[int(p * (len(xs) - 1))]
        print(f"  {label:<18}{st.mean(xs):>8.3f}{st.pstdev(xs):>8.3f}"
              f"{xs[0]:>8.3f}{q(.25):>8.3f}{q(.5):>8.3f}{xs[-1]:>8.3f}")

    nmin = min(m)
    wmin = min(w)
    print()
    print(f"  floor A1_FAIL   {TURN_FAIL:.3f}")
    print(f"  warn  A1_WARN   {TURN_WARN:.3f}")
    print(f"  null            {NULL:.3f}")
    print()
    print(f"  worst per-NOVEL mean   {nmin:.3f}   -> headroom under the floor: "
          f"{nmin - TURN_FAIL:+.3f}")
    print(f"  worst per-WINDOW       {wmin:.3f}   -> headroom under the floor: "
          f"{wmin - TURN_FAIL:+.3f}")

    below = [v for v in w if v < TURN_FAIL]
    warn_band = [v for v in w if TURN_FAIL <= v < TURN_WARN]
    print()
    print(f"  individual windows below the FAIL floor : {len(below)} of {len(w)} "
          f"({100*len(below)/len(w):.1f}%)")
    print(f"  individual windows in the WARN band      : {len(warn_band)} of {len(w)} "
          f"({100*len(warn_band)/len(w):.1f}%)")
    print(f"  novels whose MEAN is below the floor    : "
          f"{sum(1 for v in m if v < TURN_FAIL)} of {len(m)}")

    # A short book is one or two windows. How likely is such a book to fail?
    print()
    print("  A BOOK, sampled as a single window (a short serial, a one-window draft):")
    for k in (1, 2, 3, 5, 10):
        xs = sorted(w)
        picks = [xs[int(i * len(xs) / max(k, 1))] for i in range(k)]
        # worst case and typical case at this many windows
        print(f"    {k:>2} window(s):  median-of-{k} ~ {st.median(picks):.3f}"
              f"   -> {'FAILS' if st.median(picks) < TURN_FAIL else 'clears'}"
              f" the floor on its own")

    nw = [r[2] for r in per_novel]
    print()
    print(f"  windows per novel in this corpus: min {min(nw)}, median "
          f"{st.median(nw):.0f}, max {max(nw)}")
    print(f"  novels measured at all: {len(per_novel)}; unmeasurable: {unmeasurable}")
    print()
    print("=" * 78)
    if min(w) < TURN_FAIL:
        print(f"The floor sits {TURN_FAIL - wmin:.3f} above the worst single window, so a")
        print("short book can fail A1 while no published novel can. That is the same")
        print("unit error the density caps have, in the opposite direction.")
    else:
        print("The floor sits below the worst single window too, so short books clear it")
        print("as well as long ones. No unit error here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
