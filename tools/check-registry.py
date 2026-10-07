#!/usr/bin/env python3
"""check-registry.py — does the book registry match what is on disk?

This is deliberately NOT a prose gate and is not in GATE_FREEZE.md. It reads no
manuscript text and measures no prose. It belongs to the make-ready layer (the
same exemption class as tools/preflight.sh and the 2026-09-30 entry in
GATE_FREEZE.md): it answers a question about which books exist, not a question
about a book.

Created 2026-10-01, after the all-books suite silently omitted `marrow-light/`
— a finished book — because its book list was hand-typed. The failure had two
directions, and this checks both:

    1. a registered path that no longer exists (a renamed or archived book the
       suite would silently skip), and
    2. a PROJECT_STATE.yaml on disk that is not registered (a book the suite
       does not know about — the marrow-light failure).

Exit codes:
    0  registry and disk agree
    1  a mismatch was found — listed, one line each
    2  no registry found, or no books registered — never means pass

Usage:
    python tools/check-registry.py [workspace_root]
    python tools/check-registry.py --paths     # print registered paths (for loops)

The workspace root defaults to test-books/ inside the incunabula directory
this file lives in — the production layout since 2026-10-07, when the book
projects moved in under incunabula/ and incunabula itself moved to its own
device-level location. Every registered path is relative to that root.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REGISTRY = os.path.join(os.path.dirname(HERE), "BOOKS.yaml")
SKIP_DIRS = {"_archive", ".agents", ".ua", ".git", "node_modules", "dist",
             "vermillion-study", "_verify-clone"}
MAX_DEPTH = 2  # some books live two levels deep (e.g. finished-manuscripts/<slug>)

# Private books: on disk, but deliberately not listed in BOOKS.yaml. The names
# live in .registry-private next to the registry, which is gitignored - the
# public repository must not carry a private book's name. An absent file means
# nothing is private, which is the correct default on a fresh clone.
PRIVATE_FILE = os.path.join(os.path.dirname(DEFAULT_REGISTRY), ".registry-private")


def load_private_dirs():
    """Directory names the registry deliberately does not list.

    One name per line; blank lines and #-comments ignored. These are pruned
    from the direction-2 scan exactly like SKIP_DIRS.
    """
    try:
        with open(PRIVATE_FILE, encoding="utf-8") as fh:
            return {ln.strip() for ln in fh
                    if ln.strip() and not ln.strip().startswith("#")}
    except FileNotFoundError:
        return set()


def parse_registry(path):
    """Minimal reader for the registry's own shape. No YAML dependency.

    Returns a list of {path, status, expected_manuscript} dicts. Only the keys
    the checker needs; everything else in BOOKS.yaml is documentation.
    """
    books, current = [], None
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if re.match(r"^books\s*:", line):
                continue
            m = re.match(r"^\s*-\s+path\s*:\s*(.+?)\s*$", line)
            if m:
                current = {"path": m.group(1).strip().strip("\"'")}
                books.append(current)
                continue
            if current is None:
                continue
            m = re.match(r"^\s*status\s*:\s*(.+?)\s*$", line)
            if m:
                current["status"] = m.group(1).strip().strip("\"'")
                continue
            m = re.match(r"^\s*expected_manuscript\s*:\s*(.+?)\s*$", line)
            if m:
                current["expected_manuscript"] = m.group(1).strip().lower() == "true"
    return books


def find_state_files(workspace, skip):
    """Every PROJECT_STATE.yaml on disk within MAX_DEPTH, skipping known non-books."""
    found = []
    for dirpath, dirnames, filenames in os.walk(workspace):
        rel = os.path.relpath(dirpath, workspace).replace("\\", "/")
        depth = 0 if rel == "." else rel.count("/") + 1
        dirnames[:] = [d for d in dirnames if d not in skip]
        if depth > MAX_DEPTH:
            dirnames[:] = []
            continue
        if "PROJECT_STATE.yaml" in filenames and rel != ".":
            found.append(rel)
    return sorted(found)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--paths" in argv:
        argv.remove("--paths")
        paths_only = True
    else:
        paths_only = False

    registry_path = os.environ.get("BOOKS_REGISTRY", DEFAULT_REGISTRY)
    if not os.path.isfile(registry_path):
        print(f"check-registry: no registry at {registry_path}")
        print("  A suite that reads no registry governs nothing. Exit 2 - never a pass.")
        return 2
    books = parse_registry(registry_path)
    if not books:
        print("check-registry: registry exists but lists no books. Exit 2 - never a pass.")
        return 2

    if paths_only:
        # Windows text mode translates \n to \r\n on stdout, and a consumer that
        # does `for B in $(... --paths)` inherits a carriage return into every
        # book path - which then fails every gate with a path that does not exist.
        # Emit LF exactly, like every other line-oriented tool here.
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(newline="\n")
        for b in books:
            print(b["path"])
        return 0

    workspace = argv[0] if argv else os.path.join(os.path.dirname(HERE), "test-books")

    problems = []

    # Direction 1: registered paths must exist.
    for b in books:
        full = os.path.join(workspace, b["path"])
        if not os.path.isdir(full):
            problems.append(f"registered but MISSING on disk: {b['path']}")
            continue
        has_state = os.path.isfile(os.path.join(full, "PROJECT_STATE.yaml"))
        # A concept book may carry an EMPTY scaffold (the pipeline creates it at
        # intake); what makes it a drafted book is chapter files on disk.
        chapdir = os.path.join(full, "manuscript", "chapters")
        has_chapters = os.path.isdir(chapdir) and any(
            n.startswith("chapter") for n in os.listdir(chapdir))
        status = b.get("status", "")
        if status == "concept":
            if has_chapters:
                problems.append(f"{b['path']}: status concept but manuscript/chapters exists - promote the entry")
            continue
        if not has_state:
            problems.append(f"{b['path']}: status {status} but no PROJECT_STATE.yaml at the book root (ungoverned)")
        if status == "autonomous":
            # A run in flight may sit anywhere between scaffold and delivery —
            # the chapter checks below judge books that claim to HAVE a
            # manuscript. An autonomous book is judged at its own gates instead.
            continue
        expects = b.get("expected_manuscript", True)
        if expects and not has_chapters:
            problems.append(f"{b['path']}: expected_manuscript true but no manuscript/chapters/")
        if not expects and has_chapters:
            problems.append(f"{b['path']}: expected_manuscript false but manuscript/chapters exists")

    # Direction 2: state files on disk must be registered.
    registered = {b["path"] for b in books}
    private = load_private_dirs()
    for rel in find_state_files(workspace, set(SKIP_DIRS) | private):
        if rel not in registered:
            problems.append(f"on disk but NOT REGISTERED: {rel} - the suite will silently skip it")

    if problems:
        print(f"REGISTRY MISMATCH - {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        print("The suite reads BOOKS.yaml. A book missing there is governed by nothing.")
        return 1

    print(f"REGISTRY OK - {len(books)} book(s) registered, disk and registry agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
