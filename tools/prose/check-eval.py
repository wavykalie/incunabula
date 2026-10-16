#!/usr/bin/env python3
"""check-eval.py — score integrity is code, not self-policing. Hygiene, not a gate.

The anti-inflation rules were enforced by the scoring agent on itself: a number
could arrive with no citation, a floor could be an average in disguise, and a
revision could move a score half a point "because it improved". An honest
instrument applies the subtraction in code. This one reads the evaluation files
and checks the rules the evaluator protocol and the anti-inflation section
already state:

  1. CITE   every scored dimension cites a passage. A number with no citation
            is invalid (anti-inflation rule 2) and fails here.
  2. DELTA  no dimension moves more than +0.5 against the previous evaluation
            of the same chapter (rule 1) — unless the file carries an explicit
            EVIDENCE: block that names a passage (a quote or a location
            reference). The override is file-level, not per-dimension: that is
            a known coarseness, stated rather than hidden.
  3. FLOOR  the reported Incunabula Score equals the MINIMUM across the seven
            dimensions (the Platen). An arithmetic mismatch fails.
  4. CALIB  when the eval is self-scored (its provenance header says grade C /
            self-evaluation), the −0.8 self-evaluation calibration is applied
            HERE and printed as the calibrated floor. The agent never subtracts
            it from itself; rule 6 of the anti-inflation protocol is mechanical.

NOT A GATE and deliberately absent from GATE_FREEZE.md's manifest: same
exemption class as check-pass-evidence.py — it enforces rules that already
exist, reads no prose, and judges no manuscript. A FAIL here is bookkeeping
behind the scoring, never the prose being bad.

Files read: evaluations/eval-*.md and evaluations/*-evaluation.md under the
book root. BOTH naming conventions exist in this repository (the proof-pull
skill reads eval-chapter-[N].md; drafted books write chNN-evaluation.md), and a
checker that read only one would gate half the evaluations. Files are grouped by
chapter number (ch03, chapter-3, eval-chapter-3 …) and ordered oldest-first by
mtime within the group; the delta check compares consecutive evaluations of one
chapter — across different chapters there is no revision cycle to compare.

Usage:
    python tools/prose/check-eval.py <book-root>

Exit codes:
    0  every rule holds (the calibration line still prints when it applies)
    1  at least one violation: an uncited score, a delta breach without an
       EVIDENCE block, a floor that is not the minimum, or a score table that
       does not carry the seven dimensions
    2  no evaluation files under the book root — NOT RUN, never a pass
"""

import glob
import os
import re
import sys

EVAL_PATTERNS = ("eval-*.md", "*-evaluation.md")
CHAPTER = re.compile(r"(?:eval-)?(?:ch|chapter)[-_ ]?(\d+)", re.I)
ROW_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
FLOOR = re.compile(r"(?:\*\*Floor:?\s*|Incunabula Score:?\s*)([0-9]+(?:\.[0-9]+)?)", re.I)
EVIDENCE_BLOCK = re.compile(r"EVIDENCE:\s*(.*)", re.I)
SELF = re.compile(r"grade\s*C|self[- ](?:evaluation|scored|eval)", re.I)

# canonical dimension names, matched on a normalised cell
DIMS = (
    ("orig", "Originality"),
    ("theme", "Theme"),
    ("char", "Characters"),
    ("prose", "Prose and voice"),
    ("pac", "Pacing and coherence"),
    ("emotion", "Emotion"),
    ("config", "Configurable"),
)

# a citation is a quoted span or a location reference — anything else is a wish
QUOTE = re.compile(r"[\"“”«»‘’'].*[\"“”«»‘’']|\u201c|\u201d")
LOCATION = re.compile(
    r"\b(ch(?:apter)?\s*[-_]?\s*\d+|para(?:graph)?\s*\d+|line\s*\d+|p\.\s*\d+|:\d+)\b", re.I)


def fail(msg, failures):
    failures.append(msg)
    print("   FAIL  %s" % msg)


def ok(msg):
    print("   ok    %s" % msg)


def dim_name(cell):
    key = cell.strip().lower()
    for start, name in DIMS:
        if key.startswith(start):
            return name
    return None


def has_citation(cell):
    cell = cell.strip()
    if not cell:
        return False
    return bool(QUOTE.search(cell) or LOCATION.search(cell))


def chapter_key(path):
    m = CHAPTER.search(os.path.basename(path))
    return int(m.group(1)) if m else 0


def parse_file(path):
    """-> dict with dimensions {name: (score, evidence)}, floor, self_scored."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    dims = {}
    for line in text.splitlines():
        if "|" not in line or ROW_SEP.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        name = dim_name(cells[0])
        if name is None:
            continue
        try:
            score = float(cells[1])
        except ValueError:
            continue  # a header row ("Dimension | Score | Evidence") lands here
        evidence = " | ".join(cells[2:])
        dims[name] = (score, evidence)
    m = FLOOR.search(text)
    floor = float(m.group(1)) if m else None
    blocks = EVIDENCE_BLOCK.findall(text)
    qualifies = any(QUOTE.search(b) or LOCATION.search(b) for b in blocks)
    return {
        "dims": dims,
        "floor": floor,
        "self_scored": bool(SELF.search(text[:1200])),
        "evidence_block": qualifies,
    }


def check_file(path, failures):
    name = os.path.basename(path)
    print("---- %s" % name)
    data = parse_file(path)
    dims = data["dims"]
    if not dims:
        fail("%s: no score table with the seven dimensions - nothing checkable "
             "(a file in evaluations/ that is not an evaluation should not match "
             "the eval patterns)" % name, failures)
        return data

    # 1. CITE
    missing = [d for d, (_, ev) in sorted(dims.items()) if not has_citation(ev)]
    if missing:
        fail("%s: score(s) with no passage citation: %s - a number without a "
             "citation is invalid (anti-inflation rule 2)" % (name, ", ".join(missing)),
             failures)
    else:
        ok("every scored dimension cites a passage")

    # score table completeness: the floor is the minimum of SEVEN
    if len(dims) != 7:
        fail("%s: the table scores %d of the 7 dimensions - the Platen is the "
             "minimum across all seven" % (name, len(dims)), failures)

    # 3. FLOOR
    if data["floor"] is None:
        print("   --    %s: no reported floor - arithmetic NOT CHECKED" % name)
    else:
        real = min(s for s, _ in dims.values())
        if abs(real - data["floor"]) > 1e-9:
            fail("%s: reported floor %.1f is not the minimum of its dimensions "
                 "(%.1f) - the floor is the score, never an average" %
                 (name, data["floor"], real), failures)
        else:
            ok("reported floor %.1f is the minimum of the seven dimensions" % real)

    # 4. CALIB - the subtraction happens here, not in the agent's head
    real = min(s for s, _ in dims.values())
    if data["self_scored"]:
        print("   --    %s: SELF-SCORED (provenance header) - calibrated floor "
              "%.1f (raw minimum %.1f, minus the measured 0.8 self-eval bias)"
              % (name, real - 0.8, real))
    else:
        print("   --    %s: not self-scored on its face - no self-eval "
              "calibration applied" % name)
    print()
    return data


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    book = sys.argv[1]
    files = []
    for pat in EVAL_PATTERNS:
        files.extend(glob.glob(os.path.join(book, "evaluations", pat)))
    files = sorted(set(files))
    if not files:
        print("check-eval: no evaluation files under %s/evaluations - NOT RUN. "
              "Never a pass." % book)
        return 2

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(newline="\n")

    print("===================================================================")
    print("check-eval - score integrity against the anti-inflation protocol")
    print("book: %s   (%d evaluation file(s))" % (book, len(files)))
    print("===================================================================")
    failures = []

    # group by chapter; oldest first within each group (the revision cycle order)
    groups = {}
    for f in files:
        groups.setdefault(chapter_key(f), []).append(f)
    for key in sorted(groups):
        chain = sorted(groups[key], key=lambda p: (os.path.getmtime(p), p))
        label = "chapter %d" % key if key else "whole-book evaluations"
        print("== %s: %s" % (label, " -> ".join(os.path.basename(p) for p in chain)))
        prev = None
        for path in chain:
            data = check_file(path, failures)
            # 2. DELTA
            if prev is not None:
                for d in sorted(set(prev["dims"]) & set(data["dims"])):
                    before = prev["dims"][d][0]
                    after = data["dims"][d][0]
                    jump = after - before
                    if jump > 0.5 + 1e-9:
                        if data["evidence_block"]:
                            ok("%s moves %+.1f (over the +0.5 cap) but the file "
                               "carries an EVIDENCE: block naming a passage - "
                               "override accepted" % (d, jump))
                        else:
                            fail("%s moves %+.1f in one revision cycle with no "
                                 "EVIDENCE: block naming a passage - a larger "
                                 "jump must be justified with textual evidence"
                                 % (d, jump), failures)
            prev = data
        print()

    print("===================================================================")
    if failures:
        print("check-eval: FAIL - %d violation(s) of the anti-inflation rules." % len(failures))
        return 1
    print("check-eval OK - citations, deltas and floor arithmetic all hold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
