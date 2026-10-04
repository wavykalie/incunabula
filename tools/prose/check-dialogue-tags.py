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

WHY IT REPORTS AND NEVER GATES
  There is no corpus of per-character speech-tag distributions in published prose, so
  there is no measured population from which a cap could be derived. This directory
  sets no threshold from an unmeasured number. Everything printed below is an
  OBSERVATION with its counts attached; the rows cannot fail a book. Closing the
  voice-matrix loop is a reader's judgment - this tool supplies the table the
  judgment needs.

WHAT IT CANNOT DO
  It attributes by name within a short window of the quote; a tag with a pronoun
  ("she said") is unattributed and counted separately, so a chapter that tags every
  line with a pronoun reports few attributed lines. It reads quoted spans, so a
  quoted letter or sign counts as speech (the same limit `check-surplus.py` records).
  It cannot see a character whose voice lives in diction and syntax rather than tags -
  the tag layer is the cheapest slice, not the whole instrument. And it cannot read
  `voice-matrix.md`; comparing the table against the spec is the reader's step,
  which is where `register` (Phase 3.1) sends it.

ROWS (all report-only; the tool exits 0 on any content)
  V1  per-character tag table: tagged lines, distinct verbs, top verb + share,
      breath-family share (whisper, gasp, breathe, pant, murmur, moan, sigh, ...)
  V2  observations: shared top verbs between characters, tag collapse, and the
      unattributed share

EXIT CODES
  0  ran and reported (findings or not - findings are never a failure here)
  1  nothing checkable: a report from an empty read proves nothing

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


def is_name_candidate(word, lowercase_words):
    return word not in COMMON_NOISE and word.lower() not in lowercase_words


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
            verbs[speaker or "(unattributed)"][verb] += 1

    if not verbs:
        print("   --   V1  no tagged dialogue found. Either the book is not dialogue-")
        print("          driven or the tags sit outside the attribution window.")
        print()
        print("  REPORT-ONLY. Rows cannot fail a book; no per-character corpus exists.")
        return 0

    print(f"\n   --   V1  per-character speech-tag distribution "
          f"({sum(sum(c.values()) for c in verbs.values())} tagged spans):")
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
    if not printed:
        print("   --   V2  no collapse, no shared top tags at the listing lines.")
    print()
    print("  REPORT-ONLY. The listing lines are parameters, not caps: no published")
    print("  per-character tag distribution has been measured, so no threshold exists.")
    print("  Compare this table against voice-matrix.md yourself - that comparison is")
    print("  Phase 3.1 (`register`), and a spec the manuscript never verifies is a wish.")
    return 0


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
    for label, directory in targets:
        chapters = load(directory)
        if not chapters:
            continue
        checked += 1
        check(label, chapters)
        print()

    if checked == 0:
        print("check-dialogue-tags: nothing checkable - an empty read reports nothing.")
        return 1
    print(f"DIALOGUE-TAG REPORT DONE - {checked} manuscript(s) read. Report rows cannot fail.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
