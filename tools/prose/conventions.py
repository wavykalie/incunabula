#!/usr/bin/env python3
"""conventions.py - the one reader for "what mode is this book?"

A book declares its mode once, at intake, in PROJECT_STATE.yaml:

    book:
      mode: fiction | nonfiction

`mode` is the primary declaration. Two legacy fields are honoured as fallbacks so
every book that predates the field keeps working and every reader that used to
grep `positioning` / `genre` sees the same answer as every other one:

    positioning: ... nonfiction ...   (free text; the legacy declaration)
    genre: ... nonfiction ...         (free text; ditto)

The precedence is: `mode` first, exact value; then the legacy pair by substring.
A book that declares nothing gets None - "unknown", not a silent default. Gates
that need a boolean decide themselves what unknown means, in the open, where a
reviewer can read the decision.

WHY ONE READER
  Before this file, each gate owned its own copy of the same regex. The copies
  had already drifted (one anchored `:\\s*`, one `:\\s*`-less; one case-insensitive,
  one not). Two gates answering one question differently is not a gate defect, it
  is a convention defect - so the question is answered here, once, and the gates
  import it. This file holds no thresholds and reads no prose; like
  calibration/fetch-multivolume.py's staged-corpus discipline, it is infrastructure
  the gates lean on, not a gate. It is deliberately outside GATE_FREEZE.md's
  manifest: editing it cannot change what a row asserts, only who answers the
  question. Any change that DID alter an answer for a frozen book belongs in
  GATE_FREEZE.md with a date and a reason, same as any threshold move.

SELF-TEST
  Run with no arguments: re-reads every staged book in test-books/ and prints the
  mode each one resolves to, plus the fixture expectations below. Exit 1 only on a
  broken invariant, never on a book that merely declares nothing.
"""

import os
import re
import sys

# The one pattern. Anchored at line start so it reads declarations, not prose that
# quotes the word; legacy values are free text, so they match by substring, the
# way every pre-existing reader read them (validate-controls.sh control 10 stages
# `positioning: "narrative nonfiction"` and must keep passing).
_MODE_RE = re.compile(
    r"^[ \t]*mode[ \t]*:[ \t]*[\"']?(fiction|nonfiction)[\"']?[ \t]*$"
    r"|"
    r"^[ \t]*(?:positioning|genre)[ \t]*:[ \t]*[\"']?[^\"'\n#]*nonfiction",
    re.IGNORECASE | re.MULTILINE,
)


def read_head(book_root, size=8000):
    """The head of PROJECT_STATE.yaml, or STATE.yaml, or ''. One read path, shared.

    8000 bytes covers every declaration block the project has ever staged; the
    previous gates read 4000 or 8000, so 8000 is a strict widening, never a loss.
    """
    for name in ("PROJECT_STATE.yaml", "STATE.yaml"):
        path = os.path.join(book_root, name)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    return fh.read(size)
            except OSError:
                continue
    return ""


def mode_of(book_root):
    """Returns 'fiction' | 'nonfiction' | None. None = nothing declared.

    Precedence: an exact `mode:` value beats the legacy fields. Inside the legacy
    fallback, `positioning` is checked before `genre` - that ordering preserves
    the pre-plumbing behaviour of every gate, which matched the pair in one
    alternation and never had to choose.
    """
    head = read_head(book_root)

    m = re.search(
        r"^[ \t]*mode[ \t]*:[ \t]*[\"']?(fiction|nonfiction)[\"']?[ \t]*$",
        head, re.IGNORECASE | re.MULTILINE,
    )
    if m:
        return m.group(1).strip().lower()

    if _MODE_RE.search(head):
        return "nonfiction"

    if re.search(
        r"^[ \t]*(?:positioning|genre)[ \t]*:[ \t]*[\"']?[^\"'\n#]*\bfiction\b",
        head, re.IGNORECASE | re.MULTILINE,
    ):
        return "fiction"

    return None


def is_nonfiction(book_root):
    """The boolean gates actually want. Unknown is not nonfiction - the reader
    that used to live in check-surplus.py had exactly this semantics, and the
    readers in check-uniformity.py and validate-controls.sh agree with it, because
    every one of them defaulted undeclared books to the fiction-path behaviour."""
    return mode_of(book_root) == "nonfiction"


# --------------------------------------------------------------------------
# Nonfiction mode: register-scoped rows
#
# CALIBRATION.md section 20 swept the frozen deslop table over 963k words of
# published prescriptive prose (Smiles, Marden, James, Bennett, Montessori,
# Chavasse, Rousseau, 1762-1912). Ten failing row-lines across 134 files, and the
# row that accuses more than a stray file is A10a "nonfiction filler" - the one row
# whose own NAME targets this register. It is a zero-tolerance HARD row, and it
# trips on the expository constructions Victorian advice prose uses natively
# ("it is worth noting", "due to the fact that", "interestingly,").
#
# So nonfiction mode scopes A10a exactly the way the U-rows are scoped: the row
# keeps its pattern and its count, reports instead of failing, and the fiction
# arm is unchanged byte-for-byte. This file holds the decision, in the open,
# where self-test and review can see it.
#
# NOT SCOPED, deliberately, and the reasons are measurements:
#   A19, A21, A24, A25 - all scored ZERO across the prescriptive sweep. The sweep
#   bound the question ONE WAY: constructions of the modern how-to register (the
#   AI-tropes catalogue) sit behind the copyright wall. Zero published hits here
#   is not zero in a 2020s parenting book. These rows stay live for nonfiction.
#   A11a ("in summary") - 2 files in 134, capable of an author-level glance.
#   U5 warns by design on flat paragraph layout - expected in advice prose.
# --------------------------------------------------------------------------
NF_SCOPED = {"A10a"}


def nf_row_scoped(row_id):
    """True if this deslop row is scoped (report-not-fail) for a nonfiction book.
    The scanner asks this once per file; fiction never asks at all."""
    return row_id in NF_SCOPED


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

_FIXTURES = [
    # (state text, expected mode, label)
    ('project:\n  positioning: "narrative nonfiction"\n', "nonfiction",
     "control-10 fixture: indented positioning, free-text value"),
    ('project:\n  positioning: "nonfiction"\n', "nonfiction",
     "sons-of-heaven shape: quoted exact value"),
    ('book:\n  mode: nonfiction\n', "nonfiction", "primary field, bare"),
    ('book:\n  mode: "fiction"\n', "fiction", "primary field, quoted"),
    ('project:\n  genre: "prescriptive nonfiction self-help"\n', "nonfiction",
     "legacy genre field, free text"),
    ('project:\n  genre: "literary fiction"\n', "fiction", "legacy genre, fiction"),
    ('project:\n  word_target: 30000\n', None, "undeclared book"),
    ("", None, "no state file at all"),
    # precedence: mode wins even when legacy fields disagree
    ('book:\n  mode: fiction\nproject:\n  positioning: "nonfiction"\n', "fiction",
     "mode outranks legacy positioning"),
    # an anchored reader must not read prose that mentions the word
    ("notes: the genre: nonfiction debate is unsettled\n", None,
     "non-declaration mention is not a declaration"),
    # fiction must not match the nonfiction branch
    ('project:\n  positioning: "fiction"\n', "fiction", "plain fiction positioning"),
]


def selftest():
    import tempfile

    rc = 0
    for text, expected, label in _FIXTURES:
        with tempfile.TemporaryDirectory() as tmp:
            if text:
                os.makedirs(tmp, exist_ok=True)
                with open(os.path.join(tmp, "PROJECT_STATE.yaml"), "w",
                          encoding="utf-8") as fh:
                    fh.write(text)
            got = mode_of(tmp)
        mark = "ok" if got == expected else "MISMATCH"
        if got != expected:
            rc = 1
        print(f"  {mark:8} expected={str(expected):10} got={str(got):10} {label}")

    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    books_dir = os.path.join(repo, "test-books")
    if os.path.isdir(books_dir):
        print(f"\n  staged books under test-books/:")
        for entry in sorted(os.listdir(books_dir)):
            book_root = os.path.join(books_dir, entry)
            if os.path.isdir(book_root):
                print(f"    {entry:32} mode={mode_of(book_root)}")

    # NF scoping invariants: the scoped set holds what section 20 measured it may,
    # and does NOT hold the rows the sweep explicitly refused to scope (zero
    # published hits is a one-sided bound, not a clearance - see the block above).
    for must in ("A10a",):
        if must not in NF_SCOPED:
            print(f"  MISMATCH expected {must} scoped for nonfiction (CALIBRATION.md §20)")
            rc = 1
    for must_not in ("A19", "A21", "A24", "A25", "A11a"):
        if must_not in NF_SCOPED or nf_row_scoped(must_not):
            print(f"  MISMATCH expected {must_not} NOT scoped - modern-register row, "
                  f"zero published hits is not a clearance")
            rc = 1
    if not rc:
        print(f"  ok       NF scoping: {sorted(NF_SCOPED)} scoped; refused rows stay live")

    return rc


if __name__ == "__main__":
    # --scoped-rows      print the deslop row ids scoped for nonfiction, one line
    # --nf <book_root>   exit 0 if that book declares nonfiction, else 1
    # (no arguments)     the self-test
    if "--scoped-rows" in sys.argv:
        print(" ".join(sorted(NF_SCOPED)))
        sys.exit(0)
    if "--nf" in sys.argv:
        idx = sys.argv.index("--nf")
        if idx + 1 >= len(sys.argv):
            print("conventions: --nf needs a book root", file=sys.stderr)
            sys.exit(2)
        try:
            sys.exit(0 if is_nonfiction(sys.argv[idx + 1]) else 1)
        except Exception as exc:            # never crash a gate on a bad root
            print(f"conventions: {exc}", file=sys.stderr)
            sys.exit(2)
    sys.exit(selftest())
