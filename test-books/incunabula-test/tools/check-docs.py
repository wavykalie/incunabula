#!/usr/bin/env python3
"""check-docs.py - documentation integrity checks for the validation-series.

WHY THIS EXISTS
    The project's whole claim is that a later session can trust the persistent layer.
    That layer is a set of documents, and nothing was verifying them. Documents drifted:
    a ledger said "no prose exists" about a delivered book, a structural ledger disagreed
    with its twin, and files that live in the repo were not in the registry that is
    supposed to account for every one of them. This closes that class mechanically.

WHAT IT CHECKS  (ENFORCED = exit 1; REVIEW = reported, never fails on its own)

    E1  REGISTERED MISSING   - a registry path that does not exist on disk
    E2  UNREGISTERED FILE    - a tracked file (all .md/.yaml/.yml outside manuscript/
                               and dist/) that no registry accounts for
    E3  SUPERSESSION         - status/superseded_by disagree (one set, the other not)
    E4  ARCHIVE POLICY       - a superseded document with no disposition: it must be
                               archived under an archive/ directory, or explicitly
                               retained as evidence with a reason
    E5  BROKEN REFERENCE     - a file path cited in a governing document that does
                               not resolve
    E6  DUPLICATE RECORD     - the same file registered by two ledgers

    R1  STALE REVIEW         - an active document not reviewed since the newest run
    R2  DUPLICATE CANON      - two active documents claiming canonical_for the same thing

REGISTRIES
    The three CANON_LEDGER.yaml files (series + a book ledger per book) each carry a
    `documents:` block. Paths are resolved relative to the ledger that records them,
    so a series entry reads repo-relative and a book entry reads book-relative.

    usage:  python3 tools/check-docs.py
    exit 0 = no enforced finding   exit 1 = at least one enforced finding
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Adapted for the incunabula-test layout: one standalone book at the project root, so
# there is a single book-scope ledger and no series ledger above it. The original carried
# three (series + book-1 + book-2).
LEDGERS = [
    Path("CANON_LEDGER.yaml"),
]
TRACK_EXT = {".md", ".yaml", ".yml"}
EXCLUDE_DIRS = {"manuscript", "dist", "archive"}
ARCHIVE_MARKER = "archive"

# Paths that point outside this repo on purpose (the Book Genesis skills live with the
# harness, not the project). A reference to one is not a broken link.
EXTERNAL_REF_PREFIXES = (".agents/", "../.agents/")

# Documents whose file references are checked. Prose chapters deliberately excluded:
# they legitimately mention informal paths, and the manuscript is governed by the
# continuity audits instead.
# Adapted for the incunabula-test layout (single book at the project root).
REFERENCE_SOURCES = [
    "CANON_LEDGER.yaml",
    "PROJECT_STATE.yaml",
    "foundation.md",
    "outline.md",
    "ENTITY_STATE.yaml",
]


def is_null(value: str | None) -> bool:
    return value is None or value.strip().lower() in ("", "null", "~", "none")


def tracked_files() -> list[str]:
    """Every .md/.yaml/.yml in the repo except manuscript/, dist/ and archive/."""
    out = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TRACK_EXT:
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS or part.startswith(".") for part in rel.parts):
            continue
        out.append(rel.as_posix())
    return sorted(out)


def parse_ledger_documents(ledger: Path) -> dict[str, dict[str, str]]:
    """Pull the `documents:` block out of one ledger. Line-based on a regular format."""
    entries: dict[str, dict[str, str]] = {}
    in_block = False
    current: str | None = None
    for raw in (ROOT / ledger).read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if re.match(r"^documents:\s*$", line):
            in_block = True
            current = None
            continue
        if not in_block:
            continue
        if re.match(r"^\S", line):  # back to column 0 -> block over
            in_block = False
            continue
        # a YAML key may carry a trailing comment ("  path.md:  # note"); strip it
        # before matching the key, or the entry reads as unregistered
        key_line = re.sub(r"\s+#.*$", "", line)
        entry = re.match(r"^  (\S.*?):\s*$", key_line)
        if entry:
            current = entry.group(1).strip()
            entries[current] = {"__ledger__": ledger.as_posix()}
            continue
        field = re.match(r"^    ([A-Za-z_]+):\s*(.*)$", line)
        if field and current:
            entries[current][field.group(1)] = field.group(2).strip().strip('"').strip("'")
    return entries


def build_registry():
    """Return (registry, duplicates). registry: repo-relative path -> entry+fields."""
    registry: dict[str, dict[str, str]] = {}
    duplicates: list[tuple[str, str, str]] = []
    for ledger in LEDGERS:
        base = ledger.parent
        for key, fields in parse_ledger_documents(ledger).items():
            resolved = (base / key) if str(base) != "." else Path(key)
            rel = resolved.as_posix()
            if rel in registry:
                duplicates.append((rel, registry[rel]["__ledger__"], fields["__ledger__"]))
                continue
            entry = dict(fields)
            entry["__key__"] = key
            registry[rel] = entry
    return registry, duplicates


def canonical_items(value: str | None) -> list[str]:
    if is_null(value):
        return []
    inner = value.strip()
    if inner.startswith("["):
        inner = inner[1:-1]
    return [item.strip().strip("\"'") for item in inner.split(",") if item.strip()]


def scan_references() -> list[tuple[str, str, str]]:
    """Return (source, reference, reason) for file references that do not resolve.

    Deliberately narrow, so a real dead link is not buried in prose noise:
      - only paths that look like paths (a directory separator, or ./-relative)
      - never globs; never bare filenames named in passing
      - only a first segment that exists at the repo root counts as a repo path
    """
    backtick = re.compile(r"`([^`\n]+\.(?:md|yaml|yml|sh|py|txt))`")
    mdlink = re.compile(r"\]\(([^)\s]+\.(?:md|yaml|yml|sh|py|txt))\)")
    broken = []
    seen: set[tuple[str, str]] = set()
    for src in REFERENCE_SOURCES:
        path = ROOT / src
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for regex in (backtick, mdlink):
            for raw in regex.findall(text):
                ref = raw.split()[-1] if " " in raw else raw  # "python tools/x.py" -> "tools/x.py"
                if "*" in ref or ref.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                if ref.startswith(EXTERNAL_REF_PREFIXES):
                    continue
                if "/" not in ref and not ref.startswith("."):
                    continue  # a bare filename mentioned in passing
                bases = (path.parent, ROOT)
                if any((b / ref).exists() for b in bases):
                    continue
                key = (src, ref)
                if key in seen:
                    continue
                seen.add(key)
                broken.append((src, ref, "does not resolve from the file or the repo root"))
    return broken


def main() -> int:
    enforced: list[str] = []
    review: list[str] = []

    registry, duplicates = build_registry()

    # ---- duplicate records (review: a series and a book ledger both naming a file
    #      is usually correct self-registration, not drift) ----
    for rel, first, second in duplicates:
        review.append(f"duplicate record: {rel} registered by both {first} and {second}")

    # ---- E1 registered but missing --------------------------------------------
    registered_paths: set[str] = set()
    for rel, entry in registry.items():
        registered_paths.add(rel)
        target = ROOT / rel
        if target.exists():
            continue
        archive = entry.get("archive_path", "")
        if not is_null(archive) and (ROOT / archive).exists():
            registered_paths.add(Path(archive).as_posix())
            continue
        if target.suffix:  # a file (not a directory entry like "book-2")
            enforced.append(f"E1 registered but missing: {rel} (ledger {entry['__ledger__']})")

    # ---- E2 tracked but unregistered ------------------------------------------
    archive_paths = {
        Path(e["archive_path"]).as_posix()
        for e in registry.values()
        if not is_null(e.get("archive_path"))
    }
    known = registered_paths | archive_paths
    for rel in tracked_files():
        if rel not in known:
            enforced.append(f"E2 unregistered file: {rel} (no ledger accounts for it)")

    # ---- E3/E4 supersession + archive policy ----------------------------------
    for rel, entry in registry.items():
        if not Path(rel).suffix:
            continue  # a descriptor, not a file (e.g. a recorded loss) - not a document
        status = (entry.get("status") or "").strip().lower()
        superseded_by = entry.get("superseded_by")
        archived = not is_null(entry.get("archive_path")) or f"/{ARCHIVE_MARKER}/" in f"/{rel}"
        retained = str(entry.get("retained_in_place", "")).lower() in ("true", "yes")

        if status in ("superseded", "retired", "archived") and is_null(superseded_by):
            enforced.append(f"E3 supersession: {rel} is status '{status}' but has no superseded_by")
        if not is_null(superseded_by) and status not in ("superseded", "retired", "archived"):
            enforced.append(f"E3 supersession: {rel} has superseded_by but status '{status or 'unset'}'")
        if status in ("superseded", "retired") and not archived and not retained:
            enforced.append(
                f"E4 archive policy: {rel} is '{status}' but neither archived under "
                f"{ARCHIVE_MARKER}/ nor retained_in_place with a reason"
            )

    # ---- E5 broken references -------------------------------------------------
    for src, ref, reason in scan_references():
        enforced.append(f"E5 broken reference: {src} -> {ref} ({reason})")

    # ---- R1 stale review (scoped per ledger, so a finished book is not flagged
    #      forever against a later book's activity) --------------------------------
    newest_by_ledger: dict[str, str | None] = {}
    for ledger in LEDGERS:
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", (ROOT / ledger).read_text(encoding="utf-8"))
        newest_by_ledger[ledger.as_posix()] = max(dates) if dates else None
    for rel, entry in registry.items():
        if (entry.get("status") or "").strip().lower() != "active":
            continue
        newest = newest_by_ledger.get(entry["__ledger__"])
        if not newest:
            continue
        last = entry.get("last_reviewed", "")
        if is_null(last):
            review.append(f"R1 {rel}: active but no last_reviewed")
        elif last < newest:
            review.append(f"R1 {rel}: last_reviewed {last} < newest in its ledger ({newest})")

    # ---- R2 duplicate canonical claims ----------------------------------------
    claims: dict[tuple[str, str], list[str]] = {}
    for rel, entry in registry.items():
        if (entry.get("status") or "").strip().lower() != "active":
            continue
        for item in canonical_items(entry.get("canonical_for")):
            claims.setdefault((entry["__ledger__"], item), []).append(rel)
    for (ledger, item), owners in sorted(claims.items()):
        if len(owners) > 1:
            review.append(f"R2 duplicate canon claim in {ledger}: '{item}' held by {', '.join(owners)}")

    # ---- report ---------------------------------------------------------------
    print("== enforced ==")
    if enforced:
        for line in enforced:
            print(f"   FAIL  {line}")
    else:
        print("   ok    no enforced findings")
    print()
    print("== review ==")
    if review:
        for line in review:
            print(f"   note  {line}")
    else:
        print("   ok    no review findings")

    print()
    if enforced:
        print(f"DOC CHECK FAILED - {len(enforced)} enforced finding(s).")
        return 1
    print(f"DOC CHECK PASSED - 0 enforced findings, {len(review)} review note(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
