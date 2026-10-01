#!/usr/bin/env python3
"""check-premise-distinct.py - has this book already been written, with the coat off?

WHY THIS EXISTS
  The audit behind this gate found something uncomfortable. Every other gate in this suite
  begins at `manuscript/chapters` and reads one book at a time. uniformity compares a
  book's chapters to each other; drift reads prose shape; arc reads structure; length
  counts. check-names.py is the sole exception, and it reaches outward only as far as a
  character name. Meanwhile ZERO gates read `research/` - no gate opens market-research.md,
  comp-titles, bestseller-dna or the clue ledger. The research phase produces the most
  consequential document in the pipeline, the file that says what the book IS, and it is
  entirely ungated.

  The consequence is a specific and very common failure: a book that is new in its
  details and identical in its machinery. Different county, different decade, different
  body count - and a reader who finished the first one recognises the second one at the
  back cover. No amount of prose quality prevents that, because the redundancy is not in
  the sentences. It is in the engine.

  The concrete instance that prompted this gate: a book was scoped around "a
  small-town professional opens an investigation of a disappearance" before anyone
  established that Tom Baragwanath's *Paper Cage* (2022 NZ / 2024 US Knopf, Ngaio Marsh
  Award finalist, 2025 Barry Award nominee) is exactly that book, with a police-station
  RECORDS CLERK as its protagonist. The slot was occupied. Three of the four competing
  comps in that same research file turned out not to exist at all.

WHAT IT MEASURES
  Three axes, recorded per book in the frozen PREMISE_LEDGER.tsv:

    profession     what the protagonist is employed as
    engine         the machine the plot runs on
    relationship   the central dynamic - who is lying to whom

  and then a severity ladder, because the axes are not equally decisive:

    FAIL  profession AND engine match another row, or all three match
    WARN  exactly two axes match
    pass  zero or one axis matches

  The two-axis floor is the whole design. Two books with the same protagonist's job are
  extremely common and entirely fine; every detective series ever written shares one.
  What a reader experiences as "I have read this" is the JOB PLUS THE ENGINE, and a gate
  that fired on profession alone would fail every book in every series, which is why it
  must not.

WHAT IT DOES NOT CLAIM - read this before trusting a pass
  This gate does not know whether a premise is GOOD, FRESH, or WORTH WRITING. It cannot.
  A book can pass this and still be the most derivative thing ever published, because
  derivative is not the same as duplicate - an enormous space of books share a
  profession and an engine and are all worth reading.

  It is a *collision* check, not an originality check, and the two are not on the same
  scale. Originality is a judgement about a work's quality; collision is a fact about a
  catalogue's contents. Only the second is measurable here. A gate that attempted the
  first would be a taste rule wearing a measurement's clothes, which is the exact failure
  mode USER_PREFERENCES.md exists to prevent.

  It also cannot see the published world. Tom Baragwanath, or any of the ~40,000 books
  published in a year, are invisible to it. The ledger is the author's own catalogue, and
  it is a hand-seeded, finite, honestly-maintained list - its coverage is exactly the
  author's diligence. For the published world the instrument is comp research, and the
  fix for that is a verification stamp (RESEARCH-VERIFIED) rather than a scoring gate.

  What it CAN do that nothing else in the suite can: notice, before a manuscript exists,
  that book six is book three's engine with a new name on it. That is worth a gate.

USAGE
    python check-premise-distinct.py <book-dir> [--ledger <tsv>] [--strict]

  The book supplies its own three axes either from a `premise_axes:` block in
  premise.md / PROJECT_STATE.yaml, or from `--axes profession|engine|relationship`.

  Exit 0 pass (warnings allowed), 1 fail on a collision, 2 could not read the book.
"""

import argparse
import os
import re
import sys

AXES = ("profession", "engine", "relationship")


# ---------------------------------------------------------------- ledger reading

def read_ledger(path):
    """Read the frozen TSV. Returns a list of dicts. Malformed rows are skipped loudly."""
    if not os.path.isfile(path):
        print(f"check-premise-distinct: no ledger at {path}", file=sys.stderr)
        return None
    rows, bad = [], 0
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 6:
                bad += 1
                print(f"  ledger line {lineno}: expected 6 tab-separated fields, got "
                      f"{len(parts)} - SKIPPED", file=sys.stderr)
                continue
            book, year, prof, eng, rel, note = (p.strip() for p in parts)
            if not book or not prof or not eng:
                bad += 1
                print(f"  ledger line {lineno}: book/profession/engine must be non-empty "
                      f"- SKIPPED", file=sys.stderr)
                continue
            rows.append({"book": book, "year": year, "profession": prof,
                         "engine": eng, "relationship": rel, "note": note,
                         "line": lineno})
    if bad:
        print(f"check-premise-distinct: {bad} malformed ledger row(s) ignored. A ledger "
              f"that silently drops rows hides exactly the collision it exists to find.",
              file=sys.stderr)
    return rows


# ---------------------------------------------------------------- book-side axes

def norm(s):
    """Normalise an axis value for comparison: lowercase, collapse whitespace/punctuation.

    The author's own wording in a premise file will not match the wording in the ledger
    by accident, so this only has to forgive the differences that are genuinely noise -
    a stray article, a hyphen vs a space, capitalisation, surrounding quotes.
    """
    s = (s or "").strip().strip("\"'").lower()
    s = re.sub(r"[\"'`]", "", s)
    s = re.sub(r"[-_/]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


AXIS_RE = re.compile(
    r"^\s*[-*]?\s*(?:premise_axes|axes)\s*:?\s*$|"
    r"^\s*[-*]?\s*[-*]?\s*(profession|engine|relationship)\s*[:=]\s*(.+?)\s*$",
    re.I | re.M,
)


def read_book_axes(book):
    """Pull the three axes out of the book. Returns (dict, source_path) or ({}, None)."""
    candidates = ["premise.md", "PROJECT_STATE.yaml", "premise.yaml", "ASSUMPTIONS.md"]
    for name in candidates:
        p = os.path.join(book, name)
        if not os.path.isfile(p):
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        axes = {}
        for m in AXIS_RE.finditer(text):
            ax, val = m.group(1), m.group(2)
            if ax:
                v = val.strip().strip("\"'").rstrip(".")
                if v and ax.lower() not in axes:
                    axes[ax.lower()] = v
            else:
                # a "premise_axes:" key opens a block; clear anything picked up before it
                axes = {k: v for k, v in axes.items()}
        # Drop keys that came from a different section (a stray "engine:" in prose).
        axes = {k: v for k, v in axes.items() if k in AXES}
        if "profession" in axes and "engine" in axes:
            return axes, p
    return {}, None


# ---------------------------------------------------------------- the comparison

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def self_row(rows, book):
    """The ledger row for the book under test, if it has one.

    A completed book is entered in the ledger - that is the whole point of the ledger, and
    the seed file carries rows for books that are already written. Without this, the gate
    compares a book against its OWN row and fails it for being itself: the first version
    did exactly that on the-origin-point, reporting 'EXACT ENGINE + RELATIONSHIP: matches
    on profession + engine + relationship' against a book that was the thing being tested.
    A gate that cannot be run on a finished book is a gate nobody will run.
    """
    target = slugify(os.path.basename(os.path.abspath(book)))
    for r in rows:
        if slugify(r["book"]) == target:
            return r
    # also match a ledger row whose book field is a project id differing by punctuation
    for r in rows:
        if slugify(r["book"]) and slugify(r["book"]) in target or target in slugify(r["book"]):
            return r
    return None


def compare(axes, rows):
    """Score the book against every ledger row. Returns (fails, warns, detail)."""
    b = {a: norm(axes.get(a, "")) for a in AXES}
    fails, warns, detail = [], [], []
    for r in rows:
        matches = [a for a in AXES if b[a] and b[a] == norm(r[a])]
        n = len(matches)
        if n < 2:
            continue
        line = (f"{r['book']} ({r['year']}): matches on {' + '.join(matches)} - "
                f"theirs: {r['profession']} / {r['engine']}")
        detail.append((n, line))
        if n == 3:
            fails.append(f"EXACT ENGINE + RELATIONSHIP: {line}")
        else:
            fails.append(f"SAME JOB + ENGINE: {line}")
    for n, line in sorted(detail, reverse=True):
        if n == 2 and "SAME JOB + ENGINE" not in line:
            warns.append(f"two axes: {line}")
    return fails, warns, b


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("book")
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--axes", default=None,
                    help="override: 'profession|engine|relationship'")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    book = os.path.abspath(args.book)
    if not os.path.isdir(book):
        print(f"check-premise-distinct: no such book directory: {book}", file=sys.stderr)
        return 2

    here = os.path.dirname(os.path.abspath(__file__))
    ledger = os.path.abspath(args.ledger) if args.ledger else \
        os.path.join(here, "calibration", "PREMISE_LEDGER.tsv")
    rows = read_ledger(ledger)
    if rows is None:
        return 2
    if not rows:
        print("check-premise-distinct: ledger is empty. An empty ledger makes this gate "
              "silently pass everything, which is worse than it not existing.")
        return 2

    axes, src = read_book_axes(book)
    if args.axes:
        parts = [p.strip() for p in args.axes.split("|")]
        if len(parts) != 3:
            print("check-premise-distinct: --axes needs exactly 3 values "
                  "'profession|engine|relationship'", file=sys.stderr)
            return 2
        axes = dict(zip(AXES, parts))
        src = "(command line)"

    if "profession" not in axes or "engine" not in axes:
        print("check-premise-distinct: this book declares no profession and engine, so "
              "there is nothing to compare. Add a `premise_axes:` block to premise.md or "
              "PROJECT_STATE.yaml:\n"
              "    premise_axes:\n"
              "      profession: \"...\"\n"
              "      engine: \"...\"\n"
              "      relationship: \"...\"",
              file=sys.stderr)
        return 2

    print(f"check-premise-distinct: {os.path.basename(book)} vs {len(rows)} recorded book(s)")
    print(f"  source: {src}")
    for a in AXES:
        print(f"  {a:<13} {axes.get(a, '(not declared)')}")
    print()

    # A finished book has its own row in the ledger. Exclude it, or the gate fails every
    # completed book for being identical to itself.
    me = self_row(rows, book)
    rows_compared = [r for r in rows if r is not me]
    if me is not None:
        print(f"  own ledger row: {me['book']} (line {me['line']}) - excluded from comparison")
        print()

    fails, warns, b = compare(axes, rows_compared)
    for w in warns:
        print(f"  WARN  {w}")
    for f in fails:
        print(f"  FAIL  {f}")

    if fails:
        print("\nPREMISE COLLISION - this book shares a profession and an engine with a "
              "book already in the catalogue.")
        print("  Same job + same machine reads as the same book with a new coat on, and "
              "the reader")
        print("  recognises it at the back cover. Prose quality cannot prevent this; the "
              "redundancy")
        print("  is in the engine, not the sentences.")
        print("  Either change one axis and re-run, or record in premise.md why this is "
              "the same")
        print("  engine on purpose and what makes it a different book.")
        return 1

    if warns:
        print("\nPREMISE CHECK OK with warnings - two axes overlap. A warning is a "
              "question, not a")
        print("  failure: the same protagonist job in two books is normal and often "
              "correct. Answer")
        print("  the question in premise.md rather than ignoring it.")
        return 0

    print("PREMISE CHECK OK - this job-and-engine pair is unspent in the recorded "
          "catalogue.")
    print("  That is a collision result, not a compliment. A book can pass this and "
          "still be")
    print("  derivative in ways no ledger can see, because the published world is not "
          "in the file.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
