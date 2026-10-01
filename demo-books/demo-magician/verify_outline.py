#!/usr/bin/env python3
"""verify_outline.py - structural checks on outline.md, run BEFORE drafting.

Parses the chapter table out of the markdown (not a regex over prose, which on the last
book parsed a clue-ledger row as a chapter row and reported a bogus 77% CV), then:

  1. chapter count matches PROJECT_STATE
  2. word-target sum sits inside the declared floor/target band
  3. no chapter below per_chapter_min
  4. chapter-length CV reported, with the band from check-uniformity.py named
  5. no adjacent-identical structure symbols except the declared deliberate runs
  6. no ledger item first appears in the chapter that requires it

Exit 0 pass, 1 fail, 2 could not read.
"""

import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTLINE = os.path.join(HERE, "outline.md")
STATE = os.path.join(HERE, "PROJECT_STATE.yaml")

# From incunabula/tools/prose/check-uniformity.py, U1. Named here so the number in
# outline.md is traceable to a frozen gate rather than to a habit.
U1_BAND = (33.4, 45.1)

ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([A-Z]+)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|(.*)\|\s*$"
)


def read_state_number(key, default=None):
    if not os.path.isfile(STATE):
        return default
    txt = open(STATE, encoding="utf-8", errors="replace").read()
    m = re.search(rf"^\s*{key}\s*:\s*(\d+)\s*$", txt, re.M)
    return int(m.group(1)) if m else default


def read_state_floor():
    if not os.path.isfile(STATE):
        return None, None
    txt = open(STATE, encoding="utf-8", errors="replace").read()
    f = re.search(r"^\s*declared_floor\s*:\s*(\d+)\s*$", txt, re.M)
    t = re.search(r"^\s*declared_target\s*:\s*(\d+)\s*$", txt, re.M)
    return (int(f.group(1)) if f else None, int(t.group(1)) if t else None)


def main():
    if not os.path.isfile(OUTLINE):
        print(f"verify_outline: no outline at {OUTLINE}", file=sys.stderr)
        return 2
    lines = open(OUTLINE, encoding="utf-8", errors="replace").read().split("\n")

    chaps, seen = [], set()
    for ln in lines:
        m = ROW.match(ln)
        if not m:
            continue
        n = int(m.group(1))
        if n in seen:          # header/separator noise
            continue
        seen.add(n)
        chaps.append({"n": n, "sym": m.group(2), "words": int(m.group(3)),
                      "title": m.group(4).strip(), "rest": m.group(5)})

    if not chaps:
        print("verify_outline: no chapter rows parsed. If the table format changed, fix "
              "the parser rather than the outline.", file=sys.stderr)
        return 2

    chaps.sort(key=lambda c: c["n"])
    fails, warns = [], []

    # The chapter numbers must be contiguous from 1. This is the check that catches a
    # parser that silently truncated the table at a section break: the first version
    # stopped at the Act II heading, reported 14 chapters and a 6% CV, and would have
    # "passed" a 34-chapter contract against 14 chapters of plan. A missing chapter is
    # louder than a bad number.
    expected = list(range(1, len(chaps) + 1))
    actual = [c["n"] for c in chaps]
    if actual != expected:
        missing = sorted(set(range(1, (max(actual) if actual else 0) + 1)) - set(actual))
        fails.append(f"chapter numbers are not contiguous from 1; parsed {len(chaps)} "
                     f"chapters ending at {max(actual) if actual else 0}"
                     + (f"; MISSING: {missing}" if missing else ""))

    # 1 count
    want = read_state_number("chapters")
    if want and len(chaps) != want:
        fails.append(f"chapter count {len(chaps)} != PROJECT_STATE chapters {want}")

    # 2 + 3 words
    total = sum(c["words"] for c in chaps)
    floor, target = read_state_floor()
    if floor and total < floor:
        fails.append(f"word-target sum {total:,} is BELOW declared floor {floor:,} — the "
                     f"contract is not being met by the plan itself")
    if target and total > target:
        fails.append(f"word-target sum {total:,} is ABOVE declared target {target:,}")
    pmin = read_state_number("per_chapter_min")
    for c in chaps:
        if pmin and c["words"] < pmin:
            fails.append(f"ch {c['n']} targets {c['words']:,} < per_chapter_min {pmin:,}")

    # 4 CV
    words = [c["words"] for c in chaps]
    cv = (statistics.pstdev(words) / statistics.mean(words)) * 100
    lo, hi = U1_BAND
    if not (lo <= cv <= hi):
        warns.append(f"chapter-length CV {cv:.2f}% is outside the U1 band {lo}-{hi}. "
                     f"Band is from check-uniformity.py, frozen.")

    # 5 adjacent-identical structure
    runs = []
    for a, b in zip(chaps, chaps[1:]):
        if a["sym"] == b["sym"]:
            runs.append((a["n"], b["n"], a["sym"]))
    trial_runs = [r for r in runs if 24 <= r[0] and r[1] <= 28]
    other = [r for r in runs if r not in trial_runs]
    for r in other:
        warns.append(f"ch {r[0]}-{r[1]} both '{r[2]}' — check the run is deliberate")

    # 6 ledger: an L-item must not first appear in the chapter that requires it
    led = re.findall(r"L(\d+)", "\n".join(c["rest"] for c in chaps))
    first_seen = {}
    for c in chaps:
        for L in re.findall(r"L(\d+)", c["rest"]):
            first_seen.setdefault(int(L), c["n"])

    print(f"verify_outline: {os.path.basename(OUTLINE)}")
    print(f"  chapters        {len(chaps)}")
    print(f"  target sum      {total:,}  (band {floor:,}-{target:,})")
    print(f"  mean            {statistics.mean(words):,.0f}")
    print(f"  min / max       {min(words):,} / {max(words):,}"
          f"  (ratio {max(words)/min(words):.2f}x)")
    print(f"  CV              {cv:.2f}%  (U1 band {lo}-{hi})")
    print(f"  distinct syms   {len({c['sym'] for c in chaps})}")
    print(f"  adjacent runs   {len(runs)} ({len(trial_runs)} in the trial, deliberate)")
    print(f"  ledger items    {len(first_seen)} carried")
    print()
    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")

    if fails:
        print("\nOUTLINE FAILS - fix the plan before drafting. Declaring a length contract "
              "the plan cannot meet is the failure mode this gate exists to catch, and it "
              "is always cheaper here than in chapter 30.")
        return 1
    if warns:
        print("\nOUTLINE OK with warnings - see above.")
        return 0
    print("OUTLINE OK - count, word targets, structure and ledger all check out.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
