#!/usr/bin/env python3
"""check-figurative.py - are two images fighting over one referent?

WHY THIS EXISTS
  The manuscript's greatest strength - sensory density - has a failure mode no scanner
  in this directory can see: a figurative pile-up. "Like chewing on copper foil while
  someone struck a bronze bell inside her sinuses" is two good images competing for one
  sensation. `deslop-check.sh` catches anaphora, duplication and fragment runs - surface
  patterns. Metaphor stacking is SEMANTIC: multiple figurative constructions attached to
  one sensation within a short window.

  So this reports. It counts figurative constructions (similes and `as if`/`as though`
  framings) per sentence and per 50-word window, and prints the passages where they
  cluster, with context, for a reader to judge.

WHY IT REPORTS AND NEVER GATES
  The directory's rule: a rule may be zero-tolerance only if published prose never does
  it; everything else gets a density cap derived from a named corpus; and no threshold
  is ever set from an unmeasured number. There is no corpus measurement of figurative
  constructions per referent, and this detector cannot even see a referent - it sees
  windows. Every number below is therefore an OBSERVATION. The 50-word window and the
  2-per-sentence / 3-per-window listing lines are listing parameters, not caps, and they
  say so on every run. Nothing here can fail a book.

  The authority for figurative pile-ups is the evaluator rubric - proof-panel's Critic
  ("flag any passage where two images compete for one sensation") and the read-aloud
  pass. This tool is the cheap first look that points the reader at the right windows.

WHAT IT CANNOT DO
  It cannot see a metaphor without a marker ("the bronze bell in her sinuses" is
  figurative and invisible here). It cannot tell one rich image from two fighting ones -
  a dense passage of good prose will light this up. It counts `like` in comparisons that
  are not figurative ("something like four hundred meters"). A hit is a question, not a
  finding. Its unit is the window, so it cannot attribute an image to a referent; the
  two-images-one-sensation judgment stays human, which is why this never exits non-zero
  for content.

ROWS (all report-only; the tool exits 0 on any content)
  G1  sentences carrying 2+ image units (a marker plus each coordinated clause
      of two words or more inside its complement counts as a separate unit)
  G2  50-word windows carrying 3+ image units

EXIT CODES
  0  ran and reported (findings or not - findings are never a failure here)
  1  nothing checkable: a report from an empty read proves nothing

usage:  tools/prose/check-figurative.py [BOOK_DIR_OR_CHAPTER_DIR ...]
"""

import glob
import os
import re
import sys

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)
WINDOW = 50          # listing parameter, not a cap
G1_LIST, G2_LIST = 2, 3   # listing parameters, not caps

# The same sentence splitter as check-arc.py, so the units stay comparable.
SENT_RE = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[\"'(\[]*[A-Z0-9])")
ABBREV = re.compile(
    r"\b(?:Mr|Mrs|Ms|Dr|Prof|St|Sir|Lord|Lady|Capt|Col|Gen|Rev|Hon|Sgt|Lt|"
    r"vs|etc|i\.e|e\.g|No|Vol|pp|Fig|Jr|Sr|Esq)\.", re.I)

# Figurative markers: similes (`like a struck bell`), hypothetical framings
# (`as if`, `as though`), and the equative `as X as Y`. Deliberately marker-based:
# this tool sees constructions, not meaning, and says so in the docstring.
SIMILE = re.compile(r"\blike\b", re.I)
AS_IF = re.compile(r"\bas (?:if|though)\b", re.I)
AS_AS = re.compile(r"\bas\s+\w+\s+as\b", re.I)
# One construction can carry SEVERAL images: "like chewing on copper foil while
# someone struck a bronze bell inside her sinuses" is one `like` governing two
# images in competition - the canonical failure this tool exists for, and the
# first version missed it by counting markers (there is only one). Coordinated
# clauses inside a complement are counted as separate image units.
CLAUSE_SPLIT = re.compile(r"\b(?:while|and|as|but|then|though|than)\b", re.I)
SENT_END = re.compile(r"[.!?]")


def _complement_units(text, end):
    """Image units inside one marker's complement: the head plus each coordinated
    clause of two words or more. Clauses that contain another marker are left to
    that marker's own count, so nested constructions are not counted twice."""
    tail = text[end:]
    stop = SENT_END.search(tail)
    if stop:
        tail = tail[:stop.start()]
    head_count = 0
    for clause in CLAUSE_SPLIT.split(tail):
        if len(clause.split()) < 2:
            continue
        if SIMILE.search(clause) or AS_IF.search(clause) or AS_AS.search(clause):
            continue
        head_count += 1
    return max(0, head_count - 1)   # the head clause is already the marker's 1


def markers(text):
    total = 0
    for rx in (SIMILE, AS_IF):
        for m in rx.finditer(text):
            total += 1 + _complement_units(text, m.end())
    total += len(AS_AS.findall(text))
    return total


def sentences(text):
    t = ABBREV.sub(lambda m: m.group(0)[:-1], text)
    t = re.sub(r"\s+", " ", t)
    return [s.strip() for s in SENT_RE.split(t) if s.strip()]


def load(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if CHAPTER.search(name):
            with open(os.path.join(directory, name), encoding="utf-8", errors="ignore") as fh:
                out.append((name, fh.read()))
    return out


def resolve(arg):
    for candidate in (arg, os.path.join(arg, "manuscript"), os.path.join(arg, "manuscript", "chapters")):
        if os.path.isdir(candidate) and any(CHAPTER.search(n) for n in os.listdir(candidate)):
            return candidate
    return None


def clip(s, n=110):
    return s if len(s) <= n else s[:n - 1] + "\u2026"


def check(label, chapters):
    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters")
    print("=" * 67)
    hits = 0
    for name, text in chapters:
        sents = sentences(text)
        words = text.split()
        file_g1 = []
        for s in sents:
            n = markers(s)
            if n >= G1_LIST:
                file_g1.append((n, s))
        # sliding word window across sentence boundaries
        file_g2 = []
        toks = [(len(s.split()), s) for s in sents]
        i = 0
        while i < len(toks):
            total, buf, j = 0, [], i
            while j < len(toks) and total < WINDOW:
                total += toks[j][0]
                buf.append(toks[j][1])
                j += 1
            joined = " ".join(buf)
            n = markers(joined)
            if n >= G2_LIST and len(buf) > 1:
                file_g2.append((n, joined))
            i += 1
        if file_g1 or file_g2:
            print(f"\n--- {name}   {len(words)} words")
            for n, s in file_g1:
                print(f"   --   G1  {n} image units in one sentence:")
                print(f"          {clip(s)!r}")
                hits += 1
            for n, s in file_g2:
                print(f"   --   G2  {n} image units in one {WINDOW}-word window:")
                print(f"          {clip(s)!r}")
                hits += 1
    print()
    if not hits:
        print("   --   G1/G2  no cluster reached the listing lines in this book.")
    else:
        print(f"   --   {hits} passage(s) listed. These are OBSERVATIONS, not findings.")
    print()
    print("  REPORT-ONLY. There is no corpus measurement of figurative constructions")
    print("  per referent, so no cap exists and none is invented. The listing lines")
    print(f"  ({G1_LIST}+ image units per sentence, {G2_LIST}+ per {WINDOW}-word window) are")
    print("  parameters for what gets printed, not thresholds for what is wrong.")
    print("  A hit means: read this passage aloud. Sometimes the answer is that the")
    print("  passage is dense and good. The rubric that can fail it - 'two images")
    print("  competing for one sensation' - lives in proof-panel, where a reader, not")
    print("  a regex, can see the referent.")
    return 0


def main():
    args = sys.argv[1:]
    targets = []
    if args:
        for arg in args:
            directory = resolve(arg)
            if not directory:
                print(f"check-figurative: no chapters found under {arg}")
                return 1
            targets.append((arg, directory))
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for directory in sorted(glob.glob(os.path.join(root, "*", "manuscript", "chapters"))):
            targets.append((os.path.basename(os.path.dirname(os.path.dirname(directory))),
                            directory))

    checked = 0
    for label, directory in targets:
        chapters = load(directory)
        if not chapters:
            continue
        checked += 1
        check(label, chapters)
        print()

    if checked == 0:
        print("check-figurative: nothing checkable - an empty read reports nothing.")
        return 1
    print(f"FIGURATIVE REPORT DONE - {checked} manuscript(s) read. Report rows cannot fail.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
