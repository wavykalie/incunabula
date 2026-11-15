#!/usr/bin/env python3
"""check-agency.py - an inanimate subject doing a mind's work, and the clause that
explains why nothing had to happen.

WHY THIS EXISTS
  Two constructions recur in machine-written prose, and no row in `deslop-check.sh`
  sees either of them:

    object agency      "The walls remembered." "The room wanted to be left alone."
                       "Because the walls remembered..." An object is given memory,
                       want, decision or listening - the mind's verbs in a thing's
                       mouth. Adjacent rows do not cover it: `A5` wants "is not just",
                       `A24` wants "which is why", `A25` wants the "not X. It was Y."
                       frame. None of them reads subject position.

    motive by absence  "Because it didn't need to." "She didn't answer, because there
                       was no reason to." A motive is assigned to something NOT
                       happening, so the sentence explains an absence instead of
                       showing an act. This is the coda habit (`A24`, `F1`) applied
                       mid-sentence, where no row looks.

  The author asked for it in these words: "I always hear in these books written like
  'This object Remembered' Or 'Because the walls remembered' or 'Because it didn't
  need to X'."

WHY IT REPORTS AND NEVER GATES
  Measured 2026-11-14 over every corpus installed in this checkout - 4,531,815 words
  of published prose across six registers, plus the study's three arms and two project
  books. The object-agency numbers:

    human: elaina 0.01/1k, montgomery 0.01, action-voice 0.01, multivolume 0.00,
           nonfiction 0.00, prescriptive 0.01   (23 hits in 4,531,815 words = 0.005/1k)
    AI:    naive 0.01, pipeline 0.02, a demo book 0.07, the two project books 0.09

  Zero tolerance is impossible, and not because the number is small: the published
  hits are deliberate. Montgomery writes "the fire refused to burn"; Muir writes
  "The city knows. It remembers. Its past is written in its bones"; Child writes "The
  car waited, idling at the curb." A hard row would fail *Anne of Green Gables* and
  *Gideon the Ninth* - the same failure that demoted `A1a`, `A2a`, `A3a`, `A19` and
  `A21` to a density tier.

  A density cap is worse than useless at this precision. The worst human document
  reads 0.37/1k, so the directory's 1.5x convention puts the cap at ~0.55/1k, and
  every manuscript measured passes it - the highest AI chapter was 0.81 in a demo
  book, and the two project books peak at 0.50. A cap that clears published prose
  everywhere and clears the machine everywhere is a gate in name only, and its green
  result would be read as evidence. That is the `D1`/`D2` finding exactly.

  The second row is the one that separated: the causal, non-human form ("because it
  didn't need to", "since there was no reason") read **0.00/1k in all six human
  corpora** and non-zero in three AI arms (a demo book 0.04, the pipeline arm 0.01).
  That is the shape of a zero-tolerance rule, and it is the only reason this tool
  exists as a candidate rather than a curiosity. But it is ten hits, and a row in the
  scanner is a freeze event with a cap derived from a lane. Ten hits is a hypothesis.
  So the tool prints both rows, a reader rules, and the decision to open that freeze
  belongs to the author.

  The courtesy form is excluded on purpose. "You didn't have to" is ordinary dialogue
  in every arm, the published ones included, and a row that prints it is a row its
  reader learns to skip. R2 therefore requires a subject that is not a person: a
  person as subject means someone chose something, which is not this construction.

WHAT IT CANNOT DO
  It cannot tell an object that acts from an object a person acts on. It requires a
  determiner before the noun and refuses a relative pronoun, coordinator or copula
  between the noun and the verb - and still counts "the rooms you wanted" and "a room
  I remembered". Measured: of 23 hits in the human corpora, about a third are genuine
  ("the fire refused to burn", "those stones shall forget me", "her body knew what to
  do"); the rest are people doing things near a noun. In the two project books 10 of
  12 were genuine - the reverse ratio, which is why the rate is a pointer and not a
  finding.

  It cannot see an object without a determiner ("Marrow remembered"), a proper-noun
  subject, a place name, or any noun outside its list. The list IS the instrument, in
  VERMILLION's sense: a different list gives different numbers. It cannot separate a
  courtesy from a motive except by the subject's not being a person, so "He didn't have
  to explain" is invisible to R2 whether it is a courtesy or the tic. It cannot tell a
  deliberate motif from a tic - a book that writes "the hall knows" ten times may mean
  it, and this tool would say so ten times. Whether a passage earns its personification
  is a reader's question, and `proof-panel` is where a reader answers it.

ROWS (all report-only; the tool exits 0 on any content)
  R1a place agency       determiner + place or building part + mind verb, with at most
                         one intervening adverb; not after a preposition, not across a
                         relative pronoun or coordinator. "The hall waited."
  R1b object agency      the same construction where the subject is a thing rather
                         than a setting - a clock, a letter, a machine. "The car
                         waited, idling at the curb."
  R2  motive by absence  non-human subject + "did not need to / matter / point /
                         reason", named causally ("because/since") or as a whole
                         sentence ("It didn't need to be said.")

WHY R1 IS SPLIT IN TWO
  The row was asked for as object agency, and measured over this checkout's 18
  manuscripts it returned fifteen hits with no object in any of them: hall x5, room x3,
  town x2, street x2, ceiling, office, House. Every carrier was the setting itself. A
  single number would have reported fifteen object hits and been wrong fifteen times
  about what the books were doing. The two figures are not the same move and do not
  deserve the same reading: a hall given a mind is the genius loci, a device with a
  tradition behind it and usually a chorus in front of it, while a clock given a mind is
  a stranger claim and materially rarer. Counting them apart costs one regex and stops
  the tool from answering a question nobody asked.

EXIT CODES
  0  ran and reported (findings or not - findings are never a failure here)
  1  nothing checkable: a report from an empty read proves nothing

usage:  tools/prose/check-agency.py [BOOK_DIR_OR_CHAPTER_DIR ...]
"""

import glob
import os
import re
import sys

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)

# Same sentence splitter as check-arc.py / check-figurative.py, so a sentence quoted
# here is the same unit the other report tools quote.
SENT_END = re.compile(r"(?<=[.!?])[\"')\]]*\s+")
ABBREV = re.compile(
    r"\b(?:Mr|Mrs|Ms|Dr|Prof|St|Sir|Lord|Lady|Capt|Col|Gen|Rev|Hon|Sgt|Lt|"
    r"vs|etc|i\.e|e\.g|No|Vol|pp|Fig|Jr|Sr|Esq)\.", re.I)

DETERMINER = r"(?:the|a|an|its|his|her|their|this|that|these|those|every|each)"

# The inanimate subjects that actually carry this figure in English narrative. Not a
# closed set of things that cannot think - a lexicon, and the docstring says so.
#
# Split in two, because the figure is not one figure. PLACE is the setting: the room,
# the street, the town, the building a scene happens inside. THING is a discrete
# article: a clock, a letter, a machine, a bone. The line is drawn at whether the noun
# can stand for the scene itself. A wall is the room, so it goes in PLACE; a brick is a
# brick, so it goes in THING. Materials and fittings (timber, tile, wallpaper) sit with
# the things for the same reason - nobody says "the tile remembered" about the room.
PLACE = (
    r"(?:wall|walls|room|rooms|house|kitchen|floor|floors|ceiling|stair|stairs|stairwell|"
    r"door|doors|window|windows|city|cities|town|street|streets|river|water|sea|wood|woods|"
    r"earth|ground|hill|hills|garden|field|fields|forest|mountain|church|track|tracks|"
    r"road|roads|bridge|station|hotel|office|corridor|hall|hallway|porch|roof|chimney|"
    r"gate|gates|fence|hedge|sky)")
THING = (
    r"(?:silence|air|dark|darkness|light|lamplight|candlelight|timber|stone|stones|"
    r"bell|bells|machine|engine|car|train|bone|bones|blood|body|hand|hands|skin|scar|"
    r"scars|letter|letters|photograph|photographs|paint|brass|iron|steel|desk|chair|bed|"
    r"table|carpet|curtain|curtains|shelf|cupboard|heater|boiler|pipe|pipes|wire|wires|"
    r"wallpaper|tile|tiles|brick|bricks|beam|beams|rafter|rafters|tree|trees|leaf|leaves|"
    r"grass|loam|vellum|paper|page|pages|map|maps|mirror|glass|clock|fire|smoke|dust|"
    r"rain|wind|snow|shadow|shadows)")

# What only a mind does. Perception and volition, not motion: "the door opened" is
# not this row, and adding motion verbs is what would make it count all prose.
MIND = (
    r"(?:remember|remembers|remembered|forget|forgets|forgot|forgotten|knew|knows|"
    r"wanted|wants|refused|refuses|decided|decides|insisted|demanded|chose|chooses|"
    r"understood|understands|believed|believes|learned|learnt|preferred|hated|"
    # "meant" is deliberately absent: "the street meant the walk back" is a road
    # signifying a route, which is ordinary English and was a false positive on the
    # first scan of the project book.
    r"loved|feared|resented|forgave|blamed|listened|listens|"
    r"watched|watches|waited|waits|allowed|allows)")

# The gap guard. Without it the row reads relative clauses ("the room I remembered"),
# possessives and coordinated subjects as agency - measured, that was most of the
# false positives, and it is why R1's precision is only about a third on human prose.
FUNCTION = (
    r"(?:that|which|who|whom|whose|where|when|and|or|but|was|were|is|are|be|been|"
    r"being|to|of|for|with|by|from|had|has|have|me|him|her|them|us|than|as|"
    r"if|because|while|so|not|also|"
    # pronouns: "a room he means" is a relative clause, not a room with a mind. This
    # was missing in the first version and the project book's own chapter 7 caught it.
    r"she|he|they|I|you|we|it)")

# Same construction, two lexicons, two rows. The two lists are disjoint, so no match
# can be counted twice and the totals still add up to the single number this tool
# reported before the split (15 in this checkout: 15 place, 0 thing).
R1_PLACE = re.compile(
    rf"\b{DETERMINER}\s+{PLACE}\b(?:\s+(?!{FUNCTION}\b)\w+)?\s+{MIND}\b", re.I)
R1_THING = re.compile(
    rf"\b{DETERMINER}\s+{THING}\b(?:\s+(?!{FUNCTION}\b)\w+)?\s+{MIND}\b", re.I)

# Two spellings of the same move.
#
# "You didn't have to" is a courtesy, and it is ordinary dialogue in every arm,
# published ones included. A row that prints it is a row its reader learns to skip, so
# the UNCAUSED form is excluded by subject: with no "because" in the sentence, only a
# non-human subject is the construction ("It didn't need to be said"), because a person
# as subject there means someone chose something, which is not this row.
#
# CAUSAL names the cause, and takes ANY subject: "She did not answer, because she
# didn't need to" is the tic in its most common form. The cause is the signal here, not
# the subject - and the causal frame is the one that measured 0.00/1k across six
# published registers, people included.
CAUSAL = re.compile(
    r"\b(?:because|since)\b[^.!?]{0,60}?"
    r"\b(?:did|does|do|would|could|had|has|have)(?:n't| not| never)\b"
    r"[^.!?]{0,40}?\b(?:need|needed|have to)\b", re.I)
# "because there was no reason", "since there was no need" - the same move with a noun
# of absence instead of a verb of need. Kept apart from CAUSAL on purpose: allowing bare
# "matter" / "point" / "reason" as the verb matches ordinary sentences, and measured
# one the moment it was allowed - the demo book's "a room where a date mattered" is a
# date that counted, not a motive assigned to an absence.
CAUSAL_NONE = re.compile(
    r"\b(?:because|since)\b[^.!?]{0,60}?"
    r"\b(?:there|it)\b[^.!?]{0,20}?\b(?:was|were|is|are)\b[^.!?]{0,10}?"
    r"\bno\b[^.!?]{0,10}?\b(?:need|reason|point|call)\b", re.I)
# BARE is the same move as a whole sentence: "It didn't need to be said."
BARE = re.compile(
    r"\b(?:it|that|this|there|nothing|nobody)\b(?:\s+(?!\b(?:she|he|they|I|you|we)\b)\w+){0,2}"
    r"\s+(?:didn't|did not|doesn't|does not|never)\s+(?:need|needed|have|had)\s+to\b", re.I)

# A noun after a preposition is a complement, not a subject: "not a man in that hall
# knows my face" is a man knowing a face. Python lookbehind cannot span the optional
# determiner, so the guard is applied to the text before each match instead.
PREP_TAIL = re.compile(
    r"\b(?:in|on|at|to|of|for|with|from|by|under|over|through|near|behind|against|"
    r"into|across|beside|within|outside|round|around|about)\s+(?:the\s+|a\s+|an\s+|that\s+|"
    r"this\s+|its\s+|his\s+|her\s+|their\s+)?$", re.I)


def load(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if CHAPTER.search(name):
            with open(os.path.join(directory, name), encoding="utf-8", errors="ignore") as fh:
                out.append((name, fh.read()))
    return out


def resolve(arg):
    for candidate in (arg, os.path.join(arg, "manuscript"),
                      os.path.join(arg, "manuscript", "chapters")):
        if os.path.isdir(candidate) and any(CHAPTER.search(n) for n in os.listdir(candidate)):
            return candidate
    return None


def clip(s, n=110):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n - 1] + "\u2026"


def sentence_at(text, pos):
    """The sentence around a match, taken from the raw text so offsets stay honest.
    Abbreviations can split a quoted sentence short; a quote is a place to look, not
    a transcription."""
    start = 0
    for m in SENT_END.finditer(text, 0, pos):
        start = m.end()
    m = SENT_END.search(text, pos)
    end = m.start() if m else len(text)
    return text[start:end]


def observations(text):
    """[(row, matched phrase, sentence)] in reading order. A match already covered by
    an earlier one is not printed twice, and an object in a prepositional phrase is not
    a subject."""
    found = []
    for row, rx in (("R1a", R1_PLACE), ("R1b", R1_THING)):
        for m in rx.finditer(text):
            if PREP_TAIL.search(text[max(0, m.start() - 24):m.start()]):
                continue
            found.append((m.start(), row, m.group(0)))
    spans = []
    for rx in (CAUSAL, CAUSAL_NONE, BARE):
        for m in rx.finditer(text):
            if any(m.start() < b and a < m.end() for a, b in spans):
                continue
            spans.append((m.start(), m.end()))
            found.append((m.start(), "R2", m.group(0)))
    # Reading order, not row order: the report is read as prose.
    found.sort(key=lambda h: h[0])
    return [(row, phrase, sentence_at(text, pos)) for pos, row, phrase in found]


def check(label, chapters):
    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters")
    print("=" * 67)
    WHAT = {"R1a": "place agency", "R1b": "object agency", "R2": "motive by absence"}
    counts = {"R1a": 0, "R1b": 0, "R2": 0}
    chapters_with_hits = 0
    for name, text in chapters:
        hits = observations(text)
        if not hits:
            continue
        chapters_with_hits += 1
        for row, _, _ in hits:
            counts[row] += 1
        print(f"\n--- {name}   {len(text.split())} words")
        for row, phrase, sent in hits:
            print(f"   --   {row}  {WHAT[row]:18} {clip(phrase, 70)!r}")
            print(f"          {clip(sent)!r}")
        print(f"\n   --   {len(hits)} observation(s) in this chapter")
    total = sum(counts.values())
    print()
    if not total:
        print("   --   none of the three constructions appeared in this book.")
    else:
        print(f"   --   {total} observation(s) in {chapters_with_hits} of {len(chapters)} "
              f"chapters  (place {counts['R1a']}, object {counts['R1b']}, "
              f"motive-by-absence {counts['R2']}).")
    print()
    print("  REPORT-ONLY. No cap exists for either row and none is invented here.")
    print("  Published prose does R1 on purpose - Montgomery's \"the fire refused to")
    print("  burn\", Muir's \"The city knows. It remembers.\" - so a hard row would fail")
    print("  books that are better than anything this gate will ever see, and a cap at")
    print("  the directory's 1.5x convention (about 0.55/1k) passes every manuscript")
    print("  measured. R2 is the row with a zero in published prose; it is ten hits,")
    print("  which is a hypothesis, not a measurement, and promoting it is a freeze")
    print("  event that belongs to the author. A hit here means: read the passage.")
    print("  R1a and R1b are counted apart because a hall with a mind is a setting")
    print("  speaking and a clock with a mind is an object speaking: the first is a device")
    print("  and the second is a claim, and only the second was ever in the brief.")
    return counts


def main():
    args = sys.argv[1:]
    targets = []
    if args:
        for arg in args:
            directory = resolve(arg)
            if not directory:
                print(f"check-agency: no chapters found under {arg}")
                return 1
            targets.append((arg, directory))
    else:
        # Three levels up: this file lives at <root>/tools/prose/. Books live either at
        # the repository top level or under test-books/, which is where every book in
        # this install actually is - a no-argument run that finds nothing is not a
        # conservative default, it is a run that proves nothing.
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        patterns = (os.path.join(root, "*", "manuscript", "chapters"),
                    os.path.join(root, "test-books", "*", "manuscript", "chapters"))
        for directory in sorted({d for p in patterns for d in glob.glob(p)}):
            targets.append((os.path.basename(os.path.dirname(os.path.dirname(directory))),
                            directory))

    checked = 0
    tally = {"R1a": 0, "R1b": 0, "R2": 0}
    for label, directory in targets:
        chapters = load(directory)
        if not chapters:
            continue
        checked += 1
        counts = check(label, chapters)
        for row in tally:
            tally[row] += counts[row]
        print()

    if checked == 0:
        print("check-agency: nothing checkable - an empty read reports nothing.")
        return 1
    print(f"AGENCY REPORT DONE - {checked} manuscript(s) read, "
          f"{sum(tally.values())} observation(s)  (place agency {tally['R1a']}, "
          f"object agency {tally['R1b']}, motive by absence {tally['R2']}). "
          "Report rows cannot fail.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
