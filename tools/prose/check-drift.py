#!/usr/bin/env python3
"""check-drift.py - the voice-shift gate.

WHY THIS EXISTS
  Every other gate in this directory asks whether a piece of writing is GOOD, or
  whether a book is MONOTONOUS. None of them asks whether a book is the SAME BOOK
  all the way through. That is a different failure and it is the one that shows up
  when a draft is finished by a different hand or a different model: chapter 1 is
  precise and short-breathed, chapter 8 has gone loose and long, and no reader can
  name what changed, only that the floor moved.

  The published guidance on AI-assisted books names this explicitly as a tell -
  "if chapter 1 sounds polished and personal but chapter 3 turns into bland
  generalities, someone likely used AI to finish the draft. Check multiple sample
  pages." It is the OPPOSITE failure to the uniformity gate: check-uniformity
  catches chapters that are too ALIKE, and this catches a book that stops being
  like itself.

SCOPE OF THE EVIDENCE
  Three published volumes and one assembled fixture. That is enough to separate
  "one voice" from "two voices", and not enough to set a tight numeric boundary.
  The cap is therefore placed at 1.75x the worst published volume rather than
  just above it, and the drift row is expected to WARN on books that are merely
  uneven. A reading of 1.2 is not a verdict; a reading of 2.4 is.

WHAT IT MEASURES
  Stylometry, not vibes. For each chapter it computes a feature vector that is
  known to be stable within one author-voice and sensitive to a change of one:

      mean sentence length          sentence-length spread (SD)
      type-token ratio (rarefied)   dialogue share (fraction inside quotes)
      commas per sentence           paragraph length, mean
      one-line paragraph share      dashes and semicolons per 1k
      function-word profile         (the, and, of, to, a, in, that, it, was, he,
                                     she, I, as relative frequencies)

  Every feature is z-scored against the book's own distribution, so a book is
  only ever compared to itself. The drift score is the sum over features of the
  step between the first half of the chapters and the second half, plus the
  largest monotonic trend across the chapter order. Both are reported, because
  they catch different shapes: a step change (half the book rewritten) and a slow
  slide (a model decaying over a long generation).

THRESHOLDS ARE MEASURED, NOT GUESSED
  Calibrated on the three published volumes of the reference corpus (48 chapters,
  175,144 words) through this same code path. Measured RMS Cohen's d, first half
  against second half:

      published vol. 1 (17 ch)   0.58      project: Sons of Heaven (15 ch)  1.26
      published vol. 2 (18 ch)   0.49      project: Merope vol. 1 (11 ch)   0.98
      published vol. 5 (13 ch)   0.80      project: Merope vol. 2 (11 ch)   0.90

  The positive control is two fixtures assembled from two different books each -
  which is by construction a book whose voice changes at the seam, because the
  seam is a different author. Both MUST fail, and both do, by a wide margin:

      published half + Hollow Bridge half    2.73
      project half + published half      2.34

  The gap between 0.80 and 2.34 is where the cap lives. It is deliberately placed
  nearer the top of that gap, because a false accusation of voice-drift is worse
  than a missed one: the remedy is rewriting a book, and the evidence is thin.

  usage:  tools/check-drift.py [BOOK_DIR_OR_CHAPTER_DIR ...]
          (no argument = every */manuscript/chapters under the project root)
  exit 0 = PASS   exit 1 = a book shifts voice, or nothing was checkable
"""

import os
import re
import sys
import glob
import math
import statistics as st

MIN_CHAPTERS = 4           # four chapters is where the measurement exists; see SIZE_FLOOR
# Calibrated, measured, and NOT tight - see the note under THRESHOLDS in the
# docstring. The step is the RMS Cohen's d across features; a stable book sits
# around 0.5-0.8 and a book whose second half is a different hand sits above 2.3.
DRIFT_FAIL, DRIFT_WARN = 1.40, 1.05

# ---------------------------------------------------------------------------
# SIZE_FLOOR: the failure threshold depends on how many chapters it is measured from.
#
# The step is a Cohen's d between the first half of the chapters and the second, so its
# sampling noise falls as the book gets longer. A single flat 1.40 was calibrated on
# volumes of 13-18 chapters and enforced on anything with >= MIN_CHAPTERS, which meant
# four-chapter books were held to a noise-dominated threshold: holding the text, author
# and voice completely fixed and varying ONLY the chapter count, 30 published novels
# sliced to 4 chapters scored a median of 2.99 and failed 30 times out of 30, against
# 0.69 and never at 20 chapters (r = -0.777).
#
# The table below is the worst PUBLISHED book at each chapter count, measured by
# `calibration/size-floors.py` over 40 novels. A clean book cannot exceed it, so a book
# on this table cannot false-fail; a book longer than the table falls back to the value
# at the largest measured size, which is the least noisy point available and therefore
# the safest extrapolation.
#
# WHAT THIS COSTS, because it is not free and the table is not the usual headroom. The
# project's convention is ~1.5x the worst reference. It CANNOT be used here: the two arms
# overlap at every size, so 1.5x the worst negative book sits ABOVE the weakest real
# voice change and the gate would stop firing. Measured on the same 40 novels, this
# table detects 37-38 of 40 genuine voice changes (92-95%) and misses the rest. The
# guarantee bought is "never fails a clean book", not "always catches real drift".
#
#   chapters  4     6     8    10    12    14    16    20+
SIZE_FLOOR = {4: 3.41, 6: 3.41, 8: 2.47, 10: 1.94,
              12: 1.73, 14: 1.76, 16: 1.60, 20: 1.40}
# No floor is derivable below 4 chapters, so there is none: a 3-chapter split is 1
# chapter against 1, and this tool declines to guess.


def fail_threshold(n_chapters):
    """The failure line for a book of `n_chapters` chapters.

    Uses the nearest measured size at or below `n_chapters`, so a book inside the
    measured range is held to the threshold that range supports, and a book longer
    than the table uses its longest point rather than the smallest.
    """
    usable = [k for k in SIZE_FLOOR if k <= n_chapters]
    if not usable:
        return None
    return SIZE_FLOOR[max(usable)]
# The trend row is a WARNING band, not a gate. Three published volumes are not
# enough to set a failure threshold on it: the published maximum (rho 0.69) is
# too close to the values a well-behaved project book returns, so failing on it
# would reject published human prose. It reports and never fails.
TREND_FAIL, TREND_WARN = 9.99, 0.75

FUNCTION_WORDS = ["the", "and", "of", "to", "a", "in", "that", "it",
                  "was", "he", "she", "i", "as", "for", "on"]

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)


def sentences(text):
    text = re.sub(r"^#.*$", "", text, flags=re.M)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 2]


def paragraphs(text):
    text = re.sub(r"^#.*$", "", text, flags=re.M).strip()
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def ttr(text, window=1000):
    """Type-token ratio on a fixed window.

    Unrarefied TTR falls as a document grows, which would make this feature a
    measure of chapter LENGTH rather than of vocabulary. Every chapter is
    therefore sampled to the same 1,000-token window.
    """
    words = [w.lower() for w in re.findall(r"[a-z']+", text.lower())][:window]
    return len(set(words)) / len(words) if words else 0.0


def features(text):
    words = re.findall(r"[A-Za-z']+", text)
    total = len(words) or 1
    sents = sentences(text)
    paras = paragraphs(text)
    lens = [len(s.split()) for s in sents] or [0]
    plens = [len(p.split()) for p in paras] or [0]

    quoted = re.findall(r"[\u201c\"]([^\u201d\"]{0,400})[\u201d\"]", text)
    dialogue = len(" ".join(quoted).split()) / total if quoted else 0.0

    lowered = [w.lower() for w in words]
    return {
        "sent_mean": st.mean(lens),
        "sent_sd": st.pstdev(lens) if len(lens) > 1 else 0.0,
        "ttr": ttr(text),
        "dialogue": dialogue,
        "commas": text.count(",") / max(len(sents), 1),
        "para_mean": st.mean(plens),
        "oneline": sum(1 for p in paras if len(sentences(p)) == 1) / max(len(paras), 1),
        "punct": 1000.0 * (text.count("\u2014") + text.count(";")) / total,
        **{f"fw_{w}": 1000.0 * lowered.count(w) / total for w in FUNCTION_WORDS},
    }


def cohens_d(first, second):
    """Standardised difference between two groups of chapter values.

    Raw z-scores were tried first and had to be abandoned: summing |z| over ~23
    features gives a score of 10 or more for a single author's own volume, because
    the sum accumulates each feature's ordinary chapter-to-chapter noise. Dividing
    by the pooled within-half spread removes that floor, so a feature only counts
    when it moves further than it normally moves inside one of the halves.
    """
    if len(first) < 2 or len(second) < 2:
        return 0.0
    pooled = math.sqrt((st.pvariance(first) + st.pvariance(second)) / 2)
    if pooled < 1e-9:
        return 0.0
    return abs(st.mean(first) - st.mean(second)) / pooled


def trend_of(series):
    """Spearman rank correlation of a feature against chapter position.

    Two defects were found here by running the tool on a book with no quoted speech
    at all, where it reported dialogue share trending at rho +1.00 across eleven
    chapters - a perfect correlation for a feature that was 0.000% in every one.

    1. Ties were given sequential ranks. Sorting a constant series yields 1,2,3..n,
       which is a perfect ramp and therefore correlates perfectly with position BY
       CONSTRUCTION. Ties now take the average of the ranks they span, which is what
       Spearman means and what makes a constant series collapse to a flat line.
    2. A series with no variance is unmeasurable, not maximally correlated. It now
       returns 0.0, and `step_and_trend` reports it as unmeasured so the row can say so
       rather than printing a confident number derived from nothing.
    """
    n = len(series)
    if n < 2:
        return 0.0
    mx = (n + 1) / 2.0
    # Average ranks over tied groups.
    order = sorted(range(n), key=lambda i: series[i])
    rank = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and series[order[j + 1]] == series[order[i]]:
            j += 1
        shared = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            rank[order[k]] = shared
        i = j + 1
    mr = st.mean(rank)
    num = sum((rank[i] - mr) * ((i + 1) - mx) for i in range(n))
    den = math.sqrt(sum((r - mr) ** 2 for r in rank) * sum(((i + 1) - mx) ** 2 for i in range(n)))
    # den == 0 means the feature never varies: there is no trend to report.
    return abs(num / den) if den > 1e-12 else 0.0


def step_and_trend(series):
    """Half-to-half step, and the largest monotonic trend."""
    n = len(series)
    half = n // 2
    if not half:
        return 0.0, 0.0
    step = cohens_d(series[:half], series[n - half:])

    return step, trend_of(series)


def load(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if CHAPTER.search(name):
            with open(os.path.join(directory, name), encoding="utf-8", errors="ignore") as fh:
                out.append((name, fh.read()))
    return out


def resolve(arg):
    for candidate in (arg, os.path.join(arg, "manuscript"), os.path.join(arg, "manuscript", "chapters")):
        if os.path.isdir(candidate):
            names = os.listdir(candidate)
            if any(CHAPTER.search(n) for n in names):
                return candidate
    return None


def check(label, chapters):
    per_feature = {}
    for name, text in chapters:
        for key, value in features(text).items():
            per_feature.setdefault(key, []).append(value)

    steps, trends = {}, {}
    for key, series in per_feature.items():
        steps[key], trends[key] = step_and_trend(series)

    drift = math.sqrt(sum(v * v for v in steps.values()) / len(steps))
    worst_trend_key = max(trends, key=lambda k: trends[k])
    trend = trends[worst_trend_key]

    n_ch = len(chapters)
    fail_at = fail_threshold(n_ch)
    if fail_at is None:
        print("=" * 67)
        print(f"## {label}   {n_ch} chapters")
        print("=" * 67)
        print(f"   skip  D1  voice-step              not measurable below "
              f"{min(SIZE_FLOOR)} chapters")
        print("          A 3-chapter split is one chapter against one, and there is no")
        print("          floor for it that is not a guess about the book's own halves.")
        return False

    status = "FAIL" if drift > fail_at else ("warn" if drift > DRIFT_WARN else "ok")
    print("=" * 67)
    print(f"## {label}   {n_ch} chapters")
    print("=" * 67)
    basis = (f"worst published book of {n_ch} chapters; fail above {fail_at:.2f}"
             if n_ch in SIZE_FLOOR
             else f"worst published book of {max(k for k in SIZE_FLOOR if k <= n_ch)} "
                  f"chapters, used for longer books; fail above {fail_at:.2f}")
    print(f"   {status:<5} D1  voice-step              {drift:.2f}  ({basis})")

    top = sorted(steps.items(), key=lambda kv: -kv[1])[:4]
    for key, value in top:
        if value >= 0.60:
            first = st.mean(per_feature[key][: len(chapters) // 2]) if len(chapters) // 2 else 0.0
            last = st.mean(per_feature[key][len(chapters) - len(chapters) // 2:])
            print(f"          - {key:<12} steps {value:.2f}   first half {first:.2f} -> second half {last:.2f}")

    status = "warn" if trend > TREND_WARN else "ok"
    print(f"   {status:<5} D2  sustained trend (advisory)  \"{worst_trend_key}\" rho {trend:+.2f} "
          f"across the chapter order  (published worst 0.69; warning above {TREND_WARN:.2f})")

    return (drift > fail_at) or (trend > TREND_FAIL)


def main():
    args = sys.argv[1:]
    targets = []
    if args:
        for arg in args:
            directory = resolve(arg)
            if directory:
                targets.append((os.path.basename(os.path.dirname(os.path.dirname(directory))) or arg, directory))
            else:
                print(f"check-drift: no chapters found under {arg}")
                return 1
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        found = glob.glob(os.path.join(root, "*", "manuscript", "chapters"))
        if os.path.isdir(os.path.join(root, "manuscript", "chapters")):
            found.append(os.path.join(root, "manuscript", "chapters"))
        for directory in sorted(found):
            targets.append((os.path.basename(os.path.dirname(os.path.dirname(directory))), directory))

    checked = failures = 0
    for label, directory in targets:
        chapters = load(directory)
        if len(chapters) < MIN_CHAPTERS:
            print(f"check-drift: {label} has {len(chapters)} chapters, fewer than "
                  f"{MIN_CHAPTERS} - cannot judge a shift, skipped")
            continue
        checked += 1
        failures += check(label, chapters)
        print()

    if checked == 0:
        print("check-drift: nothing checkable - a pass with no books read proves nothing.")
        return 1

    print("=" * 67)
    if failures == 0:
        print(f"DRIFT OK - {checked} manuscript(s) hold one voice from first chapter to last.")
        return 0
    print(f"VOICE SHIFT - {failures} manuscript(s) change how they are written partway through.")
    print("A book that stops sounding like itself halfway is the signature of a draft")
    print("finished by a different hand. Find the seam and rewrite across it, or accept")
    print("it and record the reason in RUN_REPORT.md - do not skip the row.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
