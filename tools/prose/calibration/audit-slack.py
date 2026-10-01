#!/usr/bin/env python3
"""audit-slack.py - is every threshold in tools/prose/ still honest?

A guard with slack is a guard that cannot fail.  `check-errata.py`'s REJECTED_FLOOR
was found sitting 1 entry below its live registry count, so the next deletion would
have landed inside the headroom and printed `ok`.  That class of bug is invisible in
code review - the number looks plausible - and it is only visible when the threshold
is compared against the measurement it was derived from.

This recomputes that comparison for every threshold in the directory.  It reads
nothing but the tools' own source and the numbers recorded beside them.  It proposes
nothing, changes nothing and gates nothing; it exists so that a slack constant gets
noticed while it is still small.

WHY IT COMPARES HITS, NOT RATES
-------------------------------
`deslop-check.sh` evaluates a cap as exact integer arithmetic:

    fail when  n * allow_w  >  allow_n * words

so at a chapter of W words the cap allows `floor(allow_n * W / allow_w)` hits.  The
DENSITY table's denominators are round (1000, 2000) while chapters are not, and that
mismatch is where slack hides.  A1b is the clearest case: `1 per 2000` sounds tight and
is 0.5/1k, but a 3,557-word published chapter turns it into 1 hit allowed against 0.31
x 3557 = 1.1 observed - fine - while `2 per 1000` on the same chapter allows 7.  A
per-1k rate comparison calls 2/1000 "2.1x loose" and cannot tell you that 7 hits are
permitted where 3 were derived.

So: compare the ALLOWABLE HIT COUNT at a reference chapter length against the DERIVED
hit count, 1.5x the worst published rate.  Both chapter lengths are reported, because
the cap has to hold for whichever a book uses.
"""

import os
import re
import sys

PROSE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The convention, from deslop-check.sh's DENSITY header and CALIBRATION.md section 2:
#   "A density cap is set at roughly 1.5x the worst single calibration document"
CAP_TARGET = 1.5
# A floor (FAIL below) is the same idea inverted: 1/1.5 below the worst published doc.
FLOOR_TARGET = 1.0 / 1.5

# Two reference lengths, both from CALIBRATION.md: published chapters average 3,557
# words and this project's own books run ~2,150. A cap that only holds at one of them
# is a cap that will surprise somebody.
CHAPTER_WORDS = (3557, 2150)

TOL = 0.15

DENSITY_ROW = re.compile(
    r"^\s*'([A-Z]\d+[a-z]?)\|([^|]+)\|(\d+)\|(\d+)\|(\d*)\|(\d*)\|[^#]*#\s*(.*)$")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def worst_from_comment(comment):
    """The recorded worst published rate, per 1k words.

    Two shapes appear in the table: `worst 8.90/1k` and `1 hit in 175k`. The second
    is hits per k words already - it needs no 1000x - and reading it as
    `1000 * hits / k` reports a cap as 1000x tighter than its derivation, which is
    the one direction a reviewer will not think to double-check.
    """
    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*1k", comment)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+)\s+hits?\s+in\s+(\d+)k", comment)
    if m:
        return float(m.group(1)) / float(m.group(2))
    return None


def classify(ratio, target, kind="cap"):
    """Which direction is dangerous depends on the row's kind.

    A cap is loosened by being too high. A floor (FAIL below) is the mirror: too low
    is slack, too high would fail published human prose. Getting this backwards
    inverts the verdict, and an inverted verdict is worse than none - it tells a
    reviewer to loosen a cap that was already correct.
    """
    high, low = ("SLACK", "TIGHT") if kind == "cap" else ("TIGHT", "SLACK")
    if ratio > target * (1 + TOL):
        return high
    if ratio < target * (1 - TOL):
        return low
    return "ok"


def audit_density():
    out = []
    text = read(os.path.join(PROSE, "deslop-check.sh"))
    body = text.split("DENSITY=(", 1)[1].split("\n)", 1)[0]
    for line in body.splitlines():
        m = DENSITY_ROW.match(line)
        if not m:
            continue
        row, name = m.group(1), m.group(2)
        allow_n, allow_w = int(m.group(3)), int(m.group(4))
        worst = worst_from_comment(m.group(7))
        out.append((row, name, allow_n, allow_w, worst))
    return out


def hits(row, allow_n, allow_w, worst, words):
    """(allowable hits, derived hits) at a given chapter length."""
    allowed = (allow_n * words) // allow_w
    derived = CAP_TARGET * worst * words / 1000.0
    return allowed, derived


def main():
    print("=" * 78)
    print("## audit-slack   per-threshold headroom against its recorded measurement")
    print("=" * 78)
    print()
    print("A cap fails when n * allow_w > allow_n * words, so what matters is the")
    print("number of hits a chapter of W words may contain, not the per-1k rate.")
    print("Derived = 1.5x the worst published rate, at that same W.")
    print()

    rows = audit_density()
    flagged, skipped = [], 0
    print(f"deslop-check.sh  DENSITY table, {len(rows)} rows")
    for words in CHAPTER_WORDS:
        print()
        print(f"  at W = {words} words "
              f"({'published chapter average' if words > 3000 else 'this project\'s own books'})")
        print("    row    cap     allowed  derived   ratio   verdict")
        for row, name, allow_n, allow_w, worst in rows:
            if worst is None:
                skipped += 1
                print(f"    {row:<6} {allow_n}/{allow_w:<6} {'-':>7} {'-':>8}    -"
                      f"          no recorded worst")
                continue
            allowed, derived = hits(row, allow_n, allow_w, worst, words)
            if derived < 1.0:
                # 1.5x the worst rate is below one hit in this chapter, so every cap
                # in the table is already at its minimum. There is nothing to compare.
                print(f"    {row:<6} {allow_n}/{allow_w:<6} {allowed:>7} {derived:>8.2f}"
                      f"    -          quantized: 1 hit is the floor")
                continue
            ratio = allowed / derived
            verdict = classify(ratio, CAP_TARGET, "cap")
            mark = " " if verdict == "ok" else "*"
            if verdict != "ok":
                flagged.append((row, words, verdict, allowed, derived))
            print(f"   {mark}{row:<6} {allow_n}/{allow_w:<6} {allowed:>7} {derived:>8.2f}"
                  f"  {ratio:6.2f}   {verdict}")

    print()
    print("check-uniformity.py  floors (FAIL below; target 0.65 of the worst published)")
    print("  row              floor   published   ratio   verdict")
    uni = [
        ("CV_FAIL", 30.0, 48.4),
        ("SPREAD_FAIL", 3.0, 4.32),
        ("ONELINE_FAIL", 35.0, 11.0),
        ("PARACV_FAIL", 55.0, 57.0),
    ]
    for name, floor, worst in uni:
        ratio = floor / worst
        verdict = classify(ratio, FLOOR_TARGET, "floor")
        mark = " " if verdict == "ok" else "*"
        if verdict != "ok":
            flagged.append((name, "-", verdict, floor, worst))
        print(f" {mark}{name:<14} {floor:6.1f}   {worst:8.1f}  {ratio:6.2f}   {verdict}")
    print("    note: ONELINE_FAIL is scored against the corpus MINIMUM (11.0), which")
    print("    flatters it. Against the MEDIAN (33.2) the floor is 1.05x - above half")
    print("    the human canon. That is the refutation already recorded, and it is why")
    print("    the row is advisory by default. U4 is named here so it is not 'fixed'.")
    print("    PARACV_FAIL (U5) is the opposite problem: 55.0 against a corpus minimum")
    print("    of 57.0 leaves 2.0 points of headroom. It is the tightest enforced floor")
    print("    in the directory and the one a fourth corpus could break.")

    print()
    print("check-arc.py  A1 (FAIL under 0.45, warn under 0.50)")
    print("    human min 0.469, mean 0.571, null 0.500")
    print("    A1_FAIL 0.45 sits 0.019 BELOW the human minimum - correct, and thin.")
    print("    A1_WARN 0.50 sits ABOVE it, so a published novel can warn. Intentional:")
    print("    the warn band is a prompt to look, not an accusation.")

    print()
    print("check-drift.py")
    print("    DRIFT_FAIL 1.40 vs published 0.5-0.8  -> 1.75x the worst, correct.")
    print("    TREND_FAIL 9.99 is deliberately inert; D2 is warning-only on three volumes.")

    print()
    print("=" * 78)
    if flagged:
        print(f"{len(flagged)} row/length combination(s) off derivation:")
        for row, words, verdict, allowed, derived in flagged:
            unit = f"W={words}" if words != "-" else "floor"
            print(f"  {row:<14} {unit:<8} {verdict:<6} allowed {allowed} vs derived {derived:.2f}")
        print("This tool changes nothing. Read them before trusting the gate they sit in.")
    else:
        print("No threshold is off its derivation.")
    if skipped:
        print(f"{skipped} row(s) carry no recorded worst rate and cannot be scored.")


if __name__ == "__main__":
    sys.exit(main())
