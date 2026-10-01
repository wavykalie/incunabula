#!/usr/bin/env python3
"""check-surplus.py - how much of the dialogue carries no plot.

WHY THIS EXISTS
  Every other check in this directory asks whether the prose is *bad*. This one asks
  whether it is *all load-bearing*, and it exists because that is the failure mode no
  per-1k cap can see: a chapter in which every line of dialogue states a fact, makes a
  decision, or moves someone to a new place is not badly written. It is dead.

  VERMILLION (vermillion-study/, 140 public-domain English novels against 185 machine
  texts, genre/period/length controlled) measures the human corpus's dialogue as
  disproportionately *non-instrumental* - material that advances nothing - and names
  this as the strongest single intervention available to a writing tool: give the
  characters something to do with the scene that is not plot. Surplus, in the study's
  words, is what a model has no reason to generate and a reader most notices the
  absence of.

  Nothing in this directory could see it. Dialogue *share* is in the drift vector, but
  share is a quantity: 30% of the words being inside quotation marks says nothing about
  whether any of them mattered.

WHAT IT MEASURES, AND WHY EACH ROW IS REPORT-ONLY

  S1  speech-turn length CV        the distribution of turn lengths across the book
  S2  share of turns <= 3 words     backchannel, banter, the sound of a relationship
  S3  share of turns >= 25 words    digression, aside, the second thing someone means
  S4  instrument ratio              NOTE tier, lexicon-dependent, never gates

  Every row is report-only and this check cannot fail. That is a deliberate reversal of
  the convention in deslop-check.sh, and the reason is stated rather than hidden: S1-S3
  have no calibration corpus behind them, and this project does not publish a rule it
  cannot measure. The corpus that would measure them is the one described in
  CALIBRATION.md as missing - see "Re-deriving, if the corpus changes".

  S1-S3 are lexicon-free on purpose. That is the whole design. VERMILLION's most
  important methodological finding about itself is that "the lexicons are the
  instrument" - six of its measures depend on hand-assembled word lists, and a
  different list gives different numbers. A surplus measure built on a list of
  "banter words" would inherit that problem and be defended as if it did not have it.
  Turn-length distribution needs no list, and it measures the same underlying thing the
  study measured: surplus speech produces short exchanges AND long digressions, so it
  widens the distribution. A book whose every speech turn runs 8-14 words has one
  setting for its dialogue, which is U2's finding wearing different clothes.

THE ROW THAT MATTERS MOST IS THE SPREAD, NOT THE MEAN

  S1 is reported per chapter and then as a spread across chapters, and the spread is
  the row to read. VERMILLION's central result is that machine prose's variation is not
  flattened sentence to sentence - within-window burstiness is identical to the human
  corpus, p = .72 - but across documents. A model has one tempo and holds it. A novel
  has a tempo, a second tempo for the scene after, and a third for the chapter later.
  So a book whose per-chapter S1 all land within two points of each other has a
  dialogue problem that no mean can report and that a reader will feel immediately.

WHAT IT DOES NOT DO

  It cannot tell surplus from padding. A long digression that a reader loves and a long
  digression that a reader skips are the same length. It cannot tell a character lying
  from a character talking, and the study is explicit that hedging and moral ambiguity
  are architectures rather than surfaces - a measure that counts hedges will find more
  hedging in a novel built from incompatible testimony and the finding will be
  coincidental. It measures distribution, not value.

  When S1 is low, the remedy is NOT to cut dialogue. Cutting surplus is how you get a
  novel with no surplus, which is the thing being measured. The remedy is a brief: a
  scene where two people are in a place and the plot does not require them to be there.

  usage:  tools/check-surplus.py [BOOK_DIR_OR_CHAPTER_DIR ...]
          (no argument = every */manuscript/chapters under the project root)
          exit 0 = reported   exit 1 = nothing checkable
"""

import os
import re
import sys
import glob
import statistics as st

# Same extraction as the dialogue-share feature in check-drift.py, deliberately, so the
# two tools cannot disagree about what counts as speech.
QUOTED = re.compile(r"[\u201c\"]([^\u201d\"]{0,400})[\u201d\"]")

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)

MIN_CHAPTERS = 4

# A chapter's S1 needs enough turns for a coefficient of variation to mean anything.
# Measured rather than assumed: at 8 turns the CV of a Poisson-ish count swings by tens
# of points on a single long speech span, and the cross-chapter spread row - which is
# the row this file exists for - inherits that noise directly. 20 turns puts the
# standard error low enough for the spread to mean something. Chapters below it are
# reported as unreadable rather than guessed at.
MIN_TURNS = 20

# --- S4 lexicon. NOTE tier. Printed on every run so it can be argued with. ----------
#
# This list is the weakest thing in the file and it is here because a reader will ask
# what "instrumental" means, not because the ratio is trustworthy. CALIBRATION.md's
# rule is that a list is never neutral; the same is true here, which is why S4 never
# gates and why it is the only row that would change if someone swapped the words.
#
# Held as plain words, not raw regex, because the whole point of printing them is that
# a reader can disagree with them.
INSTRUMENT = {
    "commitment": ["must", "have to", "has to", "need to", "needs to", "going to",
                   "gonna", "will", "shall", "let's"],
    "directive": ["wait", "stop", "come", "go", "listen", "look", "tell me", "do it",
                  "do you", "can you", "we should", "you should"],
    "scene and time": ["now", "tonight", "tomorrow", "yesterday", "before", "after",
                       "when", "until", "morning", "evening"],
    "conditionality": ["because", "unless", "instead", "either", "whether", "if you",
                       "if we", "suppose"],
}
SURPLUS = {
    "contact": ["hello", "hi", "hey", "goodbye", "bye", "thanks", "thank you", "please",
                "sorry", "well", "so"],
    "backchannel": ["what", "really", "seriously", "hm", "mm", "yeah", "no", "oh", "ah",
                    "eh"],
    "sensation said aloud": ["cold", "hot", "tired", "hungry", "thirsty", "afraid",
                             "scared", "hurt", "sore", "smell", "taste", "laugh", "smile",
                             "sigh", "shake"],
    "discourse frame": ["you know", "i mean", "sort of", "kind of", "anyway", "whatever"],
}


def _rx(words):
    return re.compile("|".join(r"\b%s\b" % re.escape(w) for w in words), re.I)


INSTRUMENT_RX = _rx([w for group in INSTRUMENT.values() for w in group])
SURPLUS_RX = _rx([w for group in SURPLUS.values() for w in group])

# A proper noun mid-sentence, or any number: speech reaching outside itself for a fact.
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}\b")
DIGIT = re.compile(r"\b\d+\b")


def turns(text):
    """Speech spans, in order, as word lists."""
    return [q.split() for q in QUOTED.findall(text) if q.split()]


def load(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if CHAPTER.search(name):
            with open(os.path.join(directory, name), encoding="utf-8", errors="ignore") as fh:
                out.append((name, fh.read()))
    return out


def resolve(arg):
    """Accept a book dir, a manuscript dir, or a chapter dir. Mirrors check-uniformity."""
    for candidate in (arg, os.path.join(arg, "manuscript"), os.path.join(arg, "manuscript", "chapters")):
        if os.path.isdir(candidate) and any(CHAPTER.search(n) for n in os.listdir(candidate)):
            return candidate
    return None


def declare_nonfiction(book_root):
    """Surplus speech is a narrative property; nonfiction carries it as context only."""
    path = os.path.join(book_root, "PROJECT_STATE.yaml")
    if not os.path.isfile(path):
        return False
    with open(path, encoding="utf-8", errors="ignore") as fh:
        head = fh.read(4000)
    return bool(re.search(r"^\s*(positioning|genre)\s*:\"?[^\n]*nonfiction", head, re.I | re.M))


def measure(text):
    """The four rows, plus the S1 cross-chapter spread, for one book."""
    all_turns = []
    per_chapter = []
    for name, body in text:
        ts = turns(body)
        if not ts:
            per_chapter.append((name, 0, 0.0, 0.0, 0.0, 0.0))
            continue
        lengths = [len(t) for t in ts]
        mean_len = st.mean(lengths)
        cv = 100 * st.pstdev(lengths) / mean_len if mean_len else 0.0
        short = 100.0 * sum(1 for n in lengths if n <= 3) / len(lengths)
        long_ = 100.0 * sum(1 for n in lengths if n >= 25) / len(lengths)
        per_chapter.append((name, len(ts), mean_len, cv, short, long_))
        all_turns.extend(ts)

    lengths = [len(t) for t in all_turns]
    if not lengths:
        return None

    book_cv = 100 * st.pstdev(lengths) / st.mean(lengths)
    short = 100.0 * sum(1 for n in lengths if n <= 3) / len(lengths)
    long_ = 100.0 * sum(1 for n in lengths if n >= 25) / len(lengths)

    # S4. Counts are over speech words, not turns, so a long turn is not cheap.
    #
    # Proper nouns and digits are counted SEPARATELY rather than folded into the
    # instrument side. They were in the first version of this file and they inflated
    # the ratio badly - a name in dialogue is far more often a vocative ("Hello,
    # Sarah") than a fact being reported, so the row was measuring the cast list.
    # A name mid-sentence does suggest speech reaching outside itself, which is a real
    # signal, but it is a different signal and a reader is entitled to see it apart
    # from the verbs. Both ratios are printed for that reason.
    speech = " ".join(" ".join(t) for t in all_turns)
    inst = len(INSTRUMENT_RX.findall(speech))
    sur = len(SURPLUS_RX.findall(speech))
    proper = len(PROPER.findall(speech))
    digit = len(DIGIT.findall(speech))
    denom = inst + sur
    ratio = 100.0 * inst / denom if denom else None
    ratio_wide = 100.0 * (inst + proper + digit) / (denom + proper + digit) if (denom + proper + digit) else None

    ch_cvs = [row[3] for row in per_chapter if row[1] >= MIN_TURNS]
    spread = (max(ch_cvs) - min(ch_cvs)) if len(ch_cvs) >= 3 else None

    return {
        "turns": len(lengths),
        "words": sum(lengths),
        "mean": st.mean(lengths),
        "cv": book_cv,
        "short": short,
        "long": long_,
        "ratio": ratio,
        "ratio_wide": ratio_wide,
        "inst": inst,
        "sur": sur,
        "proper": proper,
        "digit": digit,
        "spread": spread,
        "per_chapter": per_chapter,
    }


def report(label, chapters):
    m = measure(chapters)
    if not m:
        print(f"## {label}: no speech found. Not a finding - nothing was measured.")
        return

    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters, {m['words']} words of speech "
          f"in {m['turns']} turns")
    print("=" * 67)
    print(f"{'ch':<14}{'turns':>7}{'mean len':>10}{'S1 CV':>8}{'S2 <=3w':>9}{'S3 >=25w':>10}")

    for name, n, mean_len, cv, short, long_ in m["per_chapter"]:
        if n < MIN_TURNS:
            print(f"{name:<14}{n:>7}{'-':>10}{'-':>8}{'-':>9}{'-':>10}   "
                  f"(under {MIN_TURNS} turns - too few for a CV)")
            continue
        print(f"{name:<14}{n:>7}{mean_len:>10.1f}{cv:>8.0f}{short:>8.0f}%{long_:>9.0f}%")

    print()
    print(f"   --   S1  speech-turn length CV      {m['cv']:.0f}%  "
          f"(mean turn {m['mean']:.1f} words)")
    print(f"   --   S2  turns of 3 words or fewer  {m['short']:.0f}%")
    print(f"   --   S3  turns of 25 words or more  {m['long']:.0f}%")

    if m["spread"] is not None:
        print()
        print(f"   !!   S1 spread across chapters    {m['spread']:.0f} points  <-- read this row first")
        print("        Chapters within a couple of points of each other means one tempo for the")
        print("        whole book's dialogue. VERMILLION: within-window variation is NOT where")
        print("        machine prose flattens (p = .72); across-document variation is.")
    else:
        print(f"   --   S1 spread across chapters    n/a (fewer than 3 chapters with "
              f"{MIN_TURNS}+ turns)")

    print()
    if m["ratio"] is not None:
        print(f"   --   S4  instrument ratio          {m['ratio']:.0f}%  (NOTE tier, lexicon-dependent)")
        print(f"        counts: instrument {m['inst']}, surplus {m['sur']}, plus {m['proper']} "
              f"proper nouns and {m['digit']} numbers")
        if m["ratio_wide"] is not None:
            print(f"        including names and numbers as instrument: {m['ratio_wide']:.0f}%  "
                  f"(wider reading)")
        print("        Above ~55% is worth a look. It is NOT a pass/fail, and the number is only")
        print("        as good as the list behind it, which is this one:")
        for group, words in INSTRUMENT.items():
            print(f"          instrument/{group}: {', '.join(words)}")
        for group, words in SURPLUS.items():
            print(f"          surplus/{group}:    {', '.join(words)}")
    else:
        print("   --   S4  instrument ratio          n/a (no instrument or surplus markers)")

    print()
    print("  These rows do not fail anything, and none of them has a calibration corpus.")
    print("  They are here to be read by a person, which is the same standing as the NOTE")
    print("  tier in deslop-check.sh. To promote S1-S3 to gates, measure the calibration")
    print("  corpus first and record it in CALIBRATION.md - see the re-deriving section.")
    if m["ratio"] is not None and m["ratio"] > 55:
        print()
        print("  A brief, not a cut: a scene where two people are in a place and the plot does")
        print("  not require them to be there. Do not delete dialogue to move this number.")


def main():
    args = sys.argv[1:]
    targets = []

    if args:
        for arg in args:
            directory = resolve(arg)
            if directory:
                targets.append((arg, directory))
            else:
                print(f"check-surplus: no chapters found under {arg}")
                return 1
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        found = glob.glob(os.path.join(root, "*", "manuscript", "chapters"))
        if os.path.isdir(os.path.join(root, "manuscript", "chapters")):
            found.append(os.path.join(root, "manuscript", "chapters"))
        for directory in sorted(found):
            label = os.path.basename(os.path.dirname(os.path.dirname(directory)))
            targets.append((label, directory))

    checked = 0
    for label, directory in targets:
        chapters = load(directory)
        if len(chapters) < MIN_CHAPTERS:
            print(f"check-surplus: {label} has {len(chapters)} chapters, "
                  f"fewer than {MIN_CHAPTERS} - skipped")
            continue
        checked += 1
        book_root = os.path.dirname(os.path.dirname(directory))
        if declare_nonfiction(book_root):
            print(f"## {label}: declared nonfiction. Surplus speech is a narrative property;")
            print("   rows reported for context, and a low S1 in nonfiction is not a finding.")
        report(label, chapters)
        print()

    if checked == 0:
        print("check-surplus: nothing checkable - a report with no books read proves nothing.")
        return 1

    print("=" * 67)
    print(f"SURPLUS REPORTED - {checked} manuscript(s). No row gates, by design.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
