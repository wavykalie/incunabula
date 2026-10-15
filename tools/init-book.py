#!/usr/bin/env python3
"""init-book.py — scaffold a new book and register it in BOOKS.yaml.

The entry point that makes the 2026-10-01 failure (a finished book absent from
the suite) structurally impossible for new books: there is no moment where a
book directory exists and the registry does not know about it. Every book the
pipeline starts goes through here.

What it does:
    1. validates the declaration: a floor above its ceiling, or a contract the
      plan contradicts, is refused BEFORE anything is created. A contract with
      nothing to check it against is how L1 got disarmed (2026-10-13 audit);
      intake is the one moment both numbers are in front of a person
    2. creates <workspace>/<path>/ with the directories the pipeline expects
    3. writes a PROJECT_STATE.yaml with the declared length contract, the plan,
      and the status
    4. appends the book to BOOKS.yaml (the registry the suite reads)
    5. runs tools/check-registry.py and verifies THIS registration - problems
      naming other books are reported as pre-existing debt, not failures here

What it does NOT do:
    - choose a length contract. A floor of 0 means "not declared"; the gate
      will report NOT APPLICABLE until a real contract is written by intake.
    - write premise, outline, or any prose. Phase work belongs to the pipeline.

Usage:
    python tools/init-book.py --path my-novel --title "My Novel" \
        [--status drafting] [--floor 80000] [--ceiling 95000] [--concept] \
        [--chapters-planned 30 --words-per-chapter 3000]
    python tools/init-book.py --self-test

    --chapters-planned / --words-per-chapter  the plan. Their product must sit
        inside the declared band or intake refuses; tools/check-progress.py C1
        re-checks exactly this agreement on the book from then on.

    --concept  scaffolds the book but declares expected_manuscript: false;
               prose gates will not apply until it is promoted by editing
               BOOKS.yaml (the registry says so, on one line).
"""

import argparse
import io
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = HERE                                      # incunabula/tools
FRAMEWORK = os.path.dirname(TOOLS_DIR)                # incunabula/
DEFAULT_WORKSPACE = os.path.join(FRAMEWORK, "test-books")  # incunabula/test-books/ (production workspace since 2026-10-07)
REGISTRY = os.environ.get("BOOKS_REGISTRY", os.path.join(FRAMEWORK, "BOOKS.yaml"))

STATUSES = {"concept", "drafting", "complete", "published", "fixture", "autonomous"}


def write_text(path, text, mode="w"):
    """Write text with LF line endings, whatever platform this runs on.

    Python's text mode translates '\\n' to CRLF on Windows. That is invisible in
    an editor and fatal to this project's records: a CR is a byte grep cannot see
    (it hides from `grep '^'` entirely) and it sits exactly where the sentence
    tokenizer expects a space, so sentence-level rows silently under-count. That
    is KF-005, closed by fixing the detector - and this is the same defect one
    layer down, in the file that writes the book's own state.

    preflight.sh row 3 fails any canonical state file carrying a CR, so a book
    scaffolded on Windows was born failing its own make-ready check: 7 of the
    books on disk carried CRLF PROJECT_STATE.yaml for this reason. io.open with
    newline="" writes the bytes given and translates nothing, so the file is
    LF on every platform and byte-identical in a clone.

    The registry is written the same way. It has no convention of its own to
    keep - it was CRLF only because this appender ran on Windows, so its rows
    were CRLF on one machine and LF on the next, and the file would have drifted
    to mixed if it were ever appended to from Linux. LF is what the rest of the
    repository uses (40+ files; the three CRLF ones are the two append-only
    record files and a frozen instrument, none of which this tool writes).
    """
    with io.open(path, mode, encoding="utf-8", newline="") as fh:
        fh.write(text)


def append_registry(book_path, title, status, expected_manuscript):
    note = {
        "concept": "Concept stage; no manuscript expected yet.",
        "drafting": "Registered at creation by init-book.py.",
        "fixture": "Registered as a fixture by init-book.py.",
        "autonomous": "Autonomous run (random button) - rolled by tools/roll-brief.py, no author at the wheel.",
    }.get(status, "Registered by init-book.py.")
    with io.open(REGISTRY, "a", encoding="utf-8", newline="") as fh:
        fh.write(
            f"\n  - path: {book_path}\n"
            f"    title: \"{title}\"\n"
            f"    status: {status}\n"
            f"    expected_manuscript: {str(expected_manuscript).lower()}\n"
            f"    note: \"{note} ({date.today().isoformat()})\"\n"
        )


def self_test():
    """Scaffold into a temp workspace and read the bytes back.

    The assertions are the defect classes this tool has actually produced:
      - a CR in PROJECT_STATE.yaml, so the book fails preflight row 3 at birth
      - a registration that does not reach the registry
      - a contract the plan contradicts, accepted instead of refused before
        anything is written
    """
    tmp = tempfile.mkdtemp(prefix="init-book-selftest-")
    real_registry = REGISTRY
    real_workspace = os.environ.get("BOOKS_WORKSPACE")
    try:
        workspace = os.path.join(tmp, "books")
        os.makedirs(workspace)
        registry = os.path.join(tmp, "BOOKS.yaml")
        write_text(registry, "books:\n")
        os.environ["BOOKS_WORKSPACE"] = workspace
        os.environ["BOOKS_REGISTRY"] = registry
        globals()["REGISTRY"] = registry

        rc = main(["--path", "selftest-book", "--title", "Self Test",
                   "--status", "drafting", "--chapters-planned", "4",
                   "--words-per-chapter", "1000"])
        assert rc == 0, f"the scaffold refused a valid declaration (exit {rc})"

        state = os.path.join(workspace, "selftest-book", "PROJECT_STATE.yaml")
        raw = open(state, "rb").read()
        assert b"\r" not in raw, (
            f"PROJECT_STATE.yaml carries {raw.count(chr(13).encode())} CR byte(s) - "
            "preflight row 3 would fail this book at birth")

        reg = open(registry, "rb").read()
        assert b"selftest-book" in reg, "the scaffold did not register the book"
        assert b"\r" not in reg, "the registry append was not the file's own convention"

        refused = False
        try:
            main(["--path", "refused", "--title", "Refused",
                  "--floor", "80000", "--ceiling", "90000",
                  "--chapters-planned", "10", "--words-per-chapter", "20000"])
        except SystemExit:
            refused = True
        assert refused, "a plan outside the declared band was not refused"
        assert not os.path.exists(os.path.join(workspace, "refused")), (
            "a refused declaration created files anyway")

        print("init-book self-test: ok")
        return 0
    finally:
        globals()["REGISTRY"] = real_registry
        if real_workspace is None:
            os.environ.pop("BOOKS_WORKSPACE", None)
        else:
            os.environ["BOOKS_WORKSPACE"] = real_workspace
        os.environ.pop("BOOKS_REGISTRY", None)
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return self_test()
    ap = argparse.ArgumentParser(description="Scaffold and register a book.")
    ap.add_argument("--path", required=True,
                    help="book path relative to the workspace root (e.g. my-novel)")
    ap.add_argument("--title", required=True)
    ap.add_argument("--status", default="drafting", choices=sorted(STATUSES))
    ap.add_argument("--floor", type=int, default=0,
                    help="target_floor_words; 0 declares no length contract yet")
    ap.add_argument("--ceiling", type=int, default=0)
    ap.add_argument("--chapters-planned", type=int, default=0,
                    help="planned chapter count; goes with --words-per-chapter")
    ap.add_argument("--words-per-chapter", type=int, default=0,
                    help="planned average words per chapter; with --chapters-planned "
                         "this is the plan check-progress.py C1 checks the contract against")
    ap.add_argument("--concept", action="store_true",
                    help="shorthand for --status concept (no manuscript expected)")
    args = ap.parse_args(argv)

    if args.concept:
        args.status = "concept"
    book_path = args.path.strip("/").replace("\\", "/")
    if not book_path or book_path.startswith("."):
        ap.error("--path must be a plain relative path like 'my-novel'")

    # 0. validate the declaration BEFORE anything exists on disk.
    if bool(args.chapters_planned) != bool(args.words_per_chapter):
        ap.error("--chapters-planned and --words-per-chapter go together - "
                 "half a plan is not a plan")
    if args.chapters_planned < 0 or args.words_per_chapter < 0:
        ap.error("plan numbers must be positive")
    floor, ceiling = args.floor, args.ceiling
    if floor and not ceiling:
        ceiling = int(floor * 1.15)
    if ceiling and not floor:
        floor = int(ceiling * 0.9)
    if floor and ceiling and floor > ceiling:
        ap.error(f"--floor {floor} is above --ceiling {ceiling} - "
                 f"a contract nothing can land inside")
    plan_product = args.chapters_planned * args.words_per_chapter
    if plan_product and (floor or ceiling) and not (floor <= plan_product <= ceiling):
        ap.error(
            f"the plan ({args.chapters_planned} chapters x {args.words_per_chapter} = "
            f"{plan_product:,} words) does not sit within the declared contract "
            f"[{floor:,}, {ceiling:,}]. Intake will not write a contract the plan "
            f"contradicts: a band rewritten to fit what the book happens to be is "
            f"the disarm the 2026-10-13 audit found. Fix the plan or the contract.")

    workspace = os.environ.get("BOOKS_WORKSPACE", DEFAULT_WORKSPACE)
    book_root = os.path.join(workspace, book_path)
    if os.path.exists(book_root):
        print(f"init-book: {book_root} already exists - nothing created, nothing registered.")
        return 1

    expected_manuscript = args.status != "concept"

    # 1. scaffold
    os.makedirs(os.path.join(book_root, "manuscript", "chapters"), exist_ok=True)
    for d in ("artifacts", "maintenance", "research"):
        os.makedirs(os.path.join(book_root, d), exist_ok=True)

    # 2. state file with the declared contract, the plan (or the explicit
    # absence of each), and the status
    with io.open(os.path.join(book_root, "PROJECT_STATE.yaml"), "w",
                 encoding="utf-8", newline="") as fh:
        fh.write(
            "# ============================================================================\n"
            "# A MATTER OF RECORD - created by incunabula/tools/init-book.py\n"
            f"# on {date.today().isoformat()}. The length contract below is what\n"
            "# check-length.py reads (first 8k characters). Change it here, by hand,\n"
            "# when the contract changes. status: in_progress makes L1 record rather\n"
            "# than judge; remove it at delivery.\n"
            "# ============================================================================\n\n"
            "project:\n"
            f"  title: \"{args.title}\"\n"
            f"  status: \"{'in_progress' if args.status in ('drafting', 'autonomous') else args.status}\"\n\n"
        )
        if floor or ceiling:
            fh.write(
                "  # ---- LENGTH CONTRACT (read by check-length.py, first 8k chars) ----\n"
                f"  target_floor_words: {floor}\n"
                f"  target_ceiling_words: {ceiling}\n"
                f"  target_range_words: [{floor}, {ceiling}]\n\n"
            )
        else:
            fh.write(
                "  # ---- NO LENGTH CONTRACT YET (read by check-length.py) ----\n"
                "  # Declared as the schema default, which the gate reads as 'not\n"
                "  # declared' - NOT APPLICABLE, never a pass. Write real numbers\n"
                "  # here at intake if the book is to be governed by L1.\n"
                "  target_range_words: [0, 0]\n\n"
            )
        if plan_product:
            fh.write(
                "  # ---- PLAN (read by tools/check-progress.py C1) ----\n"
                "  # Validated at intake against the contract above. When the outline\n"
                "  # lands, its per-chapter targets become the plan C1 prefers; these\n"
                "  # keys are the fallback and must then agree with it.\n"
                f"  chapter_count_planned: {args.chapters_planned}\n"
                f"  average_words_per_chapter_planned: {args.words_per_chapter}\n\n"
            )
        else:
            fh.write(
                "  # ---- NO PLAN YET (read by tools/check-progress.py C1) ----\n"
                "  # With no plan here and no per-chapter targets in outline.md, C1\n"
                "  # cannot check the contract against anything and reports NOT RUN -\n"
                "  # a self-declared contract is the gap the 2026-10-13 audit found.\n\n"
            )

    # 3. register
    if expected_manuscript:
        append_registry(book_path, args.title, args.status, True)
    else:
        append_registry(book_path, args.title, args.status, False)

    # 4. verify THIS registration, do not assume it. The workspace registry may
    # carry pre-existing problems (books whose finished claims await their
    # evidence) - those are named, but they are not this book's registration
    # failing, and folding them together would say a clean registration broke
    # the suite. A problem naming this book is a failure; anything else is a
    # debt the workspace already had, printed so nobody is surprised.
    proc = subprocess.run(
        [sys.executable, os.path.join(TOOLS_DIR, "check-registry.py"), workspace],
        capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    problems = [ln.strip()[2:].strip() for ln in out.splitlines()
                if ln.strip().startswith("- ")]
    mine = [p for p in problems if book_path in p]
    if proc.returncode == 2:
        print("init-book: the registry itself could not be read (check-registry exit 2).")
        print("  Nothing is verified until it can be. Fix BOOKS.yaml first.")
        return 1
    if mine or (proc.returncode != 0 and not problems):
        print("init-book: the registry check flagged THIS book:")
        for p in (mine or out.splitlines()):
            print(f"  - {p}")
        print("  Fix the registry by hand before running the suite.")
        return 1
    if problems:
        print(f"init-book: this book's registration is verified. The workspace registry")
        print(f"  still reports {len(problems)} pre-existing problem(s), none of them this book:")
        for p in problems:
            print(f"  - {p}")
    else:
        print("init-book: registry verified - disk and registry agree.")

    print(f"init-book: created {book_root}")
    print(f"           registered in BOOKS.yaml as status {args.status}")
    if plan_product and (floor or ceiling):
        print(f"           intake validated: the plan ({plan_product:,} words) sits "
              f"inside the contract [{floor:,}, {ceiling:,}].")
    if args.status in ("drafting", "autonomous"):
        print("           status: in_progress is set - L1 records until you remove it at delivery.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
