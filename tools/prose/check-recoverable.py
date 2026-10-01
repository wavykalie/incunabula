#!/usr/bin/env python3
"""check-recoverable.py - which of a book's anomalies have an excuse?

WHY THIS EXISTS
  VERMILLION's most-wanted measure, and the one it says it most wishes it had:

    "not the presence of inconsistency but the presence of *justified* inconsistency,
     where a reader can infer the reason. A text can be tested for this by whether its
     anomalies are recoverable - whether they cluster at points where a motive can be
     supplied." (section 9.2)

  It is here, partially, because *Fantazius Mallare*'s narrator who cannot hold a register
  for a paragraph is human irregularity and a leaked constraint list is not - and the two are
  indistinguishable by counting.

  The prototype for this file is `calibration/proto-recoverable.py`, kept so the derivation
  can be re-run. It tested the study's hypothesis in two forms, and one of them failed:

    - **POSITIONAL clustering - REFUTED.** Splitting every text into ten equal bins and
      taking the Gini of a tic's distribution across them gives 0.00 to 0.07 in EVERY corpus
      and for EVERY tic. Human prose does not cluster its anomalies positionally more than
      machine prose does. The study's phrasing, read as "clustered in the text", is not what
      separates the corpora.

    - **REGISTER enrichment - SUPPORTED, and it is large.** A tic that concentrates in
      *dialogue* has a motive available in the quote marks themselves: a character
      interrupting themselves, a voice breaking off. The same tic in narration is a habit
      with nothing to recover, and it is what a reader experiences as synthetic.

      em-dash dialogue enrichment (1.0 = evenly spread; >1 = concentrated in speech):

          human, 140 novels     1.75      machine, 153 texts   0.79
          Montgomery, 270k wds  1.49      (median 10.1% dialogue vs human 19.1%)

  **The confound was tested and it is clean.** Within the human corpus, the correlation
  between a text's dialogue share and its tic enrichment is r = -0.21 to +0.28 - nothing.
  So enrichment is not simply re-measuring how much dialogue a format has, which was the
  obvious way for this to be an artefact.

  The usable statement is therefore narrower and better than the one it replaces: **an
  anomaly is recoverable when it sits in a context that supplies its own excuse.** A dash
  inside a character's mouth is that character; the same dash in narration is the writer's
  tic, and nothing in the text tells a reader to forgive it.

WHAT IT MEASURES, PER CHAPTER

  For each tic, per chapter:
    hits        raw occurrences
    speech      share of occurrences inside quotation marks
    enrich      speech share / chapter's dialogue share. >1 = in speech. <1 = in narration
    verdict     "recoverable" (enrich >= 1.15), "narrated" (< 0.85), "mixed" between

  And per book, the headline: **the share of all anomalies that are recoverable.** A book
  whose tics all live in narration has a narrator with habits and no characters with voices.

THE THRESHOLDS, AND WHY THIS CHECK GATES NOTHING
  1.15 and 0.85 are the *prototype's* observed separation points, not measured floors, and no
  floor can be measured because the quantity has no calibration corpus: there is no published
  study of anomaly recoverability to derive one from, because there is no measure of it. This
  is the one row in this directory that would need a corpus built for it rather than borrowed.
  So it reports, and a person reads it. Same standing as the NOTE tier in deslop-check.sh and
  as check-surplus.py.

  It is also, unavoidably, the measure most likely to be over-read. Enrichment near 1.0 means
  a tic is spread evenly - it does NOT mean the tic is good. And a book can score beautifully
  here while being awful: dialogue is the easiest place to hide a tic, and concentrated
  slop is still slop. **Read this as a question about where a habit lives, never as a score.**

WHAT IT DOES NOT DO
  It cannot tell a deliberate clipped sequence from an accidental one. That is the case that
  sent P3 to warn-only - Anne of Avonlea's legitimate run of 29 fragments - and this measure
  does not resolve it, because the distinction is positional and the positional axis is the
  one that tested flat. **The recoverable-anomaly idea, as measured, is about register and
  not about intent.** That is a real limit and it is the same limit the study has.

  It reads speech out of quotation marks, so quoted letters and signage count as dialogue -
  the study's own limitation (section 9.6) and, in a corpus of nineteenth-century fiction
  full of quoted documents, a real distortion.

  usage:  tools/check-recoverable.py [BOOK_DIR_OR_CHAPTER_DIR ...]
          (no argument = every */manuscript/chapters under the project root)
          exit 0 = reported   exit 1 = nothing checkable
"""

import os
import re
import sys
import glob
import statistics as st

# Same extractor as the dialogue feature in check-drift.py and the turns in
# check-surplus.py, deliberately, so the three tools cannot disagree about speech.
QUOTED = re.compile(r"[\u201c\"]([^\u201d\"]{0,400})[\u201d\"]")

# Tics worth asking about. Chosen for being common enough to have a distribution: the
# prototype showed that a tic occurring in 1-4 documents out of 137 has no measurable
# enrichment, so rarity disqualifies it from this measure by construction.
TICS = {
    "em dash":            r"\u2014",
    "rule of three":      r"[^,.;:]{3,30}, [^,.;:]{3,30}, and [^,.;:]{3,30}",
    "-ly adverb":         r"(^|[^a-z])[a-z]{4,}ly([^a-z]|$)",
    "dash parenthetical": r"\u2014[^\u2014\n]{1,70}\u2014",
    "semicolon":          r";",
    "antithesis frame":   r"(?:was|were|is|are) not[^.!?]{0,50}[.!?] +(?:It|That|This|He|She|They) (?:was|were|is|are)",
}

RECOVERABLE, NARRATED = 1.15, 0.85
MIN_CHAPTER_HITS = 5      # below this a chapter's enrichment is mostly sampling noise
MIN_CHAPTERS = 4

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)

PG_START = re.compile(r"^\*\*\* *START OF (THE|THIS) PROJECT GUTENBERG.*?$", re.M)
PG_END = re.compile(r"^\*\*\* *END OF (THE|THIS) PROJECT GUTENBERG", re.M)


def strip_gutenberg(text):
    m = PG_START.search(text)
    if m:
        text = text[m.end():]
    m = PG_END.search(text)
    if m:
        text = text[:m.start()]
    return text


def verdict(e):
    if e >= RECOVERABLE:
        return "recoverable"
    if e < NARRATED:
        return "narrated"
    return "mixed"


def chapter_stats(text):
    """(dialogue_share, {tic: (hits, speech, enrich)}) for one chapter."""
    text = strip_gutenberg(text)
    if len(text) < 400:
        return None
    spans = [(m.start(), m.end()) for m in QUOTED.finditer(text)]
    total = len(text)
    if not spans or total == 0:
        return None
    p_dial = sum(b - a for a, b in spans) / total
    out = {}
    for name, pat in TICS.items():
        hits = list(re.compile(pat, re.I).finditer(text))
        if not hits:
            continue
        d = sum(1 for m in hits if any(a <= m.start() < b for a, b in spans))
        out[name] = (len(hits), d / len(hits),
                     (d / len(hits)) / p_dial if p_dial else 0.0)
    return p_dial, out


def load(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if CHAPTER.search(name):
            with open(os.path.join(directory, name), encoding="utf-8", errors="ignore") as fh:
                out.append((name, fh.read()))
    return out


def resolve(arg):
    for c in (arg, os.path.join(arg, "manuscript"), os.path.join(arg, "manuscript", "chapters")):
        if os.path.isdir(c) and any(CHAPTER.search(n) for n in os.listdir(c)):
            return c
    return None


def check(label, chapters):
    per = []
    for name, body in chapters:
        s = chapter_stats(body)
        if s:
            per.append((name, s[0], s[1]))
    if len(per) < 2:
        print(f"## {label}: fewer than 2 chapters with dialogue. Nothing to compare.")
        return

    print("=" * 69)
    print(f"## {label}   {len(per)} chapters, dialogue share "
          f"{100*st.mean(p for _, p, _ in per):.0f}%")
    print("=" * 69)

    total_hits = 0
    recoverable_hits = 0
    book = {}

    for name, p_dial, tics in per:
        rows = [(t, v) for t, v in sorted(tics.items()) if v[0] >= MIN_CHAPTER_HITS]
        if not rows:
            print(f"{name}   (no tic reaches {MIN_CHAPTER_HITS} hits)")
            continue
        print(f"{name}   dialogue {100*p_dial:.0f}%")
        print(f"  {'tic':<20}{'hits':>6}{'in speech':>11}{'enrich':>9}  verdict")
        for t, (n, share, e) in rows:
            total_hits += n
            if e >= RECOVERABLE:
                recoverable_hits += n
            book.setdefault(t, []).append((n, e))
            print(f"  {t:<20}{n:>6}{100*share:>10.0f}%{e:>9.2f}  {verdict(e)}")
        print()

    if total_hits == 0:
        print("  No tic reached the minimum. Nothing measured, nothing claimed.")
        return

    share = 100.0 * recoverable_hits / total_hits
    print(f"  BOOK   recoverable share   {share:.0f}%   "
          f"({recoverable_hits} of {total_hits} tic occurrences sit in speech)")
    print()

    if book:
        print(f"  {'tic':<20}{'chapters':>10}{'median enrich':>15}  book verdict")
        for t, v in sorted(book.items(), key=lambda kv: -st.median(x[1] for x in kv[1])):
            e = st.median(x[1] for x in v)
            print(f"  {t:<20}{len(v):>10}{e:>15.2f}  {verdict(e)}")
        print()

    print("  A tic above 1.0 lives in speech, where a character's voice is the excuse for it.")
    print("  A tic below 1.0 lives in narration, where nothing in the text lets a reader")
    print("  recover it. Raising a narration tic is the highest-value prose fix this")
    print("  directory knows of, and it is a MOVEMENT - into a character's mouth - rather")
    print("  than a deletion.")
    print()
    print("  Two things this does not do. It does not distinguish a deliberate clipped")
    print("  sequence from an accidental one - that is the case that sent P3 to warn-only,")
    print("  and the positional axis tested flat (Gini 0.00-0.07 in every corpus), so")
    print("  recoverability here is about REGISTER, not intent. And a book can score well")
    print("  here while being poor: dialogue is the easiest place to hide a tic, and")
    print("  concentrated slop is still slop. This is a question, not a score.")
    print()
    print(f"  Thresholds {RECOVERABLE}/{NARRATED} are the prototype's observed separation")
    print("  points, not measured floors. Nothing here gates, because there is no corpus")
    print("  from which a floor could honestly be derived - the measure does not exist in")
    print("  the literature. It needs a corpus built for it, not borrowed.")


def main():
    args = sys.argv[1:]
    targets = []
    if args:
        for a in args:
            d = resolve(a)
            if d:
                targets.append((a, d))
            else:
                print(f"check-recoverable: no chapters found under {a}")
                return 1
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        found = glob.glob(os.path.join(root, "*", "manuscript", "chapters"))
        if os.path.isdir(os.path.join(root, "manuscript", "chapters")):
            found.append(os.path.join(root, "manuscript", "chapters"))
        for d in sorted(found):
            targets.append((os.path.basename(os.path.dirname(os.path.dirname(d))), d))

    checked = 0
    for label, d in targets:
        chapters = load(d)
        if len(chapters) < MIN_CHAPTERS:
            print(f"check-recoverable: {label} has {len(chapters)} chapters, "
                  f"fewer than {MIN_CHAPTERS} - skipped")
            continue
        checked += 1
        check(label, chapters)
        print()

    if checked == 0:
        print("check-recoverable: nothing checkable - a report with no books read proves nothing.")
        return 1
    print("=" * 69)
    print(f"RECOVERABLE REPORTED - {checked} manuscript(s). No row gates, by design.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
