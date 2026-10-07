#!/usr/bin/env python3
"""measure-pd-corpus.py - run U4/U5 over a public-domain novel corpus.

WHY THIS EXISTS
  U4 and U5 were calibrated on one dialogue-heavy translated light novel, and
  CALIBRATION.md records that as the corpus's main limitation. The re-labelling of U4 as
  a *market convention* rather than a law of prose needs evidence from a corpus of
  different register, era and length, and the obvious candidate was sitting in the
  repository: the 140 public-domain English novels that VERMILLION assembled, 13.04M
  words, 94 authors, five eras.

  CALIBRATION.md also records a failed earlier attempt at exactly this - three Gutenberg
  candidates "using a line-break format that makes paragraph structure unrecoverable".
  That diagnosis was wrong. The VERMILLION corpus files are blank-line separated and
  their paragraph structure is fully recoverable; what the three failed candidates had
  in common was a line-wrap format without blank lines between paragraphs, which is a
  different thing. This script is the evidence, and it is re-runnable.

  The measurement deliberately mirrors check-uniformity.py's own arithmetic rather than
  inventing its own: same paragraph splitter, same sentence splitter, same
  per-chapter-then-averaged aggregation. Whole-novel variance is a DIFFERENT quantity
  and mixing the two would produce a number that looks like corroboration and is not.

WHAT IT PRINTS
  The distribution of both rows across the corpus, and - the point of the exercise -
  how many human novels the current Incunabula thresholds would fail.

WHAT IT DOES NOT DO
  It does not propose thresholds. A 19th-century corpus is not the corpus this pipeline
  sells into, and re-deriving U4 from it would replace one convention with another. The
  era confound is large and runs in a known direction: paragraph-breaking practice
  changed across the twentieth century, and VERMILLION's period control shows human
  sentence length falling from 37.7 words pre-1830 to 15.9 post-1939. Later prose
  breaks more. Reading this output as "lower the U4 floor" would be the era confound
  arriving through the front door.

  usage:  python measure-pd-corpus.py <dir-of-.txt-novels> [--window 3000]
          defaults to the VERMILLION human corpus if no directory is given
"""

import os
import re
import sys
import glob
import statistics as st

# Incunabula's current floors, from check-uniformity.py.
ONELINE_FAIL, ONELINE_WARN = 35.0, 50.0
PARACV_FAIL, PARACV_WARN = 55.0, 75.0

# Absolute: incunabula moved out of the books workspace (2026-10-07), so no
# relative climb reaches vermillion-study from here any more.
DEFAULT_CORPUS = "D:/KDP Books/vermillion-study/corpus/human"


def sentences(text):
    """Verbatim from check-uniformity.py. If one changes, change both."""
    text = re.sub(r"^#.*$", "", text, flags=re.M)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 2]


def paragraphs(text):
    """Verbatim from check-uniformity.py."""
    text = re.sub(r"^#.*$", "", text, flags=re.M).strip()
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def window(paras, size):
    """Split a novel into chapter-sized units of ~size words."""
    chunks, cur, n = [], [], 0
    for p in paras:
        cur.append(p)
        n += len(p.split())
        if n >= size:
            chunks.append(cur)
            cur, n = [], 0
    if cur:
        chunks.append(cur)
    return chunks


def measure(path, size):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    paras = paragraphs(text)
    if len(paras) < 100:
        return None
    cvs, ones = [], []
    for chunk in window(paras, size):
        plens = [len(p.split()) for p in chunk]
        if len(plens) > 2 and st.mean(plens):
            cvs.append(100 * st.pstdev(plens) / st.mean(plens))
        counts = [len(sentences(p)) for p in chunk]
        if counts:
            ones.append(100.0 * sum(1 for c in counts if c == 1) / len(counts))
    if not cvs or not ones:
        return None
    return (st.mean(ones), st.mean(cvs), len(text.split()))


def q(v, x):
    v = sorted(v)
    return v[min(int(len(v) * x), len(v) - 1)]


def main():
    args = sys.argv[1:]
    size = 3000
    if "--window" in args:
        i = args.index("--window")
        size = int(args[i + 1])
        del args[i:i + 2]

    root = args[0] if args else DEFAULT_CORPUS
    if not os.path.isdir(root):
        print(f"measure-pd-corpus: {root} is not a directory.")
        print("  usage: python measure-pd-corpus.py <dir-of-.txt-novels> [--window 3000]")
        return 1

    rows = []
    for path in sorted(glob.glob(os.path.join(root, "*.txt"))):
        m = measure(path, size)
        if m:
            rows.append((os.path.basename(path), m[0], m[1], m[2]))

    if not rows:
        print(f"measure-pd-corpus: no usable novels in {root} "
              f"(each needs 100+ recoverable paragraphs)")
        return 1

    ones = [r[1] for r in rows]
    cvs = [r[2] for r in rows]
    words = sum(r[3] for r in rows)

    print("=" * 67)
    print(f"U4/U5 over {len(rows)} public-domain novels, {words:,} words")
    print(f"corpus: {root}")
    print(f"method: check-uniformity.py's arithmetic, chapters of ~{size} words")
    print("=" * 67)

    print()
    print("U4  one-sentence paragraph share")
    print(f"    min {min(ones):.1f}%   q25 {q(ones,.25):.1f}%   median {q(ones,.5):.1f}%   "
          f"q75 {q(ones,.75):.1f}%   max {max(ones):.1f}%")
    fail = sum(1 for v in ones if v < ONELINE_FAIL)
    warn = sum(1 for v in ones if ONELINE_FAIL <= v < ONELINE_WARN)
    print(f"    against current gates (fail <{ONELINE_FAIL:.0f}%, warn <{ONELINE_WARN:.0f}%):")
    print(f"      FAIL {fail}/{len(rows)} ({100.0*fail/len(rows):.0f}% of the corpus)"
          f"    WARN {warn}/{len(rows)}")

    print()
    print("U5  paragraph-length CV")
    print(f"    min {min(cvs):.0f}%   q25 {q(cvs,.25):.0f}%   median {q(cvs,.5):.0f}%   "
          f"q75 {q(cvs,.75):.0f}%   max {max(cvs):.0f}%")
    fail5 = sum(1 for v in cvs if v < PARACV_FAIL)
    warn5 = sum(1 for v in cvs if PARACV_FAIL <= v < PARACV_WARN)
    print(f"    against current gates (fail <{PARACV_FAIL:.0f}%, warn <{PARACV_WARN:.0f}%):")
    print(f"      FAIL {fail5}/{len(rows)} ({100.0*fail5/len(rows):.0f}% of the corpus)"
          f"    WARN {warn5}/{len(rows)}")

    print()
    print("  Five novels with the LOWEST one-sentence share - the ones U4 would fail:")
    for name, o, c, w in sorted(rows, key=lambda r: r[1])[:5]:
        verdict = "FAIL" if o < ONELINE_FAIL else "warn"
        print(f"    {name:<14} {o:5.1f}%  CV {c:3.0f}%  {w:>7,} words   -> U4 {verdict}")

    print()
    print("  No threshold is proposed by this script. See the docstring: a 19th-century")
    print("  corpus is not the register this pipeline sells into, and paragraph-breaking")
    print("  practice moved across the twentieth century. This is evidence about U4's")
    print("  standing, not a replacement derivation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
