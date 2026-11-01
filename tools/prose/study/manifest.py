#!/usr/bin/env python3
"""manifest.py - one row per book, and the only place the columns are defined.

Design §11's minimum schema, plus the fields REDTEAM.md B4/B5 and M1 require to make the
A-vs-B comparison attributable: the operator-intervention count, the naive continuation
count, and the analysis-vs-raw word counts (header stripping is a declared rule, and the
difference is recorded rather than assumed away).

usage:
    python manifest.py --init books/manifest.csv
    python manifest.py --check books/manifest.csv
    python manifest.py --add books/manifest.csv --row '{"book_id": "A-01", ...}'
"""

import argparse
import csv
import json
import os
import sys

FIELDS = (
    # identity
    "book_id", "arm", "premise_id", "title_label", "genre",
    # generation
    "model_id", "temperature", "top_p", "system_prompt_id",
    "generation_start", "generation_end",
    # size (target_words records which length stratum the row belongs to: 60,000 primary
    # or 200,000 exploratory long-form, DECISIONS.md §2 — the two are never pooled)
    "word_count", "raw_word_count", "chapter_count", "target_words",
    # provenance (ductus_id is the literal "UNASSIGNED" on primary Arm B rows: the
    # pipeline's own no-voice state, DECISIONS.md §3. A blank cell is still an error.)
    "prompt_log_path", "pipeline_commit", "ductus_id",
    # protocol (REDTEAM.md B4, B5, M1)
    "operator_interventions", "naive_continuations",
    # anything that broke the protocol, one free-text field
    "deviations",
)
REQUIRED = ("book_id", "arm", "premise_id", "genre", "word_count")
ENUMS = {"arm": ("A", "B", "C")}


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_header(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if os.path.exists(path):
        print(f"{path} already exists; a manifest is append-only, not rewritten.")
        return 2
    with open(path, "w", encoding="utf-8", newline="") as fh:
        csv.DictWriter(fh, FIELDS).writeheader()
    print(f"created {path} with {len(FIELDS)} columns")
    return 0


def row_errors(row, seen):
    errs = []
    for f in REQUIRED:
        if not str(row.get(f, "")).strip():
            errs.append(f"missing required field {f!r}")
    arm = str(row.get("arm", "")).strip().upper()
    if arm and arm not in ENUMS["arm"]:
        errs.append(f"arm {arm!r} not in {ENUMS['arm']}")
    bid = str(row.get("book_id", "")).strip()
    if bid in seen:
        errs.append(f"duplicate book_id {bid!r}")
    if bid and arm and not bid.startswith(arm + "-"):
        errs.append(f"book_id {bid!r} does not start with its arm ({arm}-)")
    if arm == "B" and not str(row.get("pipeline_commit", "")).strip():
        errs.append("Arm B row has no pipeline_commit (design §11)")
    if arm in ("A", "B") and not str(row.get("prompt_log_path", "")).strip():
        errs.append(f"Arm {arm} row has no prompt_log_path (design §3/§11)")
    if arm == "B" and not str(row.get("ductus_id", "")).strip():
        errs.append("Arm B row has no ductus_id (design §4)")
    wc = str(row.get("word_count", "")).strip()
    if wc:
        try:
            if int(float(wc)) < 1000:
                errs.append(f"word_count {wc} is too short for a novel row")
        except ValueError:
            errs.append(f"word_count {wc!r} is not a number")
    return errs


def band_note(row):
    """A book outside its target band is reported, never failed.

    Design §7: naive books that come in short are data, not failures to hide. So a miss is
    a note to carry into the report, and turning it into an error here would pressure
    whoever files the row toward rescuing the book.
    """
    try:
        wc, target = int(float(row.get("word_count") or 0)), int(float(
            row.get("target_words") or 0))
    except ValueError:
        return None
    if not wc or not target:
        return None
    if abs(wc - target) <= 0.1 * target:
        return None
    return (f"word_count {wc:,} is outside +/-10% of target {target:,} "
            f"({wc / target:.0%} of target) - report it as an outcome")


def check(path):
    rows = read(path)
    seen, bad, notes = set(), 0, 0
    for i, row in enumerate(rows, 2):
        errs = row_errors(row, seen)
        seen.add(str(row.get("book_id", "")).strip())
        for e in errs:
            print(f"  line {i} ({row.get('book_id', '?')}): {e}")
            bad += 1
        note = band_note(row)
        if note:
            print(f"  line {i} ({row.get('book_id', '?')}): note: {note}")
            notes += 1
    print(f"{len(rows)} row(s), {bad} problem(s), {notes} band note(s)")
    return 1 if bad else 0


def add(path, payload):
    row = json.loads(payload) if isinstance(payload, str) else payload
    rows = read(path) if os.path.exists(path) else []
    errs = row_errors(row, {str(r.get("book_id", "")).strip() for r in rows})
    if errs:
        for e in errs:
            print(f"  {e}")
        return 1
    with open(path, "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, FIELDS)
        w.writerow({k: row.get(k, "") for k in FIELDS})
    print(f"appended {row['book_id']}")
    return 0


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--init", metavar="CSV")
    ap.add_argument("--check", metavar="CSV")
    ap.add_argument("--add", metavar="CSV")
    ap.add_argument("--row", help="JSON object for --add")
    args = ap.parse_args(argv)
    if args.init:
        return write_header(args.init)
    if args.check:
        return check(args.check)
    if args.add:
        if not args.row:
            print("--add needs --row JSON")
            return 2
        return add(args.add, args.row)
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main())
