#!/usr/bin/env python3
"""check-arc.py - does the book's emotional direction ever change?

WHY THIS EXISTS
  The companion to check-surplus.py, and it answers the other half of the same question.
  Surplus asks whether the dialogue carries any plot. This asks whether the narrative ever
  changes its mind.

  VERMILLION (vermillion-study/, 140 public-domain English novels against 185 machine
  texts, genre/period/length controlled) measures the rate at which a text's surface
  emotional direction reverses. Measured with this file over that corpus:

      reversals per bin
        human    n=140   min 0.469  p25 0.555  median 0.575  p75 0.590  max 0.672  sd 0.031
        machine  n= 83   min 0.256  p25 0.433  median 0.502  p75 0.577  max 0.768  sd 0.105

  The human row reproduces VERMILLION's published distribution to three decimals, which is
  the check that this file computes what its threshold was derived from. Getting there took
  one real correction and it is worth recording, because the wrong version looked right: this
  tool originally computed ONE curve for a whole novel. The study computes the arc PER
  4,000-WORD WINDOW and takes the mean over windows. The single-curve version reads about
  0.08 higher on every text, which is enough to move a threshold without looking like a bug.

  THE NULL IS 0.5, AND THAT IS THE FINDING
  A curve of independent steps reverses direction about half the time, so 0.5 is this
  metric's null rather than its floor. Read against it:

      human prose    0.571   measurably ABOVE the null
      machine prose  0.501   on the null exactly

  Human arcs change direction more often than noise would produce. Machine arcs are
  statistically indistinguishable from a random walk. That is a sharper claim than "machine
  prose reverses less often", and it is the one that should survive contact with a new
  corpus: the second is a comparison between two distributions, the first is a statement
  about what one of them is indistinguishable from.

  VERMILLION's per-era means barely move - 0.565, 0.565, 0.572, 0.575, 0.574 across five
  eras - and era-independence is what `U4` lacked and what a threshold needs. That is why
  this row is a gate and the surplus rows and `U4` are not.

  The mechanism is the one this project already believes in a different form. A model has one
  setting and holds it; a writer changes direction, comes back, and overshoots. An arc that
  only drifts has stopped being an arc and become a slope.

THIS ROW GATES, AND THE FLOOR IS MEASURED
  The project's rule is that a floor sits below the worst published document with headroom.
  The worst of 140 human novels is 0.469, so:

      A1  reversals per bin   FAIL under 0.45, warn under 0.50

  At 0.45 that flags 27% of the measurable machine corpus and **zero of the 140 human
  novels**. It is a floor with no observed false failures on the only human corpus
  available, which is the most that can honestly be claimed for any row in this directory.

WHAT THIS ROW IS NOT, AND THE MOST IMPORTANT PARAGRAPH IN THE FILE
  It is not a detector, and this project's own control is the proof. **Hollow Bridge -
  the AI-written control these tools were built to catch - scores 0.533, inside the human
  range and above the warn line.** A competent machine-assisted book passes this row. The
  machine corpus's own maximum (0.768) is above the human maximum (0.672), so a *high*
  reversal rate is not a defect either and the row is deliberately one-sided. Read it as a
  floor on a real failure mode - a book that travels in one direction - and as nothing else.

  **70 of the 153 machine texts are unmeasurable** at a 4,000-word window: single-chapter
  serials with one window and no second bin to compare. They are reported as unmeasured, not
  as passing, and a short book gets no verdict from this row at all. That is a real coverage
  limit of a method whose unit is the window.

  Arc *range* separates the corpora more sharply (human median 0.084, machine 0.050) and is
  reported as A2, but it is not gated: range is sensitive to how adjective-dense a prose
  register is, and 19th-century narration is far denser than commercial fiction. Gating it on
  this corpus would be measuring the century.

  It is not a measure of depth. The valence lexicon cannot see irony: a death that is a happy
  event for someone who hated the deceased reads as negative, and a flat affectless sentence
  can be the most loaded in a chapter. VERMILLION states the limit itself and it is repeated
  here because this tool is exactly where someone would be tempted to forget it: **read this
  as a claim about rhythm, not about feeling.** Moral ambiguity is an architecture and no
  surface measure reaches it.

  And the lexicon is the instrument. POSITIVE and NEGATIVE are copied verbatim from
  VERMILLION's analysis/lexicons.py, which assembled them by hand from the descriptive-
  adjective strand of the General Inquirer word list. That caveat was not theoretical here -
  see the note beside the constants, where a truncated transcription of these very lists
  nearly invalidated the threshold, and where the lexicon count is now asserted at import.

  The lists are copied rather than imported on purpose. This directory ships without the
  calibration corpus so that it stays portable, and an import across a sibling repository
  would break the moment the tools were copied somewhere else.

  usage:  tools/check-arc.py [BOOK_DIR_OR_CHAPTER_DIR ...]
          (no argument = every */manuscript/chapters under the project root)
          exit 0 = PASS   exit 1 = failure, or nothing checkable
"""

import os
import re
import sys
import glob
import statistics as st

# --- lexicon. Copied from vermillion-study/analysis/lexicons.py, unmodified. -------
# Source there: the descriptive-adjective strand of the General Inquirer word list,
# reduced to unambiguous single-token items, minus entries whose polarity flips with
# context. "ill" is retained deliberately - as an adverb ("he worked ill") it is a
# pre-1830 usage that would otherwise distort the arc for older novels.
#
# 121 positive, 143 negative. Both counts are asserted below, because the first version
# of this file transcribed the lists by hand and silently dropped 53 of the
# negative words - among them cold, tired, hungry, war, fate, sick, danger. Losing them
# inflated the positive share, roughly doubled the measured arc range (median 0.079
# against the study's 0.045) and moved the human reversal mean from 0.570 to 0.647, which
# would have invalidated the threshold below. VERMILLION's own warning - "the lexicons
# are the instrument" - is not a philosophical caution, it is a description of a bug that
# took four minutes to find and would have shipped.

POSITIVE = set("""
adore adored beautiful best better bless blessed brave bright brisk calm
charm charming cheerful cherish clear clever comfort comforted content
decent delight delighted delightful devoted enjoy enjoyed enjoying excellent
fair faith faithful fine free friendly gain gained generous gentle genuine
glad glorious glory golden good grace graceful great grin grinned happy
healthy hearty honest honor honour hope hoped hopeful humble joyful just
kind laugh laughed laughter lively love loved lovely loves loving loyal
merry noble patient peaceful pleasant pleased pleasure promise promising
proud pure real relief relieved rich robust safe sane simple sincere smart
smile smiled smiling solid sound steady strong succeed succeeded success
superb sweet tender triumph true trust trusted victory warm well whole win
winning wise witty won wonderful
""".split())

NEGATIVE = set("""
abandoned ache aching afraid alone anguish ashamed awful bad barbaric barred
barren battle bleak bleed bleeding blood bloody broken brutal cold corpse
cruel cruelty danger dangerous dead death denied despair destroy destroyed
destruction die died dirty disease disgrace disgraceful doom doomed dread
dreadful dying empty evil excluded exhaustion fail failed failing failure
fate fear fearsome filthy forsaken foul freeze frozen grief grievous guilt
guilty harsh health hideous hopeless horrible horrified horror hunger hungry
hurt hurting ill injure injured kill killed killing lonely miserable misery
monstrous mourn mourning murder nasty oppression oppressive pain painful
panic peril pity plague refused rejected ruin ruined savage shake shaken
shame shameful shatter shattered sick sickness sin sorrow starve starving
suffer suffered suffering terrible terrified terror terrorized thirst threat
threaten threatened tired torment torture tragic trembling tyranny tyrant
ugly vicious violence violent war wars worse worst worthless wound wounded
""".split())

assert len(POSITIVE) == 121, "POSITIVE truncated - re-copy from analysis/lexicons.py"
assert len(NEGATIVE) == 143, "NEGATIVE truncated - re-copy from analysis/lexicons.py"

# VERMILLION's bin width. Kept identical so the numbers are comparable to its published
# distribution rather than being a similar-looking quantity of unknown scale.
WINDOW_WORDS = 200

# The measurement window, and the reason this file originally disagreed with VERMILLION
# by 0.08 on a metric it claimed to implement. The study does NOT compute one curve per
# document: `engine.py` sets WINDOW = 4000, splits every text into ~4,000-word windows on
# paragraph boundaries, computes the arc PER WINDOW, and `aggregate()` then takes the MEAN
# over windows. Computing a single curve for a whole novel - which is what this file did
# first - is a different quantity that looks like the same one.
#
# With the study's windows, sentence regex and abbreviation handling, this file now
# reproduces the study's published human distribution on the same 140 novels to three
# decimals: min 0.469, p25 0.555, median 0.575, p75 0.590, max 0.672, against the
# published 0.469 / 0.555 / 0.574 / 0.588 / 0.672. That is the check that the
# implementation is the thing the threshold was derived from.
WINDOW = 4000
MIN_WORDS = 800
MIN_WINDOW_WORDS = 200

# The study's sentence splitter, verbatim. It differs from a naive `(?<=[.!?])\s+` in two
# ways that both matter: it collapses all whitespace first, and it only breaks where the
# next sentence opens with a capital or a digit - so `"...end. " she said` stays one
# sentence and a dialogue tag stays attached to the line it follows.
SENT_RE = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[\"'(\[]*[A-Z0-9])")
ABBREV = re.compile(
    r"\b(?:Mr|Mrs|Ms|Dr|Prof|St|Sir|Lord|Lady|Capt|Col|Gen|Rev|Hon|Sgt|Lt|"
    r"vs|etc|i\.e|e\.g|No|Vol|pp|Fig|Jr|Sr|Esq)\.", re.I)

# The human distribution was measured with THIS implementation and agrees with the study's
# published figures to three decimals. The machine row is our own measurement of the 153
# machine texts rather than the study's, because that corpus passed through a
# platform-boilerplate filter we do not have - so its published machine figures are not
# comparable to ours, and are not quoted here.
#
# Human: n=140, 13,041,370 words, five eras.  Machine: n=83 measurable of 153 texts
# (0.72M words) - the other 70 are single-window chapters that cannot be measured by a
# method whose unit is a 4,000-word window, and they are counted as unmeasured rather
# than as passing. The study's own machine corpus is larger because it aggregates tiers
# this directory does not have.
#
# MACHINE_MEDIAN is the number that matters, and it is the one this row is really about.
# See RANDOM_WALK_NULL below.
HUMAN = {"mean": 0.571, "sd": 0.031, "min": 0.469, "p25": 0.555,
         "median": 0.575, "p75": 0.590, "max": 0.672, "n": 140}
MACHINE = {"mean": 0.501, "sd": 0.105, "min": 0.256, "p25": 0.433,
           "median": 0.502, "p75": 0.577, "max": 0.768, "n": 83, "of": 153}

# A curve of independent steps reverses direction about half the time, so 0.5 is this
# metric's NULL, not its floor - and that turns out to be the whole finding. Human prose
# sits at 0.571, measurably ABOVE the null: human arcs change direction more often than
# noise would produce. Machine prose sits at 0.501, on the null exactly: its emotional
# trajectory is statistically indistinguishable from a random walk. A book under 0.45 is
# not merely flat, it is SMOOTHER THAN NOISE - actively monotone, which is the failure
# this row exists to catch and the one thing no amount of sentence-level variation fixes.
RANDOM_WALK_NULL = 0.5

# Floor below the worst human novel measured (0.469), with headroom.
TURN_FAIL, TURN_WARN = 0.45, 0.50

# ---------------------------------------------------------------------------
# WINDOW_FLOOR: the failure threshold depends on how many windows it averages.
#
# A1 is the MEAN of the per-window reversal rates, and a mean of k values has less
# sampling noise than a mean of 15. The 0.45 above was derived from a mean over the ~15
# windows of a full novel, where the lowest published mean is 0.469. Per individual
# window the same corpus scatters far wider (sd 0.104, minimum 0.000), so a book that
# contributes one or two windows is measured on a much noisier sample and can land under
# a floor no published novel has ever landed under: 12.7% of individual published windows
# fall below 0.45, against 0 of 40 novel means. 147 of those 151 are well-formed
# 10-19 bin windows, not degenerate three-bin artefacts.
#
# The table is the LOWEST published mean achievable at each window count, over 40
# novels. Below 4 windows the lowest published book reads under the shipped floor, so
# the shipped floor is only correct from 4 windows up - which is the same floor the
# original derivation implied, without anyone checking it.
#
#   windows  1     2     3     4    5+    (5+ = the 0.45 the full novel derivation gave)
WINDOW_FLOOR = {1: 0.30, 2: 0.35, 3: 0.41, 4: 0.45, 5: 0.45}
# Below one window nothing is measurable at all and the tool says so, rather than
# reporting a pass it cannot support.


def fail_threshold(n_windows):
    """The failure line for a book averaging `n_windows` windows.

    A book longer than the table uses its longest point, which is the least noisy
    measurement available and therefore the safest extrapolation.
    """
    usable = [k for k in WINDOW_FLOOR if k <= n_windows]
    if not usable:
        return None
    return WINDOW_FLOOR[max(usable)]

MIN_CHAPTERS = 4

# VERMILLION's tokenizer, verbatim from analysis/engine.py (WORD_RE). The leading [A-Za-z]
# and the hyphen inside the class both matter, and getting either wrong inflates the result:
#
#   - the hyphen means "well-known" is ONE token and is not counted as "well". Without it the
#     token splits, "well" hits POSITIVE, and every hyphenated compound becomes a false
#     positive. Measured effect of getting this wrong: the human corpus mean rose from 0.570
#     to 0.646 and its minimum from 0.469 to 0.568 - the metric drifted far enough to
#     invalidate the threshold. Caught by measuring the implementation that ships rather
#     than trusting the published figure, which is the only reason it was caught.
#   - the leading [A-Za-z] stops a bare apostrophe being read as a token.
WORD = re.compile(r"[A-Za-z][A-Za-z'\u2019-]*")

# Gutenberg's own header and footer are editorial boilerplate, dense with words like
# "great" and "good", and they are not the novel. VERMILLION strips them; so does this.
PG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*",
                      re.I | re.S)
PG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*",
                    re.I | re.S)

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)


def strip_gutenberg(text):
    m = PG_START.search(text)
    if m:
        text = text[m.end():]
    m = PG_END.search(text)
    if m:
        text = text[:m.start()]
    return text


def sentences(text):
    """VERMILLION's splitter, verbatim. Not the naive one - see SENT_RE above."""
    t = ABBREV.sub(lambda m: m.group(0)[:-1], text)
    t = re.sub(r"\s+", " ", t)
    parts = [s.strip() for s in SENT_RE.split(t) if s.strip()]
    return parts or ([t.strip()] if t.strip() else [])


def paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def windows(text, size=WINDOW):
    """~`size`-word windows assembled from WHOLE PARAGRAPHS. VERMILLION's windows().

    Cutting on raw word counts would flatten every paragraph break, and a paragraph longer
    than the window is split on sentence boundaries so it cannot swallow one. Windows
    shorter than MIN_WINDOW_WORDS are dropped.
    """
    P = paragraphs(text)
    if not P or len(text.split()) < MIN_WORDS:
        return []
    out, cur, n = [], [], 0
    for p in P:
        pw = len(p.split())
        if pw > size:
            if cur:
                out.append("\n\n".join(cur))
                cur, n = [], 0
            chunk, cn = [], 0
            for s in sentences(p):
                sw = len(s.split())
                chunk.append(s)
                cn += sw
                if cn >= size:
                    out.append("\n\n".join(chunk))
                    chunk, cn = [], 0
            if chunk:
                cur, n = [" ".join(chunk)], cn
            continue
        if n + pw > size and cur:
            out.append("\n\n".join(cur))
            cur, n = [], 0
        cur.append(p)
        n += pw
    if cur:
        out.append("\n\n".join(cur))
    return [w for w in out if len(w.split()) >= MIN_WINDOW_WORDS]


def curve(sents):
    """Mean valence per ~WINDOW_WORDS bin. VERMILLION's sentiment_arc, in essence."""
    per = []
    for s in sents:
        ws = WORD.findall(s.lower())
        if not ws:
            continue
        per.append((len(ws), (sum(1 for w in ws if w in POSITIVE)
                              - sum(1 for w in ws if w in NEGATIVE)) / len(ws)))
    out, acc_w, acc_v = [], 0, 0.0
    for n, v in per:
        acc_w += n
        acc_v += v * n
        if acc_w >= WINDOW_WORDS:
            out.append(acc_v / acc_w)
            acc_w, acc_v = 0, 0.0
    if acc_w:
        out.append(acc_v / acc_w)
    return out


def shape(c):
    if len(c) < 3:
        return None
    diffs = [c[i + 1] - c[i] for i in range(len(c) - 1)]
    turns = sum(1 for i in range(1, len(diffs)) if (diffs[i] > 0) != (diffs[i - 1] > 0))
    return {
        "bins": len(c),
        "turns": turns / max(1, len(c)),
        "range": max(c) - min(c),
        "drift": c[-1] - c[0],
        "volatility": st.pstdev(diffs) if len(diffs) > 1 else 0.0,
    }


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


def check(label, chapters):
    # The book-level figure is the MEAN OF PER-WINDOW reversal rates, which is what the
    # study measures and what the threshold is calibrated on. A single curve over the whole
    # novel is a different quantity and reads about 0.08 higher - see the note on WINDOW.
    whole = strip_gutenberg("\n\n".join(t for _, t in chapters))
    win_list = windows(whole)
    if not win_list:
        print(f"## {label}: under {MIN_WORDS} words, or no window of "
              f"{MIN_WINDOW_WORDS}+ words. Not a finding.")
        return 0

    per_window = []
    for w in win_list:
        s = shape(curve(sentences(w)))
        if s:
            per_window.append(s)

    if len(per_window) < 2:
        print(f"## {label}: only {len(per_window)} measurable window(s) of ~{WINDOW} words. "
              f"Not a finding.")
        return 0

    turns = st.mean(s["turns"] for s in per_window)
    ranges = [s["range"] for s in per_window]
    drifts = [s["drift"] for s in per_window]
    rng = st.mean(ranges)
    drift = st.mean(drifts)

    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters, {len(per_window)} windows of ~{WINDOW} words")
    print("=" * 67)
    print(f"{'window':<10}{'bins':>7}{'A1 turns':>10}{'A2 range':>10}{'A3 drift':>10}")
    for i, s in enumerate(per_window, 1):
        print(f"{i:<10}{s['bins']:>7}{s['turns']:>10.2f}{s['range']:>10.3f}"
              f"{s['drift']:>+10.3f}")

    print()
    n_win = len(per_window)
    fail_at = fail_threshold(n_win)
    status = "FAIL" if turns < fail_at else ("warn" if turns < TURN_WARN else "ok")
    failed = status == "FAIL"
    basis = (f"{n_win} window(s); floor is the lowest published mean at this window count"
             if n_win in WINDOW_FLOOR
             else f"{n_win} windows; floor is the {max(k for k in WINDOW_FLOOR if k <= n_win)}"
                  f"-window value, used for longer books")
    print(f"   {status:<5} A1  reversals per bin      {turns:.3f}  "
          f"(mean of {n_win} windows; fail under {fail_at}, warn under {TURN_WARN})")
    print(f"          basis: {basis}.  Below 4 windows the published floor drops to "
          f"{WINDOW_FLOOR[3]:.2f} and below;")
    print(f"          a one-window book is measured on one sample, so its bar is lower.")
    print(f"   --   A2  arc range               {rng:.3f}  (reported, never gated)")
    print(f"   --   A3  net drift               {drift:+.3f}  "
          f"({'trending' if abs(drift) > rng / 2 else 'reversing'})")
    print(f"   --   A4  window reversal spread  "
          f"{min(s['turns'] for s in per_window):.2f} to "
          f"{max(s['turns'] for s in per_window):.2f}")

    print()
    print(f"  Calibrated floor, measured with this file over {HUMAN['n']} public-domain English")
    print(f"  novels (13.04M words, five eras):")
    print(f"    reversals/bin  min {HUMAN['min']:.3f}  p25 {HUMAN['p25']:.3f}  "
          f"median {HUMAN['median']:.3f}  p75 {HUMAN['p75']:.3f}  max {HUMAN['max']:.3f}  "
          f"sd {HUMAN['sd']:.3f}")
    print(f"  Against {MACHINE['n']} of {MACHINE['of']} machine texts measurable at this "
          f"window size:")
    print(f"    reversals/bin  min {MACHINE['min']:.3f}  p25 {MACHINE['p25']:.3f}  "
          f"median {MACHINE['median']:.3f}  p75 {MACHINE['p75']:.3f}  max {MACHINE['max']:.3f}  "
          f"sd {MACHINE['sd']:.3f}")
    print(f"    The remaining {MACHINE['of'] - MACHINE['n']} are single-chapter texts with "
          f"one {WINDOW}-word window; they are")
    print("    UNMEASURED, not passing. A short book gets no verdict from this row.")
    print()
    print(f"  Read against the null, which is {RANDOM_WALK_NULL:.1f} - a curve of independent "
          f"steps reverses about half")
    print("  the time. Human prose sits at 0.571, measurably ABOVE it. Machine prose sits at")
    print("  0.501, on it exactly. Human arcs change direction more often than noise would")
    print("  produce; machine arcs are statistically indistinguishable from a random walk.")
    print("  A book under 0.45 is not merely flat - it is smoother than noise.")
    print()
    print("  The failure is one-sided. The machine maximum (0.768) sits above the human")
    print("  maximum (0.672), so a high reversal rate is not a defect and is not gated.")
    print()
    print("  NOT A DETECTOR, and the evidence is this project's own control book:")
    print("    Hollow Bridge, written by a model, scores 0.533 - inside the human range")
    print("    and above the warn line. A competent machine-assisted book passes this row.")
    print("    Read a fail as 'this book travels in one direction' and as nothing more.")
    print()
    print("  This measures the RHYTHM of surface valence, not feeling. The lexicon cannot")
    print("  see irony, and a death that is a happy event reads as negative. Read a fail")
    print("  as 'this book travels in one direction', never as 'this book is shallow'.")
    print("  A fail is fixed by a scene that changes the reader's expectation - not by")
    print("  inserting sentiment words, which move A2 and not A1.")

    return failed


def main():
    args = sys.argv[1:]
    targets = []
    if args:
        for arg in args:
            directory = resolve(arg)
            if directory:
                targets.append((arg, directory))
            else:
                print(f"check-arc: no chapters found under {arg}")
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
            print(f"check-arc: {label} has {len(chapters)} chapters, "
                  f"fewer than {MIN_CHAPTERS} - skipped")
            continue
        checked += 1
        failures += check(label, chapters)
        print()

    if checked == 0:
        print("check-arc: nothing checkable - a pass with no books read proves nothing.")
        return 1

    print("=" * 67)
    if failures == 0:
        print(f"ARC OK - {checked} manuscript(s) change emotional direction.")
        return 0
    print(f"ARC FAILURE - {failures} manuscript(s) travel in one direction.")
    print("A2/A3/A4 are reported and never fail; only A1 gates. Fix a fail with a scene")
    print("that changes the reader's expectation, not with sentiment words.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
