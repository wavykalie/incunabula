#!/usr/bin/env python3
"""check-quantities.py - do the numbers in this book agree with each other?

WHY THIS EXISTS
  A book can invite hard-SF reading through its texture and then break its own numbers:
  a character standing under "eight gravities" (a human would be paste; magnetic boots
  do not help), a 60,000-ton station moved "in a fraction of a second" on thrust
  figures that do not cohere. No gate in this directory extracts or reasons about
  quantities at all. This is the cheap first pass: pull every number-with-a-unit out of
  each chapter, show the spread per unit, flag direct contradictions where the same
  quantity is stated two ways, and print a short table of physical sanity notes.

WHY IT REPORTS AND NEVER GATES
  Two reasons, and the second one is the interesting one.
  1. There is no corpus measurement of quantity coherence in published prose, so no
     cap exists, and this directory sets no threshold from an unmeasured number.
  2. Extraction is lossy: it cannot see what a number APPLIES TO. "Eight gravities" on
     a nozzle skirt and "eight gravities" of engine acceleration are the same span and
     different situations. A gate that cannot see the referent would fail correct prose
     for a coincidence of units.

  So every row is an OBSERVATION with its contexts attached. The sanity notes (Q3) are
  the one place physics rather than prose supplies the number: a standing human is
  incapacitated well below 5g and near 8g is not survivable for the duration described.
  Those are facts about bodies, not thresholds derived from a corpus - which is exactly
  why they are printed as notes for a reader and not as a failure line.

WHAT IT CANNOT DO
  It cannot resolve what a quantity modifies. It cannot check dimensional consistency
  of a derived figure (thrust vs. mass vs. acceleration) - that is an evaluator's job
  (proof-panel's Hostile already hunts "dubious data"). It treats a range ("forty to
  fifty hours") as its first number, and it counts a year ("in 1919") as a number with
  no unit only when spelled or followed by a known unit. A contradiction it reports may
  be a change over time rather than an error - the chapter context is attached so a
  reader can tell. Q4's noun extraction is crude about which noun a number modifies
  (adjectives, compound heads, and appositives are guessed at), and parts of a stock
  SUM - four taken and thirty-six left can be forty against a promised fifty - so Q4
  names candidates and RECONCILE pairs, and the reader does the arithmetic. The
  canister case is exactly why: the row cannot tell "four of fifty" from "forty of
  fifty"; it can only insist somebody checks.

ROWS (all report-only; the tool exits 0 on any content)
  Q1  extracted quantities per chapter (grouped by unit, with context)
  Q2  same-unit spread observations (values differing by 100x or more)
  Q3  physical sanity notes (g-force on bodies, and anything a reader would catch)
  Q4  counted-noun conflicts - the same counted noun carrying different values
      across the book ("fifty canisters" in ch 3 against "four" and "thirty-six"
      in ch 6), with a RECONCILE line when two values are close but not equal,
      which is the shape a stock stated two ways takes

EXIT CODES
  0  ran and reported (findings or not - findings are never a failure here)
  1  nothing checkable: a report from an empty read proves nothing

usage:  tools/prose/check-quantities.py [BOOK_DIR_OR_CHAPTER_DIR ...]
"""

import glob
import os
import re
import sys
from collections import defaultdict

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)

SPELL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
         "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
         "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
         "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
         "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000}

UNITS = (r"kg|g|mg|tonnes?|tons?|kilos?|meters?|metres?|m|km|cm|mm|kilometers?|"
         r"kilometres?|hours?|hrs?|h|minutes?|mins?|seconds?|secs?|s|days?|weeks?|"
         r"months?|years?|gravities|gravity|atm|rpm|%|percent|kPa|psi|AU|hertz|hz|"
         r"mph|kph|km/h|m/s|pulses?|beats?|degrees?|celsius|fahrenheit|kelvin|"
         r"watts?|kW|MW|volts?|amps?|liters?|litres?|litres|litre|liter")
MODIFIER = r"(?:\s+(?:metric|imperial|square|cubic|nautical|linear))?"
MODIFIER_WORDS = {"metric", "imperial", "square", "cubic", "nautical", "linear"}
# Heads that are grammar, not nouns. The counted-noun extractor is crude by design
# (it cannot see which noun a number modifies), so it skips closed-class words rather
# than trying to parse.
STOP_HEADS = {"of", "and", "or", "the", "a", "an", "in", "on", "at", "to", "for",
              "by", "with", "more", "less", "other", "others", "than", "that",
              "this", "these", "those", "its", "his", "her", "their", "my", "our",
              "from", "into", "over", "under", "about", "around"}
# Adjectives that sit between a number and its noun: "two corporate gun-cutters".
HEAD_ADJ = {"corporate", "military", "medical", "full", "half", "double", "single",
            "extra", "last", "next", "first", "second", "third", "whole", "empty",
            "sealed", "spare", "dead", "live", "small", "large", "big", "little"}
# A number phrase, not a number token. The first version of this file matched ONE
# word, so "sixty thousand tons" matched at "thousand" and read as 1,000 tons, and
# "forty-two degrees" matched at "two" and read as 2 degrees - both found by running
# the tool on the book the critique examined and reading what it said. Spelled numbers
# carry their magnitude word, and hyphenated tens-units are one number.
WORDNUM = "|".join(sorted(SPELL, key=len, reverse=True))
NUM = (r"(?:\d+(?:[.,]\d+)?|"
       r"(?:" + WORDNUM + r")(?:[- ](?:" + WORDNUM + r"))*)")
QUANTITY = re.compile(rf"\b({NUM}){MODIFIER}\s*({UNITS})\b", re.I)
G_FORCE = re.compile(rf"\b({NUM})\s*(gravities|gravity|g(?:'s)?)\b", re.I)
# Q4: a number with a NOUN head rather than a unit - "fifty canisters", "nine turns".
# Up to two words are captured so modifier/adjective cases can be resolved or skipped.
COUNT = re.compile(rf"\b({NUM})\s+([A-Za-z][A-Za-z-]*)(?:\s+([A-Za-z][A-Za-z-]*))?", re.I)


def counted_head(w1, w2):
    """The noun a count applies to, or None if the span is a unit phrase or grammar."""
    w1, w2 = (w1 or "").lower(), (w2 or "").lower()
    if not w1 or w1 in STOP_HEADS:
        return None
    if re.fullmatch(UNITS, w1, re.I):
        return None                       # a unit phrase; Q1 already has it
    if w1 in MODIFIER_WORDS and w2 and re.fullmatch(UNITS, w2, re.I):
        return None                       # "twenty metric tons"
    if w2 and re.fullmatch(UNITS, w2, re.I):
        return None                       # a unit with an adjective in front
    head = w2 if (w1 in HEAD_ADJ and w2) else w1
    if head in STOP_HEADS or re.fullmatch(UNITS, head, re.I):
        return None
    if head.endswith("ss"):
        return head
    return head[:-1] if head.endswith("s") else head

MAGNITUDE = {"hundred": 100, "thousand": 1000, "million": 1000000}


def value_of(phrase):
    """'sixty thousand' -> 60000, 'forty-two' -> 42, '2,400' -> 2400. None on junk."""
    t = str(phrase).lower().replace(",", "")
    if re.fullmatch(r"\d+(?:\.\d+)?", t):
        return float(t)
    total = 0
    for word in re.split(r"[- ]+", t):
        if not word:
            continue
        if word in MAGNITUDE:
            total = (total or 1) * MAGNITUDE[word]
        elif word in SPELL:
            total += SPELL[word]
        else:
            return None
    return float(total) or None


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


def clip(s, n=100):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[:n - 1] + "\u2026"


def context(text, start, end):
    a = max(0, start - 60)
    b = min(len(text), end + 60)
    return clip(("..." if a else "") + text[a:b] + ("..." if b < len(text) else ""))


def check(label, chapters):
    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters")
    print("=" * 67)
    by_unit = defaultdict(list)   # unit -> [(value, chapter, context)]
    by_noun = defaultdict(list)   # counted noun -> [(value, chapter, context)]
    g_hits = []
    for name, text in chapters:
        for m in QUANTITY.finditer(text):
            v = value_of(m.group(1))
            if v is None or v == 0:
                continue
            unit = m.group(2).lower()
            by_unit[unit].append((v, name, context(text, m.start(), m.end())))
        for m in COUNT.finditer(text):
            v = value_of(m.group(1))
            if v is None or v == 0:
                continue
            head = counted_head(m.group(2), m.group(3))
            if head:
                by_noun[head].append((v, name, context(text, m.start(), m.end())))
        for m in G_FORCE.finditer(text):
            v = value_of(m.group(1))
            if v is not None and v >= 4:
                g_hits.append((v, name, context(text, m.start(), m.end())))

    if not by_unit:
        print("   --   Q1  no number-with-a-unit spans found.")
        print()
        print("  REPORT-ONLY. Rows cannot fail a book.")
        return 0

    print(f"\n{'unit':<12}{'mentions':>9}{'min':>10}{'max':>10}{'max/min':>10}")
    for unit in sorted(by_unit, key=lambda u: -len(by_unit[u])):
        vals = [v for v, _, _ in by_unit[unit]]
        ratio = max(vals) / min(vals) if min(vals) > 0 else float("inf")
        print(f"{unit:<12}{len(vals):>9}{min(vals):>10g}{max(vals):>10g}"
              f"{f'{ratio:g}x':>10}")
    print()
    print("   --   Q1  contexts (first 6 per unit):")
    for unit in sorted(by_unit, key=lambda u: -len(by_unit[u])):
        for v, ch, ctx in by_unit[unit][:6]:
            print(f"          [{unit} {v:g}] {ch}: {ctx}")
    print()

    spread = False
    for unit in sorted(by_unit):
        vals = by_unit[unit]
        lo = min(vals, key=lambda t: t[0])
        hi = max(vals, key=lambda t: t[0])
        if lo[0] > 0 and hi[0] / lo[0] >= 100 and len(vals) >= 2:
            spread = True
            print(f"   --   Q2  unit {unit!r} spreads {hi[0] / lo[0]:g}x "
                  f"({lo[0]:g} at {lo[1]} vs {hi[0]:g} at {hi[1]}).")
            print(f"          low : {lo[2]}")
            print(f"          high: {hi[2]}")
    if not spread:
        print("   --   Q2  no unit spreads 100x or more across the book.")
    print()

    if g_hits:
        for v, ch, ctx in sorted(g_hits, key=lambda t: -t[0]):
            print(f"   --   Q3  SANITY: {v:g} gravities at {ch}. A standing human is")
            print(f"          incapacitated well below 5g; sustained {v:g}g is not")
            print(f"          survivable for a person. Verify the referent: {ctx}")
    else:
        print("   --   Q3  no acceleration values at or above 4g found.")
    print()

    # Q4: the easy win the critique asked for first - a stock stated two ways. The
    # row cannot sum parts of a stock and cannot see referents; it names the nouns
    # whose values disagree and calls RECONCILE on the pairs that are close but not
    # equal, which is the shape a contradiction takes. A reader does the arithmetic.
    conflicts = {n: rows for n, rows in by_noun.items()
                 if len({v for v, _, _ in rows}) >= 2}
    if not conflicts:
        print("   --   Q4  no counted noun carries conflicting values.")
    for noun in sorted(conflicts):
        rows = conflicts[noun]
        vals = sorted({v for v, _, _ in rows})
        print(f"   --   Q4  '{noun}' carries {len(vals)} different values "
              f"({', '.join(f'{v:g}' for v in vals)}) across "
              f"{len({c for _, c, _ in rows})} chapter(s):")
        for v, ch, ctx in rows[:4]:
            print(f"          [{v:g}] {ch}: {ctx}")
        # RECONCILE keys on CROSS-CHAPTER restatement, not raw closeness. The
        # contradiction shape is one stock counted two ways in different places
        # ("fifty canisters" in ch 3 against a ch-6 tally); same-sentence counts like
        # "once, twice, three times, four times" are enumerations and are listed but
        # not reconciled. Found by reading the first run's output on the book the
        # critique examined: closeness flagged enumerations and missed the flagship
        # case, whose extracted values (4, 12, 50) are not close to each other at all.
        def cross_chapter(a, b):
            return any(ca != cb
                       for va, ca, _ in rows if va == a
                       for vb, cb, _ in rows if vb == b)

        pairs = sorted(((a, b) for i, a in enumerate(vals) for b in vals[i + 1:]
                        if cross_chapter(a, b)), key=lambda p: -(p[0] + p[1]))[:2]
        for a, b in pairs:
            print(f"          RECONCILE: {a:g} and {b:g} are restated in different")
            print(f"          chapters and do not agree - a stock counted two ways reads")
            print(f"          as a contradiction. Parts of a stock SUM (four taken plus")
            print(f"          thirty-six left), so the reader reconciles; the row only")
            print(f"          insists somebody checks.")
    print()
    print("  REPORT-ONLY. Extraction cannot see what a number applies to, so no row")
    print("  may fail a book: two same-unit values can be correct in two situations.")
    print("  Q3's numbers come from physiology, not from a prose corpus - they are")
    print("  notes for a reader, not a threshold. Dimensional coherence (thrust vs.")
    print("  mass vs. acceleration) is an evaluator judgment; proof-panel's Hostile")
    print("  already hunts 'dubious data', and this table is what it should be shown.")
    return 0


def main():
    args = sys.argv[1:]
    targets = []
    if args:
        for arg in args:
            directory = resolve(arg)
            if not directory:
                print(f"check-quantities: no chapters found under {arg}")
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
        print("check-quantities: nothing checkable - an empty read reports nothing.")
        return 1
    print(f"QUANTITY REPORT DONE - {checked} manuscript(s) read. Report rows cannot fail.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
