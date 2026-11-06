#!/usr/bin/env python3
"""check-dialogue-tags.py - does every character talk the same way at the tag level?

WHY THIS EXISTS
  `voice-matrix` writes a per-character voice specification. Nothing verifies the
  manuscript against it. Specs without verification are wishes. The cheapest verifiable
  slice of voice is the speech-tag layer: which verbs a character's lines get attached
  to, and how concentrated they are. When two characters share the same top tags, or a
  character's tags collapse onto whispering and gasping outside the contexts that
  justify them, the register has flattened - and it flattens at the tag level first.

  The failure this caught in the field: two viewpoint characters defaulting to
  breathless whispering and gasping everywhere, including outside intimate scenes,
  while the one character under no erotic charge sounded like a person. The prose
  gates could not see it: `check-recoverable.py` measures a tic against the text's
  own dialogue SHARE (register, not per-character behaviour), and `check-drift.py`
  watches the narrative voice, which does not shift while the dialogue flattens.

WHAT GATES, AND WHAT ONLY REPORTS
  V1 and V2 report, and cannot fail a book: there is no corpus of per-character
  speech-tag distributions, so no per-character cap can be derived. Everything they
  print is an OBSERVATION with its counts attached, and closing the voice-matrix loop
  is still a reader's judgment.

  V3 is the exception, and it is the only row in this class with a measured population
  behind it. The whole-book breath-family share of tagged spans was measured on 167
  public-domain English novels (13.4M words, `tools/prose/study` stratum C-dist-2, the
  frozen extractor v2, disjoint from the 140 novels in `calibration/`): human median
  0.048, p90 0.107, p95 0.121. The fifteen books this pipeline wrote sit at median
  0.168 and 11 of 15 exceed the fail line; twenty naive-draft books exceed it six times.
  That is the one row in the study that is both large and pipeline-specific, which is
  why it is the one row here promoted to a gate.

  Below MIN_TAGGED_FOR_V3 tagged spans the row declines to judge and says UNMEASURED:
  a p90 is not placeable on forty events, and a book with little tagged dialogue is not
  a book with a bad tag register.

WHAT IT CANNOT DO
  It attributes by name within a short window of the quote; a tag with a pronoun
  ("she said") is unattributed and counted separately, so a chapter that tags every
  line with a pronoun reports few attributed lines. It reads quoted spans, so a
  quoted letter or sign counts as speech (the same limit `check-surplus.py` records).
  It cannot see a character whose voice lives in diction and syntax rather than tags -
  the tag layer is the cheapest slice, not the whole instrument. And it cannot read
  `voice-matrix.md`; comparing the table against the spec is the reader's step,
  which is where `register` (Phase 3.1) sends it.

ROWS (V1/V2 report; V3 gates when it can be measured)
  V1  per-character tag table: tagged lines, distinct verbs, top verb + share,
      breath-family share (whisper, gasp, breathe, pant, murmur, moan, sigh, ...)
  V2  observations: shared top verbs between characters, tag collapse, the
      unattributed share, and the per-chapter breath map - which chapters carry the
      breath-heavy tags - so the register question can be asked of the right scenes
      rather than of the book in general
  V3  whole-book breath-family share of tagged spans. GATES above 0.107 (5% of 167
      human books), warns above 0.082, and reports UNMEASURED under 40 tagged spans.

EXIT CODES
  0  ran and passed: V1/V2 reported, and V3 passed, warned, or went unmeasured
  1  V3 failed a book (breath-family share above 0.107)
  2  nothing checkable: a report from an empty read proves nothing

usage:  tools/prose/check-dialogue-tags.py [BOOK_DIR_OR_CHAPTER_DIR ...]
"""

import glob
import os
import re
import sys
from collections import Counter, defaultdict

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)

QUOTE = re.compile(r"[\"\u201c]([^\"\u201c\u201d]{2,})[\"\u201d]")
# Speech verbs. The breath family is called out separately because breathless
# register outside intimate contexts is the observed failure mode (F-04).
BREATH = {"whisper", "whispered", "whispering", "gasp", "gasped", "gasping",
          "breathe", "breathed", "breathing", "pant", "panted", "panting",
          "murmur", "murmured", "murmuring", "moan", "moaned", "moaning",
          "sigh", "sighed", "sighing", "choke", "choked", "choking", "sob",
          "sobbed", "sobbing", "whimper", "whimpered", "croak", "croaked"}
# V3 - the one row here with a measured population behind it. Corpus: 167 public-domain
# English novels, stratum C-dist-2 of tools/prose/study, extractor v2. Human breath-family
# share of tagged spans: median 0.048, p90 0.107, p95 0.121. 5% of human books exceed the
# fail line; the pipeline's fifteen run at median 0.168 (11/15 above), the naive arm 6/20.
BREATH_FAIL, BREATH_WARN = 0.107, 0.082
# A guard, not a threshold: 40 spans cannot place a p90, so V3 declines to judge below it.
# The same principle as check-drift.py's size floor - a rate on too few events is noise
# wearing a number. Unmeasured is reported and gates nothing, never read as a pass.
MIN_TAGGED_FOR_V3 = 40

VERBS = (BREATH | {"said", "says", "asked", "replied", "answered", "added",
                   "continued", "offered", "called", "shouted", "yelled",
                   "snapped", "muttered", "growled", "hissed", "spat", "barked",
                   "laughed", "cried", "begged", "warned", "told", "agreed",
                   "countered", "shot", "started", "finished", "managed",
                   "returned", "echoed", "let", "let out"})
TAG = re.compile(r"\b(" + "|".join(sorted(VERBS)) + r")\b", re.I)
NAME_AFTER = re.compile(r"\b(" + "|".join(sorted(VERBS)) + r")\b[\w,\'\"\u2019\u201c\u201d -]{0,40}?\b([A-Z][a-z]{2,})\b")
NAME_BEFORE = re.compile(r"\b([A-Z][a-z]{2,})\b[\w,\'\"\u2019 -]{0,20}?\b(" + "|".join(sorted(VERBS)) + r")\b")

# Sentence-starter words and imperatives that capitalise without being names. The
# first version of this file reported Don (from "Don't"), Touch ("Touch me"),
# Breathe ("Breathe, Kaname") and Speak as characters - found by running it on a
# real book. The filters below are three, and all three are needed: an apostrophe
# guard ("Don't" -> "Don"), a starter list, and the lowercase rule - a real name in
# a manuscript does not also appear as a lowercase common word.
COMMON_NOISE = {"The", "And", "But", "She", "Her", "His", "You", "Not", "When",
                "Then", "There", "This", "That", "These", "Those", "With", "From",
                "Into", "After", "Before", "Only", "Just", "One", "Two", "Some",
                "All", "If", "He", "They", "We", "It", "Its", "My", "Your", "No",
                "Yes", "What", "Where", "How", "Why", "Who", "Which", "Don", "Do",
                "Come", "Go", "Get", "Keep", "Stay", "Hold", "Give", "Take", "Let",
                "Tell", "Wait", "Watch", "Listen", "Try", "Remember", "Forget",
                "Think", "Imagine", "Open", "Close", "Stop", "Turn", "Check", "Brace",
                "Touch", "Breathe", "Speak", "Spoke", "Look", "Good", "Hey", "Please",
                "Sorry", "Thank", "Thanks", "Okay", "Right", "Well", "Never", "Again",
                "Maybe", "Still", "Even", "Here", "Now", "Anyway", "Christ", "Jesus",
                "God", "Damn", "Hell", "Shit", "Fuck", "Hello", "Hi", "Bye"}


# Temporal nouns and honorifics capitalise without being names. Measured on the
# demo books: "said he, on Thursday" attributed seven lines to Thursday, and months,
# weekdays and Mrs filled the table. "March" and "May" are also first names; the
# over-filter is accepted and recorded - this is a report row and a missing minor row
# costs less than a table a reader stops believing.
TEMPORAL_HONORIFIC = {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december", "today", "tonight", "yesterday",
    "tomorrow", "morning", "evening", "afternoon", "night", "week", "month", "year",
    "mr", "mrs", "ms", "miss", "dr", "sir", "lady", "lord", "madam", "madame",
    "monsieur", "herr", "frau", "capt", "colonel", "general", "sergeant",
    "lieutenant", "professor", "reverend"}


def is_name_candidate(word, lowercase_words):
    return (word not in COMMON_NOISE
            and word.lower() not in lowercase_words
            and word.lower() not in TEMPORAL_HONORIFIC)


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


def attribute(text, quote_start, quote_end, lowercase_words):
    """Best-effort speaker for one quoted span. Name within a short window after the
    closing quote, else a name before the opening quote. Returns a name or None."""
    after = text[quote_end:quote_end + 120]
    for m in NAME_AFTER.finditer(after):
        word = m.group(2)
        if "'" in after[m.end(2) - 1:m.end(2) + 1] or "\u2019" in after[m.end(2) - 1:m.end(2) + 1]:
            continue        # "Don't" -> "Don": an apostrophe truncation, not a name
        if is_name_candidate(word, lowercase_words):
            return word
    before = text[max(0, quote_start - 120):quote_start]
    for m in NAME_BEFORE.finditer(before):
        word = m.group(1)
        if "'" in before[m.end(1) - 1:m.end(1) + 1] or "\u2019" in before[m.end(1) - 1:m.end(1) + 1]:
            continue
        if is_name_candidate(word, lowercase_words):
            return word
    return None


def check(label, chapters):
    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters")
    print("=" * 67)
    verbs = defaultdict(Counter)     # speaker -> verb counts
    # speaker -> chapter number -> [tagged spans, breath-family spans]. The map V2
    # reports: the field failure (F-04) was leads breathing outside the scenes that
    # justified it, and a book-level share cannot tell a reader WHICH scenes to read.
    per_ch = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    whole = "\n".join(t for _, t in chapters)
    # Words that appear lowercase ANYWHERE in the book. A real name does not; a
    # common word does. This is the strongest of the three name filters and it is
    # still a heuristic - a name that is also a lowercase common word gets dropped.
    lowercase_words = set(re.findall(r"(?<![A-Za-z])[a-z][a-z']+\b", whole))
    for name, text in chapters:
        for m in QUOTE.finditer(text):
            after = text[m.end():m.end() + 120]
            before = text[max(0, m.start() - 120):m.start()]
            # prefer the nearest verb: the after-window is the usual tag position
            vm = TAG.search(after) or TAG.search(before)
            speaker = attribute(text, m.start(), m.end(), lowercase_words)
            if not vm:
                continue
            verb = vm.group(1).lower()
            sp = speaker or "(unattributed)"
            verbs[sp][verb] += 1
            cm = CHAPTER.search(name)
            if cm:
                slot = per_ch[sp][cm.group(1)]
                slot[0] += 1
                if verb in BREATH:
                    slot[1] += 1

    if not verbs:
        print("   --   V1  no tagged dialogue found. Either the book is not dialogue-")
        print("          driven or the tags sit outside the attribution window.")
        print()
        print("  REPORT-ONLY. Rows cannot fail a book; no per-character corpus exists.")
        return 0

    tagged_total = sum(sum(c.values()) for c in verbs.values())
    breath_total = sum(n for c in verbs.values() for v, n in c.items() if v in BREATH)
    breath_share = breath_total / tagged_total if tagged_total else 0.0
    failed = 0

    print(f"\n   --   V1  per-character speech-tag distribution "
          f"({tagged_total} tagged spans):")
    print(f"{'character':<18}{'lines':>7}{'verbs':>7}{'top verb':>22}{'breath share':>14}")
    tops = {}
    for speaker in sorted(verbs, key=lambda s: -sum(verbs[s].values())):
        c = verbs[speaker]
        n = sum(c.values())
        top, topn = c.most_common(1)[0]
        breath = sum(v for k, v in c.items() if k in BREATH)
        tops[speaker] = top
        print(f"{speaker:<18}{n:>7}{len(c):>7}{f'{top} ({topn})':>22}"
              f"{f'{100.0 * breath / n:.0f}%':>14}")
    print()

    if tagged_total >= MIN_TAGGED_FOR_V3:
        status = "FAIL" if breath_share > BREATH_FAIL else (
            "warn" if breath_share > BREATH_WARN else "ok")
        failed += status == "FAIL"
        print(f"   {status:<5} V3  breath-family share of tagged spans  "
              f"{breath_share:.3f} ({breath_total}/{tagged_total})")
        print(f"          basis: 167 public-domain novels - p90 0.107, p95 0.121; 5% of")
        print(f"          human books exceed {BREATH_FAIL:.3f}. The pipeline's own fifteen:")
        print(f"          median 0.168, 11/15 above.")
    else:
        print(f"   n/a   V3  breath-family share UNMEASURED - {tagged_total} tagged spans,")
        print(f"          under the {MIN_TAGGED_FOR_V3}-span minimum for a p90 line.")
    print()

    # Pairwise observations only for speakers with enough tagged lines to have a
    # "top tag" worth sharing - a two-line character shares everything by accident.
    speakers = [s for s in tops if s != "(unattributed)"
                and sum(verbs[s].values()) >= 5]
    printed = False
    for i in range(len(speakers)):
        for j in range(i + 1, len(speakers)):
            a, b = speakers[i], speakers[j]
            if tops[a] == tops[b]:
                print(f"   --   V2  {a} and {b} share the top tag {tops[a]!r}")
                printed = True
    for speaker in speakers:
        c = verbs[speaker]
        n = sum(c.values())
        if len(c) <= 2 and n >= 5:
            print(f"   --   V2  {speaker} carries {n} tagged lines on {len(c)} verbs "
                  f"({dict(c)}) - tag collapse")
            printed = True
        breath = sum(v for k, v in c.items() if k in BREATH)
        if n >= 5 and breath / n >= 0.5:
            print(f"   --   V2  {speaker}: {100.0 * breath / n:.0f}% of tags are breath-"
                  f"family (whisper/gasp/pant/...). In context this is voice; out of")
            print(f"          context it is register flattening. Check the scenes, not the table.")
            printed = True
        heavy = {ch: (nt, b) for ch, (nt, b) in per_ch[speaker].items()
                 if nt >= 3 and b / nt >= 0.5}
        if heavy:
            listed = ", ".join(f"ch-{ch} {b}/{nt}"
                              for ch, (nt, b) in sorted(heavy.items(),
                                                       key=lambda kv: int(kv[0])))
            print(f"   --   V2  {speaker} breath-heavy chapters: {listed}")
            print(f"          The map the register question needs: are these the intimate")
            print(f"          scenes? A breath-heavy chapter that is not is the field failure.")
            printed = True
    if not printed:
        print("   --   V2  no collapse, no shared top tags at the listing lines.")
    print()
    print("  V1/V2 REPORT-ONLY. The listing lines are parameters, not caps: no published")
    print("  per-character tag distribution has been measured, so no per-character")
    print("  threshold exists. V3 is the measured row. Compare this table against")
    print("  voice-matrix.md yourself - that comparison is Phase 3.1 (`register`), and a")
    print("  spec the manuscript never verifies is a wish.")
    return failed


def main():
    args = sys.argv[1:]
    targets = []
    if args:
        for arg in args:
            directory = resolve(arg)
            if not directory:
                print(f"check-dialogue-tags: no chapters found under {arg}")
                return 1
            targets.append((arg, directory))
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for directory in sorted(glob.glob(os.path.join(root, "*", "manuscript", "chapters"))):
            targets.append((os.path.basename(os.path.dirname(os.path.dirname(directory))),
                            directory))

    checked = 0
    failures = 0
    for label, directory in targets:
        chapters = load(directory)
        if not chapters:
            continue
        checked += 1
        failures += check(label, chapters)
        print()

    if checked == 0:
        print("check-dialogue-tags: nothing checkable - an empty read reports nothing.")
        return 2
    print(f"DIALOGUE-TAG REPORT DONE - {checked} manuscript(s) read, "
          f"{failures} V3 failure(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
