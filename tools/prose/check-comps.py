#!/usr/bin/env python3
"""check-comps.py - was every comp title checked against a source before it was used?

WHY THIS EXISTS
  During Phase 1 of one book, four of the six comp titles in market-research.md turned out
  to be fabricated. Steve Yarbrough's *The Bureau of Missing Persons* does not exist; the
  title returns only a 1933 Bette Davis film, and the entry had been flagged "closest comp,
  confidence: high". Peter Ho Davies' *The Dying Light* and the series "Devils and Dusters"
  do not exist either - the author is real and his four novels are documented. Two more
  were real but had the wrong year, the wrong genre and the wrong description.

  Nothing about that was a failure of diligence. The verification was performed, and it
  was *good* - it caught all four, with evidence. The failure was one of ORDER: the
  fabricated titles were in the file first, marked "closest comp, confidence: high", and
  were only corrected after a human went looking. A premise is scoped against a comp set.
  If the comp set contains invented books, the premise is scoped against nothing, and no
  amount of later verification repairs the hours of reasoning that were built on it.

  The one that actually mattered was found the same way, by accident: Tom Baragwanath's
  *Paper Cage* is precisely a small-town professional uncovering an old disappearance, and
  the slot the new book wanted was already occupied. That is the failure this gate exists
  to prevent, and it is a *false negative* - a comp that exists and was missed - which no
  stamp in this file can detect. See the closing section.

WHAT IT MEASURES
  Every comp row in the research file must carry a verification line:

      | Author, *Title* (year) | **VERIFIED** 2026-09-28 - publisher, ISBN; comp slot |

  and must be either VERIFIED or explicitly marked as a falsification. A row that is
  neither is unverified, and this gate fails.

WHAT IT DOES NOT CLAIM
  It cannot tell a real book from an invented one. Nothing can, at this level, without
  consulting a catalogue. It checks that a human wrote down a date and a source; that is
  the entire claim, and the entire limit. A stamp is a witness, not a proof - and a
  fabricated citation with a stamp on it passes, exactly as a fabricated comp did before
  it was checked.

  Critically, it CANNOT catch the inverse error, which is the one that burns hardest: a
  real, famous, on-point comp that nobody thought of. Paper Cage was missed while four
  fabricated titles were present - the research was busy being wrong about books that did
  not exist, and had no attention left for the one that did. This gate makes the first
  error rarer and does nothing for the second. The second needs a different instrument.

USAGE
    python check-comps.py <book-dir> [--strict]
    Exit 0 pass, 1 unverified comps, 2 research file missing or unreadable.
"""

import argparse
import os
import re
import sys

VERIFIED = re.compile(r"\bVERIFIED\b", re.I)
FALSIFIED = re.compile(r"\b(DOES NOT EXIST|FALSIFIED|DISCONFIRMED)\b", re.I)
ROW = re.compile(r"^\s*\|(.+)\|\s*$")
# a comp row: a cell containing an italicised title, or a year in parentheses
COMPY = re.compile(r"\*[^*]+\*|\(\d{4}\)")

# THE COMP TABLE, and nothing else.
#
# The first version of this gate scanned every table row in the file and guessed which
# ones were comps. On the real research file that flagged four rows from the RISK REGISTER
# - a table of conclusions, not citations - while passing the actual comp table only
# because those rows happened to be stamped already. Guessing was wrong in both
# directions at once, and a gate that flags the risk register teaches its reader to
# ignore it.
#
# A comp table is a markdown table whose first header cell names a book-shaped column.
# Requiring that is stricter (a conclusions table is ignored rather than adjudicated) and
# it removes the guesswork entirely: the author writes the table, this gate reads it.
COMP_HEADER = re.compile(r"^\**\s*(recalled|comp|comps|comparables?|comparable|"
                          r"title|titles|book|books)\s*\**\s*:?\s*$", re.I)


def find_research(book):
    r = os.path.join(book, "research")
    if not os.path.isdir(r):
        return None
    for name in ("market-research.md", "comp-titles.md", "bestseller-dna.md"):
        p = os.path.join(r, name)
        if os.path.isfile(p):
            return p
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("book")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    book = os.path.abspath(args.book)
    if not os.path.isdir(book):
        print(f"check-comps: no such book directory: {book}", file=sys.stderr)
        return 2
    path = find_research(book)
    if not path:
        print("check-comps: no research/market-research.md in this book. Nothing to "
              "verify, and no comp set recorded either - which is the same finding.",
              file=sys.stderr)
        return 2

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    # locate the comp table by its header row, then judge only the rows inside it
    in_comp_table, table_seen, table_start = False, False, 0
    comps = []
    for i, line in enumerate(lines, 1):
        m = ROW.match(line)
        if not m:
            in_comp_table = False
            continue
        body = m.group(1)
        if set(body.strip()) <= set("-: "):
            continue  # separator belongs to the table just opened
        if not in_comp_table:
            cells = [c.strip() for c in body.split("|")]
            # MATCH THE WHOLE CELL, not a word inside it.
            #
            # The first version searched for /\btitle\b/ anywhere in the first cell, and a
            # risk-register row reading "| Something with *An Italic Title* in it |" re-
            # anchored the gate onto the risk table. It reported 0 unverified and exited
            # 0 while no longer watching the comp table at all - a silent false pass, the
            # worst failure mode this suite has. A header cell is a short label, so the
            # whole cell must be the label.
            if len(cells) >= 2 and COMP_HEADER.match(cells[0]):
                in_comp_table, table_seen, table_start = True, True, i
            continue
        first = body.split("|")[0].strip()
        if not COMPY.search(body):
            continue
        label = re.sub(r"\s+", " ", first)[:60]
        if VERIFIED.search(body) or FALSIFIED.search(body):
            continue
        comps.append((i, label))

    print(f"check-comps: {os.path.basename(book)} - {os.path.relpath(path, book)}")
    if not table_seen:
        print("  no comp table found (looking for a markdown table whose first header cell")
        print("  reads 'recalled' / 'comp' / 'title'). A research file with no comp table "
              "has no comp")
        print("  set, and a premise scoped against no comp set is scoped against nothing.")
        return 1
    n_ok = sum(1 for line in lines if VERIFIED.search(line) or FALSIFIED.search(line))
    print(f"  comp table: line {table_start} | stamped rows in file: {n_ok} | "
          f"unverified: {len(comps)}")
    print()
    bad = []
    for lineno, title in comps:
        bad.append(f"line {lineno}: {title} - no VERIFIED line and no falsification note")
        print(f"  UNVERIFIED  line {lineno}: {title}")

    if bad:
        print("\nCOMP VERIFICATION MISSING - a comp title has no source and no date.")
        print("  Every comp in the set needs one of:")
        print("    **VERIFIED** 2026-09-28 - publisher, ISBN; which slot it fills")
        print("    **DOES NOT EXIST** - what was searched, and what IS by that author")
        print("  A falsified comp that is marked is a good outcome. It is a comp that was")
        print("  never checked that is the failure - the premise is scoped against it.")
        return 1

    print("COMP CHECK OK - every comp row carries a verification stamp or a recorded "
          "falsification.")
    print("  A stamp is a witness, not a proof: this gate cannot tell a real book from an "
          "invented")
    print("  one, and a fabricated citation with a stamp on it passes. It also cannot see "
          "a real")
    print("  comp nobody thought of, which is the error that costs the most.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
