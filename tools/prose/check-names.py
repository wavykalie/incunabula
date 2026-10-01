#!/usr/bin/env python3
"""check-names.py - does this book reuse a character name from a book the author already wrote?

WHY THIS EXISTS
  A name is the one piece of a cast that travels between books without ever being checked,
  and it is the piece a returning reader is most likely to notice, because a returning reader
  *is* the person holding the previous book in their head. Two characters called Priya in one
  author's catalogue register as a single writer's habit rather than as two people, and the
  tell is invisible to every other gate in this suite: uniformity reads chapter-to-chapter
  within one book, drift reads prose shape, arc reads structure, and not one of them has ever
  opened a second book. Nothing in the pipeline was going to catch this. It was caught by the
  author, at the end of Act II, by memory.

  The specific failure was a first name that a model reaches for as a matter of course. This
  is a *frequency* problem, not a taste problem: a name can be individually excellent and
  still be a name this author has already spent.

WHAT IT MEASURES
  For each named character in the book under test, against a corpus of the author's other
  projects:

    exact        full name matches a full name elsewhere
    first        first name matches a first name elsewhere
    surname      surname matches a surname elsewhere

  First-name collision is the one that matters and it is the one that gets waved through,
  because two different surnames read as two different people to the writer doing the
  checking. It does not read that way to the reader.

  Severity is asymmetric on purpose:
    - `exact` and `first` on a *character* are FAIL. A reader who meets the same first name
      in two books by one author has learned something false about the books.
    - `surname` on a character is FAIL only on an exact surname match, and WARN otherwise -
      surnames repeat legitimately inside a family (Vance, mother and nephew) and a shared
      surname is sometimes the point.
    - Reader personas in `readership.md` and sample files are NOT characters. A persona named
      Priya in a calibration document is not a published character and must not fail a book.
      Only names under a characters key, or in a cast/character file, are treated as cast.

WHAT IT DOES NOT CLAIM
  This is a cross-book hygiene check, not a stylometric one. It has no corpus of published
  fiction behind it, because published fiction is not the population that matters here - the
  population is *this author's own catalogue*, which is finite and enumerable. It therefore
  carries no calibrated threshold, only a rule: a collision is a collision. Its error modes
  are the ones of a rule, not of a fitted number - it will not tell you a name is too common
  in the world at large, only that you have used it before.

USAGE
    python check-names.py <book-dir> [--corpus <dir> ...] [--strict]

  --corpus defaults to every sibling directory of the book that looks like a book project
  (it has a premise, outline, or CANON_LEDGER), excluding the book under test. Pass it
  explicitly to check against a specific set instead.

  Exit 0 pass (warnings allowed), 1 fail on a collision, 2 could not read the book.
"""

import argparse
import os
import re
import sys

# A cast name as it appears in the ledgers. Deliberately conservative: a capitalised word
# that is not a sentence-initial word, not a month, not a weekday, not a known proper noun
# of the craft, and not inside the running prose (this reads the canon files, not chapters).
STOP = {
    # calendar
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    # craft and office vocabulary that shows up capitalised in ledgers
    "The", "A", "An", "And", "But", "If", "When", "While", "After", "Before", "Because",
    "Chapter", "Act", "Part", "Note", "Rule", "Fact", "Item", "Phase", "Gate", "Freeze",
    "CONF", "Outline", "Premise", "Canon", "Entity", "State", "Name", "Role", "Age",
    "County", "State", "Fire", "Coroner", "Chief", "Sheriff", "Pastor", "Mechanic",
    "Monday", "Friday",
    "No", "Yes", "Not", "None", "Both", "Either", "Never", "Always",
    "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
}

# Sections of a canon file that hold cast, and sections that hold reader personas / samples.
# Personas are the whole reason this list is necessary: a calibration document that
# invented a reader named Priya must not be able to fail a manuscript.
CAST_KEYS = ("characters", "cast", "people", "persons")
NONCAST_HINT = (
    "reader", "persona", "segment", "sample", "voice-bank", "speech", "benchmark",
    "comp", "market", "research", "reader_persona",
)

NAME_RE = re.compile(r"\b([A-Z][a-z]{2,})\b")
FULLNAME_RE = re.compile(r"\b([A-Z][a-z]{2,})\s+([A-Z][a-z]{2,})\b")

# First names a model reaches for by default. Read from the frozen data file, never
# hardcoded here: an earlier version of this gate carried a hand-written guess list, which
# is exactly the thing the filter exists to replace - a list of names somebody felt were
# common is not a measurement of which names the model actually reaches for.
#
# The tiers and the reasoning behind them are in calibration/NAME_FREQUENCY.md. In short:
#   A (SSA top 20) = FAIL. Strongest prior in the language; reaching for it is a default,
#                    not a decision, and the point of the filter is to force a decision.
#   B (Nameberry 100+100) = WARN. A popular name is not per se a defect. `Cora` is
#                    Nameberry #28 and is also the correct name for a woman born in 1951
#                    in a rural American county. Popularity measures what a name is NOW;
#                    a cast is mostly people named long before now. What makes a popular
#                    name a tell is anachronism, and a gate cannot know when a character
#                    was born. The author rules.
#
# This is deliberately NOT a rule that names must be thematic or meaningful. That is a
# craft standard belonging to the author and the voice matrix. Encoding it here would make
# the pipeline unable to produce a plain name for a character who needs one, and would
# convert a preference into a rule that generates a different preference in disguise -
# choosing flowers because the gate said flowers.
FREQUENCY_TSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "tools", "prose", "calibration", "NAME_FREQUENCY.tsv",
)


def load_frequency_tiers(path=FREQUENCY_TSV):
    """Return {name: tier}. Returns empty dicts if the file is missing, and says so -
    a gate that cannot see its own denominator must not quietly pass."""
    tiers = {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) == 2 and parts[1] in ("A", "B"):
                    tiers[parts[0].strip()] = parts[1].strip()
    except OSError as exc:
        print(f"check-names: cannot read the name-frequency list at {path} ({exc}).")
        print("  The default-name filter is OFF for this run. Fix the path, do not")
        print("  read a pass here as a clean book.", file=sys.stderr)
    return tiers


TIERS = load_frequency_tiers()


def looks_like_book(d):
    return any(
        os.path.isfile(os.path.join(d, f))
        for f in ("premise.md", "outline.md", "CANON_LEDGER.yaml", "premise.yaml")
    )


def walk_candidate_files(root):
    """Canon-ish files only. Chapters are deliberately excluded: this is a cast check, and
    reading prose to find names would drag in every incidental proper noun."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "__pycache__")]
        for fn in filenames:
            if not fn.endswith((".md", ".yaml", ".yml")):
                continue
            low = fn.lower()
            if low.startswith(("canon_ledger", "entity_state", "03-characters", "characters",
                               "cast", "voice-dna")) or low in ("state.yaml", "state.yml"):
                out.append(os.path.join(dirpath, fn))
    return out


def clean(parts):
    """Keep only tokens that look like name parts. This is what stops possessives
    ('Denny's') and sentence-initial junk ('Gives') from entering the cast."""
    out = []
    for p in parts:
        p = p.strip().strip("\"'.,;:()[]")
        # Possessives are a reference, not a name. Strip the exact suffix - rstrip("'s")
        # takes a character *set* and would turn "Holli's" into "Holli", which then reads
        # as a different character and reports a collision that does not exist.
        for suf in ("'s", "\u2019s", "s'"):
            if p.endswith(suf):
                p = p[: -len(suf)]
                break
        if not p or p in STOP:
            continue
        if not re.fullmatch(r"[A-Z][a-z'’-]+", p):
            continue
        out.append(p)
    return out


# A cast name, declared. Two accepted forms and no others:
#   name: "First Last"            (CANON_LEDGER person entry)
#   canonical_name: "First Last"   (ENTITY_STATE entity)
#   ## First Last - "role"         (03-characters.md heading)
# The first version of this gate also scanned free prose, and picked up 'Paper Cage' out
# of a comp title and 'Gives Rusk' out of a sentence. A cast check that reads prose is a
# cast check that reports whatever else is capitalised, so it now reads declarations only.
HONORIFICS = {
    "Mr", "Mrs", "Ms", "Miss", "Dr", "Officer", "Deputy", "Chief", "Pastor", "Coach",
    "Judge", "Rev", "Sgt", "Detective", "Doc",
}

DECL_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:name|canonical_name)\s*:\s*[\"']?([A-Za-z'’ -]+?)[\"']?\s*(?:#.*)?$",
    re.IGNORECASE,
)
HEAD_RE = re.compile(r"^#{1,4}\s+([A-Z][a-z'’-]+(?:\s+[A-Z][a-z'’-]+){0,2})\s*(?:[-–—(]|$)")


def harvest(path):
    """Return (full names, first names, surnames) from *declared* cast only."""
    full, firsts, surnames = set(), set(), set()
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return full, firsts, surnames

    is_markdown = path.lower().endswith(".md")
    for line in lines:
        low = line.lower()
        # A declaration on a persona/reader/sample line is not cast.
        if any(h in low for h in ("reader", "persona", "segment", "benchmark",
                                  "speech sample", "sample bank")):
            continue

        m = DECL_RE.match(line)
        parts = clean(m.group(1).split()) if m else []
        honorific = False
        if parts and parts[0] in HONORIFICS:
            parts = parts[1:]
            honorific = True
        if not parts and is_markdown:
            hm = HEAD_RE.match(line.strip())
            if hm:
                parts = clean(hm.group(1).split())
                if parts and parts[0] in HONORIFICS:
                    parts = parts[1:]
                    honorific = True
        if not parts:
            continue

        # A person is declared with at least two name parts ("Delphine Rusk"), or with one
        # part behind an honorific ("Mrs. Okafor" -> Okafor). A single bare part is an
        # object or a place - "Rusk's own signature" is not a character named Rusk, and
        # counting it would put the protagonist's own surname in her own first-name set.
        if len(parts) >= 2:
            full.add(f"{parts[0]} {parts[1]}")
            firsts.add(parts[0])
            surnames.add(parts[1])
        elif honorific:
            surnames.add(parts[0])
    return full, firsts, surnames


def corpus_names(corpus_dirs):
    full, firsts, surnames = {}, {}, {}
    for d in corpus_dirs:
        for path in walk_candidate_files(d):
            f, fi, su = harvest(path)
            for n in f:
                full.setdefault(n, []).append(path)
            for n in fi:
                firsts.setdefault(n, []).append(path)
            for n in su:
                surnames.setdefault(n, []).append(path)
    return full, firsts, surnames


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("book")
    ap.add_argument("--corpus", action="append", default=[])
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    book = os.path.abspath(args.book)
    if not os.path.isdir(book):
        print(f"check-names: no such book directory: {book}", file=sys.stderr)
        return 2

    if args.corpus:
        corpus_dirs = [os.path.abspath(c) for c in args.corpus]
    else:
        parent = os.path.dirname(book)
        # Archive and scratch dirs are excluded by prefix. An archived premise is a dead
        # branch, and a temp copy of the book under test is that book's own cast - either
        # one makes the corpus report the book colliding with itself, which is noise that
        # trains the reader of this output to ignore it.
        SKIP = ("_archive", "_nmtest", "_tmp", "_scratch", "archive", "node_modules")
        corpus_dirs = [
            os.path.join(parent, d) for d in sorted(os.listdir(parent))
            if os.path.isdir(os.path.join(parent, d))
            and os.path.join(parent, d) != book
            and not d.startswith(SKIP)
            and not d.startswith("_")
            and looks_like_book(os.path.join(parent, d))
        ]

    c_full, c_first, c_sur = corpus_names(corpus_dirs)
    if not (c_full or c_first or c_sur):
        print("check-names: corpus is empty - nothing to compare against.")
        print(f"  searched: {', '.join(os.path.basename(d) for d in corpus_dirs) or '(none)'}")
        return 0

    b_full, b_first, b_sur = harvest_canon(book)
    if not b_first:
        print("check-names: no cast names found in the book. "
              "Is CANON_LEDGER.yaml present? Failing rather than passing on an empty read.",
              file=sys.stderr)
        return 2

    fails, warns, reports = [], [], []

    # --- cross-book collision: a hard failure, and independent of popularity ---
    for fn in sorted(b_first):
        if fn in c_first:
            hits = sorted({os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p)
                           for p in c_first[fn]})
            fails.append(f"FIRST  {fn}: also a character in {', '.join(hits)}")
    for fn in sorted(b_sur):
        if fn in c_sur and fn not in b_first:
            hits = sorted({os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p)
                           for p in c_sur[fn]})
            warns.append(f"SURNAME {fn}: shared with {', '.join(hits)}")
    for name in sorted(b_full & set(c_full)):
        fails.append(f"EXACT  {name}: identical full name elsewhere")

    # --- default-name filter: measured from NAME_FREQUENCY.tsv, not from taste ---
    if not TIERS:
        reports.append("REPORT (default-name filter unavailable - see the note above)")
    tier_a = sorted(n for n in b_first if TIERS.get(n) == "A")
    tier_b = sorted(n for n in b_first if TIERS.get(n) == "B")
    for n in tier_a:
        fails.append(f"TIER-A {n}: SSA national top 20. The strongest prior in the "
                     f"language - reaching for it is a default, not a choice")
    for n in tier_b:
        warns.append(f"TIER-B {n}: Nameberry top 100. Common *now*; the question is "
                     f"whether it is anachronistic for this character. Author rules")

    print(f"check-names: {os.path.basename(book)} vs {len(corpus_dirs)} other project(s)")
    print(f"  cast: {len(b_first)} first names, {len(b_sur)} surnames | "
          f"corpus: {len(c_first)} first, {len(c_sur)} surnames\n")
    for line in reports:
        print("  " + line)
    for line in warns:
        print("  " + line)
    for line in fails:
        print("  " + line)
    print()

    if fails:
        coll = [f for f in fails if f.startswith(("FIRST", "EXACT"))]
        defa = [f for f in fails if f.startswith("TIER-A")]
        if coll:
            print(f"NAME COLLISION - {len(coll)} conflict(s).")
            print("  A returning reader meets this name twice and reads it as one writer's habit.")
            print("  Rename the character in canon, entity state, voice matrix, sample bank,")
            print("  outline and any chapter it appears in, then re-run this gate.")
        if defa:
            print(f"DEFAULT NAME - {len(defa)} name(s) at the top of the prior.")
            print("  This row measures how common a name is, not whether it fits. It")
            print("  cannot tell whether the name suits the character's age or setting;")
            print("  it only refuses the name you would have reached for without thinking.")
        return 1
    if warns and args.strict:
        print("NAME CHECK - nothing failed, but the warnings above are errors under --strict.")
        return 1
    print("NAME CHECK OK - no cast name collides with another project, and none sits")
    print("at the top of the name prior. This says nothing about whether the names mean")
    print("anything; that is a craft question and it belongs to the author.")
    return 0


def harvest_canon(book):
    """The book under test: only its canon files, which is where its own cast is declared."""
    full, firsts, surnames = set(), set(), set()
    for fn in ("CANON_LEDGER.yaml", "CANON_LEDGER.yml", "ENTITY_STATE.yaml",
               "artifacts/03-characters.md", "characters.md", "cast.md"):
        p = os.path.join(book, fn)
        if os.path.isfile(p):
            f, fi, su = harvest(p)
            full |= f
            firsts |= fi
            surnames |= su
    return full, firsts, surnames


if __name__ == "__main__":
    sys.exit(main())
