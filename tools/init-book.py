#!/usr/bin/env python3
"""init-book.py — scaffold a new book and register it in BOOKS.yaml.

The entry point that makes the 2026-10-01 failure (a finished book absent from
the suite) structurally impossible for new books: there is no moment where a
book directory exists and the registry does not know about it. Every book the
pipeline starts goes through here.

What it does:
    1. creates <workspace>/<path>/ with the directories the pipeline expects
    2. writes a PROJECT_STATE.yaml with the declared length contract and status
    3. appends the book to BOOKS.yaml (the registry the suite reads)
    4. runs tools/check-registry.py so the result is verified, not assumed

What it does NOT do:
    - choose a length contract. A floor of 0 means "not declared"; the gate
      will report NOT APPLICABLE until a real contract is written by intake.
    - write premise, outline, or any prose. Phase work belongs to the pipeline.

Usage:
    python tools/init-book.py --path my-novel --title "My Novel" \
        [--status drafting] [--floor 80000] [--ceiling 95000] [--concept]

    --concept  scaffolds the book but declares expected_manuscript: false;
               prose gates will not apply until it is promoted by editing
               BOOKS.yaml (the registry says so, on one line).
"""

import argparse
import os
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = HERE                                      # incunabula/tools
FRAMEWORK = os.path.dirname(TOOLS_DIR)                # incunabula/
DEFAULT_WORKSPACE = os.path.join(FRAMEWORK, "test-books")  # incunabula/test-books/ (production workspace since 2026-10-07)
REGISTRY = os.environ.get("BOOKS_REGISTRY", os.path.join(FRAMEWORK, "BOOKS.yaml"))

STATUSES = {"concept", "drafting", "complete", "published", "fixture", "autonomous"}


def append_registry(book_path, title, status, expected_manuscript):
    note = {
        "concept": "Concept stage; no manuscript expected yet.",
        "drafting": "Registered at creation by init-book.py.",
        "fixture": "Registered as a fixture by init-book.py.",
        "autonomous": "Autonomous run (random button) - rolled by tools/roll-brief.py, no author at the wheel.",
    }.get(status, "Registered by init-book.py.")
    with open(REGISTRY, "a", encoding="utf-8") as fh:
        fh.write(
            f"\n  - path: {book_path}\n"
            f"    title: \"{title}\"\n"
            f"    status: {status}\n"
            f"    expected_manuscript: {str(expected_manuscript).lower()}\n"
            f"    note: \"{note} ({date.today().isoformat()})\"\n"
        )


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scaffold and register a book.")
    ap.add_argument("--path", required=True,
                    help="book path relative to the workspace root (e.g. my-novel)")
    ap.add_argument("--title", required=True)
    ap.add_argument("--status", default="drafting", choices=sorted(STATUSES))
    ap.add_argument("--floor", type=int, default=0,
                    help="target_floor_words; 0 declares no length contract yet")
    ap.add_argument("--ceiling", type=int, default=0)
    ap.add_argument("--concept", action="store_true",
                    help="shorthand for --status concept (no manuscript expected)")
    args = ap.parse_args(argv)

    if args.concept:
        args.status = "concept"
    book_path = args.path.strip("/").replace("\\", "/")
    if not book_path or book_path.startswith("."):
        ap.error("--path must be a plain relative path like 'my-novel'")

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

    # 2. state file with the declared contract (or the explicit absence of one)
    floor, ceiling = args.floor, args.ceiling
    if floor and not ceiling:
        ceiling = int(floor * 1.15)
    if ceiling and not floor:
        floor = int(ceiling * 0.9)
    with open(os.path.join(book_root, "PROJECT_STATE.yaml"), "w", encoding="utf-8") as fh:
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

    # 3. register
    if expected_manuscript:
        append_registry(book_path, args.title, args.status, True)
    else:
        append_registry(book_path, args.title, args.status, False)

    # 4. verify, do not assume
    import subprocess
    rc = subprocess.call([sys.executable, os.path.join(TOOLS_DIR, "check-registry.py"), workspace])
    if rc != 0:
        print("init-book: the registry check did not pass after registration.")
        print("  Fix the registry by hand before running the suite.")
        return 1

    print(f"init-book: created {book_root}")
    print(f"           registered in BOOKS.yaml as status {args.status}")
    if args.status in ("drafting", "autonomous"):
        print("           status: in_progress is set - L1 records until you remove it at delivery.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
