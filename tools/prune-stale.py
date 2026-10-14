#!/usr/bin/env python3
"""prune-stale.py — the self-prune: keep the records true to the program.

WHY THIS EXISTS
  The record files (ERRATA.md, GATE_FREEZE.md, KNOWN_FINDINGS.md and the rest) carry
  claims about the CURRENT program — how many controls the suite runs, how many entries
  a registry holds — and the program moves while the claims stand still. The failure is
  quiet and it is the same shape this project keeps finding: a reader trusts a number
  that was true once. The author found exactly this — a stale fragment glued to the top
  of ERRATA.md claiming "the ten controls" against a suite that runs nineteen — and the
  ledger's own contract (append-only) had no legal way to fix it. This tool is that way.

WHAT IT DOES
  It measures the live program and compares the record files against it:

    recount      a standing count claim (controls, registry rows, entry totals) that the
                 live program contradicts -> the number is rewritten to the measured one.
    fragment     a table fragment glued onto a markdown heading (corruption that also
                 hides stale claims) -> the heading is restored, the fragment pruned.
    status-prose a book's state/planning file asserting "no prose exists" / "still not
                 drafted" while that book's own manuscript has chapters with words ->
                 the disproven sentence is pruned. The inverse (status: complete with an
                 empty manuscript) is NOT touched — see REVIEW below.
    copy         a book carrying its own copy of the instruments (name-matched against
                 tools/, the same rule as preflight.sh row 6) -> quarantined under
                 <book>/_archive/tools/, never deleted.
    cache        __pycache__/ and *.pyc outside _archive/ — derived, regenerable
                 bytecode that runs leave behind -> removed and logged.

  Every repair is written to maintenance/PRUNING_LOG.md (the repo root log for record
  files, the book's own log for book records) with the OLD WORDING VERBATIM, the
  replacement, the reason, and the date — the format maintenance-protocol.md §7
  requires. Pruning reduces what a reader has to trust; it does not erase history.

WHAT IT REFUSES TO DO  (and why, per maintenance-protocol.md §7 and §9)
  - It never edits a DATED entry. An entry records what was measured, decided or done on
    a date; correcting its numbers would falsify history. A stale claim inside one is
    reported as REVIEW with the live measurement and a suggested replacement, for the
    author to rule on. "An absence is not a decision" — and neither is a guess.
  - It never edits a claim framed in the past ("at freeze", "as shipped", "was ..."):
    that is a historical statement, not a standing one.
  - It never DELETES a document. Copies are moved to _archive/ (with an index entry, per
    §7); the only deletions are regenerable bytecode caches, and those are logged.
  - It never touches the frozen instruments in tools/prose/, USER_PREFERENCES.md or
    PREFERENCES.md (declared taste is immutable, SELF_IMPROVEMENT.md §6.2), and it never
    moves a threshold or a hash — measurement surfaces belong to the freeze procedure.
  - It never upgrades state: a book claiming `status: complete` over an empty manuscript
    is REVIEW, because choosing the truthful status is the author's call (that is the
    same open decision check-registry.py reports).

  REVIEW items never fail --check; a repair that could not be made is named, not passed.

USAGE
  python tools/prune-stale.py            # same as --check
  python tools/prune-stale.py --check    # report; change nothing
  python tools/prune-stale.py --apply    # repair what is provable, log, report the rest
  python tools/prune-stale.py --self-test
  python tools/prune-stale.py --check --root PATH   (self-test uses this)

EXIT
  --check    0 = nothing repairable (REVIEW items may exist and are named)
             1 = repairable staleness found
  --apply    0 = everything provable repaired and logged
             1 = a repair failed or could not be written
  --self-test 0 = every assertion held, 1 = an assertion failed
  2 = could not run at all.
"""

import os
import re
import shutil
import sys
import tempfile
from datetime import date

# ---------------------------------------------------------------------------
# What counts as "dated history" vs "a standing claim about the present".
# ---------------------------------------------------------------------------

DATED_HEADING = re.compile(r"^#{1,3}\s.*\b20\d{2}-\d{2}-\d{2}\b")
DATE_ANYWHERE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
# Temporal framing: the sentence is talking about a past state of the program, so the
# number in it is a record, not a claim. Curated tight on purpose — a false "historical"
# reading leaves a stale claim standing (reported), while a false "standing" reading
# rewrites history. The asymmetry is why the list leans conservative.
TEMPORAL = re.compile(
    r"(?i)\bwas\b|\bwere\b|\bat freeze\b|\bat freeze \d|\bas shipped\b"
    r"|\bused to\b|\bpreviously\b|\bformerly\b|\bback when\b|\bhad been\b"
)
# A markdown heading glued behind other content on one line: "... |# ERRATA".
GLUED = re.compile(r"^[^#\s].*?\|#")

WORDNUM = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
    8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
    19: "nineteen", 20: "twenty",
}
NUMWORD = {v: k for k, v in WORDNUM.items()}
NUMWORD.update({str(k): k for k in WORDNUM})

RECORD_FILES = [
    "ERRATA.md", "KNOWN_FINDINGS.md", "COMMONPLACE.md", "GATE_FREEZE.md",
    "SELF_IMPROVEMENT.md", "PRINTERS_COPY.md", "README.md",
]

# Stale-status rule, ported from tools/check-stale-status.sh (which lives inside books):
# a file that asserts the work is NOT done while its own fields assert completion.
STALE_PHRASES = (
    "no prose exists", "still not drafted", "not yet drafted", "not yet introduced",
    "zero chapters", "nothing past phase 0 has run", "no research has been run",
    "still not chosen",
)
COMPLETION = (
    r'status: "?(complete|completed)"?', r"DELIVERED",
    r"(drafted_total|manuscript_words): [1-9]", r'prose_gate_all_chapters: "?[1-9]',
)
ENFORCED_NAMES = (
    "PROJECT_STATE.yaml", "STATE.yaml", "ENTITY_STATE.yaml", "CANON_LEDGER.yaml",
    "foundation.md", "outline.md",
)
ADVISORY_RE = re.compile(r"(^|/)(README\.md|continuity/[^/]+\.md)$")

STUB = "(pruned {d} - stale claim; wording preserved in maintenance/PRUNING_LOG.md)"


# ---------------------------------------------------------------------------
# Live measurements. Every repair in this tool is one of these numbers; when a
# measurement cannot be made, nothing is repaired — an absence is not a decision.
# ---------------------------------------------------------------------------

def read_raw(path):
    # newline="" keeps CRLF byte-exact: .gitattributes stores every file unconverted
    # (`* -text`) because the freeze hashes were taken against these exact bytes.
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def write_raw(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def count_controls(root):
    """How many controls validate-controls.sh runs, from its own section headers.

    COUNTED, not read off a denominator. The `Control n/m` totals are historical
    debris — 5, 7, 9, 10, 11, 12 and 19 all appear in the live file, because controls
    were added in batches and the old headers were never renumbered. Every header is
    one control that runs, so the header count is the size of the suite; an earlier
    version averaged the denominators, threw up its hands at the disagreement, and
    returned None — which silently removed the `controls` claim from everything this
    tool checks. A measurement that gives up must say so, not vanish.
    """
    path = os.path.join(root, "tools", "prose", "validate-controls.sh")
    if not os.path.isfile(path):
        return None
    marks = re.findall(r'^(?:echo\s+)?"?=== Control (\d+)/(\d+)', read_raw(path), re.M)
    return len(marks) if marks else None


def count_errata_entries(root):
    """Same rule tools/prose/check-errata.py counts with (its ENTRY regex)."""
    path = os.path.join(root, "ERRATA.md")
    if not os.path.isfile(path):
        return None
    return len(re.findall(r"^### \d{4}-\d{2}-\d{2}\s+—\s+.+$", read_raw(path), re.M))


def count_printers(root):
    """(rejected, confirmed) registry rows in PRINTERS_COPY.md — table rows, not prose.

    Mirrors check-errata.py's rejected_count() so the pruner and the protocol guard
    can never disagree about the number they are each protecting.
    """
    path = os.path.join(root, "PRINTERS_COPY.md")
    if not os.path.isfile(path):
        return (None, None)

    def rows(section):
        m = re.search(rf"^##\s*{section}\..*?^(?=^##\s)", read_raw(path), re.M | re.S)
        if not m:
            return None
        return sum(
            1 for line in m.group(0).splitlines()
            if line.strip().startswith("|") and "---" not in line
            and not re.match(r"^\|\s*(measure|row)\s*\|", line.strip())
        )

    return (rows(4), rows(3))


def count_projects(root, gaining=()):
    """(total live book projects, how many carry maintenance/PRUNING_LOG.md).

    `gaining` names the books this run is about to write a log for. The count is
    self-referential — repairing a book record creates that book's log — so the
    measurement has to be as of the END of the run or the tool would repair the same
    claim to a number that is stale before it lands.
    """
    base = os.path.join(root, "test-books")
    if not os.path.isdir(base):
        return (None, None)
    projects = [
        d for d in sorted(os.listdir(base))
        if os.path.isdir(os.path.join(base, d)) and not d.startswith("_") and d != "epubs"
    ]
    with_log = [
        d for d in projects
        if os.path.isfile(os.path.join(base, d, "maintenance", "PRUNING_LOG.md"))
        or d in gaining
    ]
    return (len(projects), len(with_log))


def manuscript_words(book):
    total = 0
    chapters = os.path.join(book, "manuscript", "chapters")
    if not os.path.isdir(chapters):
        return 0
    for name in os.listdir(chapters):
        if not name.lower().endswith((".md", ".txt")):
            continue
        try:
            with open(os.path.join(chapters, name), encoding="utf-8", errors="ignore") as fh:
                total += len(fh.read().split())
        except OSError:
            continue
    return total


def measure(root, gaining=()):
    rej, conf = count_printers(root)
    projects, with_log = count_projects(root, gaining)
    return {
        "controls": count_controls(root),
        "errata_entries": count_errata_entries(root),
        "rejected": rej,
        "confirmed": conf,
        "projects": projects,
        "projects_with_log": with_log,
    }


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

class Finding:
    def __init__(self, action, kind, path, line_no, old, new, reason, suggestion=None):
        self.action = action        # repair | review | quarantine | delete
        self.kind = kind            # recount | fragment | status-prose | copy | cache | claim
        self.path = path            # workspace-relative
        self.line_no = line_no      # 1-based, or 0 for file-level actions
        self.old = old
        self.new = new
        self.reason = reason
        self.suggestion = suggestion


def fmt_num(n, as_word):
    return WORDNUM.get(n, str(n)) if as_word else str(n)


def claim_specs(m):
    """The standing claims this tool knows how to measure. Each maps a regex capture
    onto a live measurement; anything outside this table is never rewritten."""
    specs = []

    def add(name, pattern, live, describe):
        specs.append((name, re.compile(pattern), live, describe))

    if m.get("controls") is not None:
        n = m["controls"]
        add(
            "controls",
            # "all N controls" / "the N controls" ONLY — a bare "N controls" is
            # almost always a record of one run ("10 of 11 controls green", "6 controls
            # proven, 5 skipped") or a subset reference ("those four controls [4–7]",
            # "three controls (the scanner, ...)"). Rewriting those would falsify a
            # measurement and corrupt the reference; a draft of this pattern did both
            # and the dry run caught it. Plural `controls` also drops attributive
            # singulars ("1 control book", "22 control chapters").
            r"(?i)\b(all|the)(\s+)(one|two|three|four|five|six|seven|eight|nine|ten"
            r"|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen"
            r"|nineteen|twenty|\d+)(\s+controls\b)",
            lambda g: (
                (g.group(3).lower() in NUMWORD and NUMWORD[g.group(3).lower()] == n)
                or (g.group(3).isdigit() and int(g.group(3)) == n)
            ),
            lambda g: (g.group(1) + g.group(2)
                       + fmt_num(n, g.group(3).lower() in NUMWORD) + g.group(4)),
        )
    if m.get("errata_entries") is not None:
        add(
            "errata-entries",
            r"(`ERRATA\.md`\s*[-—]\s*)(\d+)(\s+entries\b)",
            lambda g: int(g.group(2)) == m["errata_entries"],
            lambda g: g.group(1) + str(m["errata_entries"]) + g.group(3),
        )
    if m.get("rejected") is not None and m.get("confirmed") is not None:
        add(
            "printers-counts",
            r"(`PRINTERS_COPY\.md`\s*[-—]\s*)(\d+)(\s+rejected measures,\s*)(\d+)(\s+confirmed\b)",
            lambda g: int(g.group(2)) == m["rejected"] and int(g.group(4)) == m["confirmed"],
            lambda g: g.group(1) + str(m["rejected"]) + g.group(3) + str(m["confirmed"]) + g.group(5),
        )
    if m.get("projects") is not None:
        add(
            "projects",
            r"(\d+)(\s+of\s+)(\d+)(\s+live projects?\b)",
            lambda g: (int(g.group(1)) == m["projects_with_log"]
                       and int(g.group(3)) == m["projects"]),
            lambda g: (
                str(m["projects_with_log"]) + g.group(2)
                + str(m["projects"]) + g.group(4)
            ),
        )
    return specs


# ---------------------------------------------------------------------------
# Record-file scan
# ---------------------------------------------------------------------------

def record_findings(root, m):
    findings = []
    for rel in RECORD_FILES:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        lines = read_raw(path).splitlines(keepends=True)
        # "history" zones hold records of what was measured/done — never rewritten.
        # ERRATA: dated entries (### or ## with a date). GATE_FREEZE: the one-line-each
        # freeze table and every `## Freeze` section. Everywhere else is standing text,
        # where a present-tense claim is exactly the drift this tool exists to fix.
        zone = "standing"
        for i, raw in enumerate(lines):
            body = raw.rstrip("\r\n")
            if re.match(r"^#{1,3}\s", body):
                if rel == "GATE_FREEZE.md":
                    if re.match(r"^##\s+Manifest", body):
                        zone = "standing"
                    elif (DATED_HEADING.match(body)
                          or re.match(r"^##\s+(Every freeze|Freeze)", body)):
                        zone = "history"
                    else:
                        zone = "standing"
                elif rel == "ERRATA.md":
                    zone = "history" if DATED_HEADING.match(body) else "standing"
                else:
                    zone = "standing"

            glued = GLUED.match(body)
            if glued:
                at = body.find("|#")
                fragment = body[:at]
                heading = body[at + 1:].strip()
                findings.append(Finding(
                    "repair", "fragment", rel, i + 1, body, heading,
                    "a table fragment is glued onto a markdown heading; the fragment is "
                    "itself a stale copy of a GATE_FREEZE manifest cell. The heading is "
                    "restored and the fragment is preserved in the pruning log.",
                ))
                continue

            historic = zone == "history" or bool(TEMPORAL.search(body))
            hits = []   # (start, end, spec-name, replacement), merged per line
            for name, rx, is_live, build in claim_specs(m):
                for g in rx.finditer(body):
                    if is_live(g):
                        continue
                    if any(not (g.end() <= s or g.start() >= e) for s, e, _, _ in hits):
                        continue
                    hits.append((g.start(), g.end(), name, build(g)))
            if not hits:
                continue
            # Prose after the claim that this tool cannot rebuild as a whole — a
            # wrapped list, a parenthetical of names. Half-fixing the numbers would
            # leave a NEW inconsistency beside them, so the line is reported instead.
            wrapped = any("(" in body[e:] for _, e, _, _ in hits)
            hits.sort()
            new_body = body
            for s, e, _n, rep in reversed(hits):
                new_body = new_body[:s] + rep + new_body[e:]
            names = "+".join(sorted({h[2] for h in hits}))
            if historic:
                findings.append(Finding(
                    "review", "claim", rel, i + 1, body, new_body,
                    f"stale {names} claim, but the line is dated history or past "
                    f"framing — history is never rewritten here",
                    suggestion=new_body,
                ))
            elif wrapped:
                findings.append(Finding(
                    "review", "claim", rel, i + 1, body, new_body,
                    f"stale {names} claim, but prose follows it on the line that cannot "
                    f"be rebuilt as a whole — reported, never half-fixed",
                    suggestion=new_body,
                ))
            else:
                findings.append(Finding(
                    "repair", "recount", rel, i + 1, body, new_body,
                    f"standing {names} claim disagrees with the live program "
                    f"(measured at run time from the tools themselves)",
                ))
    return findings


# ---------------------------------------------------------------------------
# Book scan: stale status prose, instrument copies, caches
# ---------------------------------------------------------------------------

def live_instrument_names(root):
    names = set()
    base = os.path.join(root, "tools")
    for dirpath, _dirs, files in os.walk(base):
        for name in files:
            if name.endswith((".py", ".sh", ".tsv")):
                names.add(name)
    return names


def iter_book_dirs(root):
    base = os.path.join(root, "test-books")
    if not os.path.isdir(base):
        return
    for name in sorted(os.listdir(base)):
        book = os.path.join(base, name)
        if os.path.isdir(book) and not name.startswith("_") and name != "epubs":
            yield book


def book_findings(root):
    findings = []
    instruments = live_instrument_names(root)
    for book in iter_book_dirs(root):
        rel_book = os.path.relpath(book, root).replace(os.sep, "/")
        words = manuscript_words(book)

        # 1. stale status prose in state/planning files
        for dirpath, dirs, files in os.walk(book):
            dirs[:] = [d for d in dirs if not d.startswith("_") and d != ".git"]
            for name in files:
                if name not in ENFORCED_NAMES:
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                raw = read_raw(path)
                hits = [p for p in STALE_PHRASES if p in raw.lower()]
                if not hits:
                    continue
                completes = any(re.search(c, raw) for c in COMPLETION)
                if words >= 200 and completes:
                    stub = STUB.format(d=date.today().isoformat())
                    lines = raw.splitlines(keepends=True)
                    for i, ln in enumerate(lines):
                        low = ln.lower()
                        if not any(p in low for p in hits):
                            continue
                        body = ln.rstrip("\r\n")
                        if body.lstrip().startswith("#") or TEMPORAL.search(body):
                            findings.append(Finding(
                                "review", "claim", rel, i + 1, body, body,
                                "not-done prose, but the line is a comment or past "
                                "framing — reported, never rewritten",
                            ))
                            continue
                        # Phrase-span, not sentence-span: in a YAML state file the
                        # sentence IS the whole `key: "..."` line, and stubbing the
                        # sentence would delete the key with it. The phrase is the
                        # stale claim; the line around it is structure.
                        new_body = body
                        for p in hits:
                            if p in new_body.lower():
                                new_body = re.sub(re.escape(p), stub, new_body,
                                                  flags=re.I)
                        findings.append(Finding(
                            "repair", "status-prose", rel, i + 1, body, new_body,
                            f"the sentence asserts the work is not done, but the "
                            f"manuscript holds {words} words across "
                            f"{rel_book}/manuscript/chapters — the prose is stale",
                        ))
                elif words == 0 and completes:
                    findings.append(Finding(
                        "review", "claim", rel, 0,
                        "; ".join(hits), "; ".join(hits),
                        "file asserts completion but the manuscript holds no words — "
                        "which side is stale is the author's decision (the same open "
                        "decision check-registry.py reports), so nothing is touched",
                        suggestion="write the pass evidence, or record a truthful status",
                    ))
                else:
                    findings.append(Finding(
                        "review", "claim", rel, 0,
                        "; ".join(hits), "; ".join(hits),
                        f"not-done prose found ({rel_book}: {words} manuscript words) "
                        f"but this file carries no completion signal — historical, or "
                        f"stale? A ruling needed",
                    ))

        # 2. book-carried copies of the instruments (preflight.sh row 6's matcher)
        for dirpath, dirs, files in os.walk(book):
            dirs[:] = [d for d in dirs if not d.startswith("_") and d != ".git"]
            for name in files:
                if name not in instruments:
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                inside = os.path.relpath(path, book).replace(os.sep, "/")
                target = f"{rel_book}/_archive/{inside}"
                findings.append(Finding(
                    "quarantine", "copy", rel, 0, rel, target,
                    "a book-carried copy of the instrument: a stale copy mis-measures "
                    "(the quarantined check-uniformity.py fails U1 at 30% against the "
                    "frozen copy's 22%), and a result must be attributable to one known "
                    "instrument. Quarantined, never deleted (maintenance-protocol §7).",
                ))

        # 3. regenerable bytecode caches
        for dirpath, dirs, files in os.walk(book):
            dirs[:] = [d for d in dirs if d != "_archive"]
            for d in list(dirs):
                if d == "__pycache__":
                    findings.append(Finding(
                        "delete", "cache", os.path.relpath(os.path.join(dirpath, d), root)
                        .replace(os.sep, "/"), 0, d, "",
                        "derived bytecode cache left by a run — regenerable, holds no "
                        "source information; deletion logged per the pruning log rule",
                    ))
    return findings


# ---------------------------------------------------------------------------
# The pruning log
# ---------------------------------------------------------------------------

def log_entry(f, verb):
    lines = [
        f"- **date:** {date.today().isoformat()}",
        f"- **path:** {f.path}" + (f":{f.line_no}" if f.line_no else ""),
        f"- **action:** {verb} ({f.kind})",
    ]
    if verb == "quarantined":
        lines.append(f"- **archive path:** {f.new}")
    else:
        lines.append("- **archive path:** none — the wording is preserved below, verbatim")
    if f.old:
        old = f.old if len(f.old) <= 400 else f.old[:400] + " …"
        lines.append(f"- **old wording:** {old}")
    if f.new and f.new != f.old:
        new = f.new if len(f.new) <= 400 else f.new[:400] + " …"
        lines.append(f"- **replacement:** {new}")
    else:
        lines.append("- **replacement:** none — removed")
    lines.append(f"- **reason:** {f.reason}")
    lines.append("- **authority:** author direction 2026-10-14 — the self-prune corrects "
                 "standing claims the live program contradicts, in place, with the old "
                 "wording preserved here (ERRATA.md header amendment; "
                 "SELF_IMPROVEMENT.md §6.3)")
    return "\n".join(lines) + "\n"


def append_log(root, scope, entries):
    """scope: None for the repo root log, or a book dir for that book's log."""
    if scope is None:
        log_dir = os.path.join(root, "maintenance")
        scope_rel = "maintenance"
    else:
        log_dir = os.path.join(scope, "maintenance")
        scope_rel = os.path.relpath(scope, root).replace(os.sep, "/") + "/maintenance"
    log_path = os.path.join(log_dir, "PRUNING_LOG.md")
    os.makedirs(log_dir, exist_ok=True)
    if not os.path.isfile(log_path):
        write_raw(log_path, (
            "# PRUNING LOG\n\n"
            "Append-only. Format per `skills/incunabula-codex/references/"
            "maintenance-protocol.md` §7: path, archive path, replacement, reason, date.\n"
            "Written by `tools/prune-stale.py`; entries record what was pruned and keep "
            "the old wording verbatim — pruning reduces what a reader must trust, it "
            "does not erase history.\n"
        ))
    existing = read_raw(log_path)
    marks = [int(x) for x in re.findall(r"^## (\d+) —", existing, re.M)]
    n = (max(marks) + 1) if marks else 1
    chunks = []
    for f in entries:
        verb = {"repair": "corrected in place", "quarantine": "quarantined",
                "delete": "deleted (derived, regenerable)"}[f.action]
        chunks.append(f"## {n:03d} — {date.today().isoformat()} — {f.kind}: {f.path}\n\n"
                      + log_entry(f, verb))
        n += 1
    write_raw(log_path, existing + ("\n" if not existing.endswith("\n") else "")
              + "\n".join(chunks))
    return log_path, len(chunks)


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

def apply_findings(root, findings):
    errors = []
    repairs = [f for f in findings if f.action == "repair"]
    quars = [f for f in findings if f.action == "quarantine"]
    deletes = [f for f in findings if f.action == "delete"]

    # --- in-place repairs, grouped by file -------------------------------
    by_file = {}
    for f in repairs:
        by_file.setdefault(f.path, []).append(f)
    for rel, flist in by_file.items():
        path = os.path.join(root, rel)
        try:
            lines = read_raw(path).splitlines(keepends=True)
            for f in flist:
                if f.kind == "fragment":
                    # restore the heading as the line; the fragment is log-only.
                    # EOL preserved: .gitattributes stores every file byte-exact.
                    old_line = lines[f.line_no - 1]
                    eol = "\r\n" if old_line.endswith("\r\n") else "\n"
                    lines[f.line_no - 1] = f.new + eol
                else:
                    body = lines[f.line_no - 1].rstrip("\r\n")
                    eol = lines[f.line_no - 1][len(body):]
                    lines[f.line_no - 1] = f.new + eol
            write_raw(path, "".join(lines))
        except OSError as e:
            errors.append(f"{rel}: {e}")

    # --- quarantines -----------------------------------------------------
    for f in quars:
        src = os.path.join(root, f.path)
        dst = os.path.join(root, f.new)
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(dst):
                errors.append(f"{f.path}: target exists, not overwritten — {f.new}")
                continue
            shutil.move(src, dst)
            # The index lives at the _archive ROOT (protocol §7 names
            # `_archive/README.md`), naming where each quarantined item went.
            arc_root = f.new.split("/_archive/")[0] + "/_archive"
            idx = os.path.join(root, arc_root, "README.md")
            entry = (f"- `{os.path.basename(f.path)}` — quarantined "
                     f"{date.today().isoformat()} from `{f.path}` by "
                     f"`tools/prune-stale.py` (book-carried copy of the instrument; see "
                     f"the book's `maintenance/PRUNING_LOG.md`).\n")
            if not os.path.isfile(idx):
                write_raw(idx, "# _archive index\n\n"
                          "Required by maintenance-protocol.md §7: a new subdirectory "
                          "under `_archive/` gets an entry here.\n")
            write_raw(idx, read_raw(idx) + entry)
        except OSError as e:
            errors.append(f"{f.path}: {e}")

    # --- cache deletions -------------------------------------------------
    for f in deletes:
        path = os.path.join(root, f.path)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
        except OSError as e:
            errors.append(f"{f.path}: {e}")

    # --- the pruning logs ------------------------------------------------
    root_entries = [f for f in repairs + quars + deletes
                    if not f.path.startswith("test-books/")]
    book_entries = {}
    for f in repairs + quars + deletes:
        if f.path.startswith("test-books/"):
            book = "/".join(f.path.split("/")[:2])
            book_entries.setdefault(book, []).append(f)
    written = []
    if root_entries:
        written.append(append_log(root, None, root_entries))
    for book, entries in book_entries.items():
        written.append(append_log(root, os.path.join(root, book), entries))

    # --- GATE_FREEZE.md gets its own dated note, per the 2026-10-13 precedent ---
    if any(f.path in ("GATE_FREEZE.md", "ERRATA.md", "KNOWN_FINDINGS.md",
                      "PRINTERS_COPY.md") for f in repairs):
        note_freeze_history(root, repairs)

    return errors, written


def note_freeze_history(root, repairs):
    """A summary-count catch-up is logged in GATE_FREEZE.md's own history table with a
    date and a reason — the recorded freeze procedure (see the 2026-10-13 row). No check
    changed and no hash moved; this only annotates."""
    path = os.path.join(root, "GATE_FREEZE.md")
    raw = read_raw(path)
    lines = raw.splitlines(keepends=True)
    noted = {"GATE_FREEZE.md", "ERRATA.md", "KNOWN_FINDINGS.md", "PRINTERS_COPY.md"}
    desc = "; ".join(sorted({f.path for f in repairs if f.path in noted}))
    row = (f"| ({date.today().isoformat()}) | | Record files caught up with the live "
           f"program by `tools/prune-stale.py` ({desc}) — self-prune, author direction "
           f"2026-10-14. No check changed and no hash moved; old wording in "
           f"`maintenance/PRUNING_LOG.md`. |")
    if desc in raw:
        return
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("## Every freeze so far"):
            start = i
            break
    if start is None:
        return
    last = None
    for i in range(start, len(lines)):
        if lines[i].startswith("## ") and i > start:
            break
        if lines[i].startswith("|"):
            last = i
    if last is None:
        return
    eol = "\r\n" if lines[last].endswith("\r\n") else "\n"
    lines.insert(last + 1, row + eol)
    write_raw(path, "".join(lines))


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def safe(s):
    # cp1252 consoles mangle em dashes when echoing quoted excerpts back.
    return s.encode("ascii", "replace").decode("ascii")


def report(root, m, findings, mode):
    print("=" * 67)
    print("prune-stale — records measured against the live program")
    print(f"mode: {mode}")
    # A measurement this tool could not take is SHOWN as not measured. An absence
    # is not a decision, and hiding it here is how the controls claim escaped the
    # whole check once already.
    meas = " · ".join(
        f"{k}={v if v is not None else 'NOT MEASURED'}" for k, v in m.items()
    ) or "no measurements available"
    print(f"measured: {meas}")
    print("=" * 67)
    if not findings:
        print("  CLEAN — every standing claim matches the live program.")
        return
    for f in findings:
        tag = {"repair": "REPAIR", "review": "REVIEW", "quarantine": "QUARANTINE",
               "delete": "DELETE"}[f.action]
        where = f.path + (f":{f.line_no}" if f.line_no else "")
        print(f"  {tag:9} {where}  [{f.kind}]")
        if f.old:
            print(f"            was: {safe(f.old)[:160]}")
        if f.action == "repair" and f.new != f.old:
            print(f"            now: {safe(f.new)[:160]}")
        if f.suggestion:
            print(f"            suggest: {safe(f.suggestion)[:160]}")
        print(f"            why: {safe(f.reason)[:200]}")
    n_rep = sum(1 for f in findings if f.action == "repair")
    n_rev = sum(1 for f in findings if f.action == "review")
    n_quar = sum(1 for f in findings if f.action == "quarantine")
    n_del = sum(1 for f in findings if f.action == "delete")
    print("-" * 67)
    print(f"  {n_rep} repairable · {n_rev} REVIEW (never auto-fixed) · "
          f"{n_quar} to quarantine · {n_del} caches")
    if n_rev:
        print("  REVIEW items need a ruling — history is reported, never rewritten.")


# ---------------------------------------------------------------------------
# Self-test: a pruner that has never fired is not a pruner.
# ---------------------------------------------------------------------------

def self_test():
    checks = []

    def ok(cond, label):
        checks.append((bool(cond), label))

    tmp = tempfile.mkdtemp(prefix="prune-stale-")
    try:
        # --- fixture workspace ---
        os.makedirs(os.path.join(tmp, "tools", "prose"))
        # Deliberately inconsistent denominators: the live suite's headers grew by
        # batch (1/5 ... 13/19 ... 19/19) and were never renumbered. The count must
        # come from the headers, or the measurement silently disappears.
        write_raw(os.path.join(tmp, "tools", "prose", "validate-controls.sh"),
                  'echo "=== Control 1/5: a"\necho "=== Control 2/7: b"\n')
        write_raw(os.path.join(tmp, "tools", "prose", "check-uniformity.py"),
                  "# fixture instrument\n")
        write_raw(os.path.join(tmp, "PRINTERS_COPY.md"),
                  "## 3. Confirmed\n\n| row | what |\n|---|---|\n| A | b |\n| C | d |\n\n"
                  "## 4. Rejected\n\n| measure | verdict |\n|---|---|\n| x | y |\n| z | w |\n\n"
                  "## 5. other\n")
        write_raw(os.path.join(tmp, "ERRATA.md"),
                  "stale cell |# ERRATA\n\n"
                  "Standing: the ten controls run.\n\n"
                  "Result: 10 of 11 controls green. Six controls proven, 5 skipped.\n\n"
                  "### 2026-09-27 — a dated entry\n\n"
                  "- **observed:** the ten controls ran then.\n")
        write_raw(os.path.join(tmp, "GATE_FREEZE.md"),
                  "## Every freeze so far, in one line each\n\n"
                  "| version | date | what changed |\n|---|---|---|\n"
                  "| Freeze 1 | 2026-09-27 | the ten controls pass |\n\n"
                  "## Manifest\n\n"
                  "- `PRINTERS_COPY.md` — 25 rejected measures, 6 confirmed\n"
                  "- `ERRATA.md` — 49 entries\n\n"
                  "Suite status at freeze: all ten controls pass (exit 0)\n\n"
                  "## Freeze 2 — 2026-09-27\n")
        write_raw(os.path.join(tmp, "KNOWN_FINDINGS.md"),
                  "## Added 2026-09-28 — dated\n\n"
                  "2. exists in 2 of 9 live projects.\n")
        book = os.path.join(tmp, "test-books", "ghost")
        os.makedirs(os.path.join(book, "manuscript", "chapters"))
        os.makedirs(os.path.join(book, "tools"))
        write_raw(os.path.join(book, "manuscript", "chapters", "chapter-01.md"),
                  "word " * 300)
        write_raw(os.path.join(book, "PROJECT_STATE.yaml"),
                  'status: "complete"\nnotes: "STILL NOT DRAFTED, nothing exists."\n')
        write_raw(os.path.join(book, "tools", "check-uniformity.py"), "stale copy\n")
        empty = os.path.join(tmp, "test-books", "hollow")
        os.makedirs(os.path.join(empty, "manuscript", "chapters"))
        write_raw(os.path.join(empty, "PROJECT_STATE.yaml"),
                  'status: "complete"\nnotes: "STILL NOT DRAFTED."\n')
        os.makedirs(os.path.join(book, "tools", "__pycache__"))
        write_raw(os.path.join(book, "tools", "__pycache__", "x.pyc"), "bytecode")

        bf = book_findings(tmp)
        gaining = sorted({f.path.split("/")[1] for f in bf
                          if f.path.startswith("test-books/")
                          and f.action in ("repair", "quarantine", "delete")})
        m = measure(tmp, gaining)
        ok(m["controls"] == 2, "measure: control count read from the suite")
        ok(m["errata_entries"] == 1, "measure: ERRATA entry count")
        ok((m["rejected"], m["confirmed"]) == (2, 2), "measure: registry rows")

        findings = record_findings(tmp, m) + bf
        kinds = {(f.kind, f.action) for f in findings}

        ok(("fragment", "repair") in kinds, "detect: glued heading fragment")
        ok(("recount", "repair") in kinds, "detect: stale standing count")
        ok(("status-prose", "repair") in kinds, "detect: stale status prose")
        ok(("copy", "quarantine") in kinds, "detect: book-carried instrument copy")
        ok(("cache", "delete") in kinds, "detect: bytecode cache")

        dated_edited = any(
            f.action == "repair" and f.path == "ERRATA.md" and f.line_no == 9
            for f in findings
        )
        ok(not dated_edited, "boundary: a dated entry is never rewritten")
        temporal_kept = any(
            f.action == "review" and f.path == "GATE_FREEZE.md"
            and "at freeze" in f.old for f in findings
        )
        ok(temporal_kept, "boundary: past-framed claim is REVIEW, not rewritten")
        hollow_review = any(
            f.action == "review" and "hollow" in f.path for f in findings
        )
        ok(hollow_review, "boundary: complete-status over empty manuscript is REVIEW")
        kf_repaired = any(
            f.action == "repair" and f.path == "KNOWN_FINDINGS.md" for f in findings
        )
        ok(kf_repaired, "policy: a present-tense stale claim is repaired even under "
           "a dated heading (old wording goes to the log)")
        subset_safe = not any(
            f.action == "repair" and "10 of 11" in f.old for f in findings
        )
        ok(subset_safe, "boundary: run records (\"10 of 11 controls green\") are "
           "never recounted as suite size")

        errors, written = apply_findings(tmp, findings)
        ok(not errors, "apply: no write errors")

        errata = read_raw(os.path.join(tmp, "ERRATA.md"))
        ok(errata.splitlines()[0] == "# ERRATA", "apply: heading restored")
        ok("the ten controls run" not in errata.split("## 2026")[0].replace(
            "the two controls run", ""), "apply: standing count recounted")
        ok("the two controls run" in errata, "apply: recounted to the live value")
        ok("the ten controls ran then" in errata, "apply: dated history untouched")

        gf = read_raw(os.path.join(tmp, "GATE_FREEZE.md"))
        ok("`PRINTERS_COPY.md` — 25" not in gf and "2 rejected measures, 2 confirmed" in gf,
           "apply: GATE_FREEZE counts recounted")
        ok(f"({date.today().isoformat()})" in gf, "apply: GATE_FREEZE history note added")

        state = read_raw(os.path.join(book, "PROJECT_STATE.yaml"))
        ok("STILL NOT DRAFTED" not in state and "pruned" in state,
           "apply: stale status sentence pruned")
        ok(read_raw(os.path.join(empty, "PROJECT_STATE.yaml")).count("STILL NOT DRAFTED") == 1,
           "apply: REVIEW-only book untouched")
        ok(not os.path.exists(os.path.join(book, "tools", "check-uniformity.py")),
           "apply: instrument copy moved out of the book")
        ok(os.path.exists(os.path.join(book, "_archive", "tools", "check-uniformity.py")),
           "apply: quarantined under _archive/, not deleted")
        ok(os.path.isfile(os.path.join(book, "_archive", "README.md")),
           "apply: _archive index entry written (protocol §7)")
        ok(not os.path.isdir(os.path.join(book, "tools", "__pycache__")),
           "apply: cache removed")

        root_log = os.path.join(tmp, "maintenance", "PRUNING_LOG.md")
        book_log = os.path.join(book, "maintenance", "PRUNING_LOG.md")
        ok(os.path.isfile(root_log) and "old wording" in read_raw(root_log),
           "log: root pruning log carries the old wording verbatim")
        ok(os.path.isfile(book_log), "log: book pruning log written")
        ok(len(written) == 2, "log: one log per scope, not one per finding")

        # idempotence: a second pass finds nothing repairable
        bf2 = book_findings(tmp)
        gaining2 = sorted({f.path.split("/")[1] for f in bf2
                           if f.path.startswith("test-books/")
                           and f.action in ("repair", "quarantine", "delete")})
        again = record_findings(tmp, measure(tmp, gaining2)) + bf2
        ok(not [f for f in again if f.action in ("repair", "quarantine", "delete")],
           "idempotent: second pass repairs nothing")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [label for good, label in checks if not good]
    for good, label in checks:
        print(("  ok    " if good else "  FAIL  ") + label)
    print("-" * 67)
    if failed:
        print(f"SELF-TEST FAILURE — {len(failed)} of {len(checks)} assertions failed.")
        return 1
    print(f"SELF-TEST PASS — {len(checks)} assertions, including every boundary "
          f"(dated history, past framing, REVIEW-only states).")
    return 0


# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    mode = "check"
    root = None
    i = 0
    while i < len(args):
        a = args[i]
        if a in ("--check", "--apply", "--self-test"):
            mode = a[2:]
        elif a == "--root" and i + 1 < len(args):
            root = args[i + 1]
            i += 1
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            print(f"prune-stale: unknown argument {a}")
            return 2
        i += 1

    if root is None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isdir(root):
        print(f"prune-stale: no such root: {root}")
        return 2

    if mode == "self-test":
        return self_test()

    bf = book_findings(root)
    # The "N of M live projects" claim counts pruning logs, and applying a repair
    # creates one — so measure as of the END of the run, or the tool would repair
    # the claim to a number stale before it lands and never reach idempotence.
    gaining = sorted({f.path.split("/")[1] for f in bf
                      if f.path.startswith("test-books/")
                      and f.action in ("repair", "quarantine", "delete")})
    m = measure(root, gaining)
    findings = record_findings(root, m) + bf

    if mode == "apply":
        actionable = [f for f in findings if f.action in ("repair", "quarantine", "delete")]
        errors, written = apply_findings(root, findings)
        report(root, m, findings, "apply")
        for path, n in written:
            print(f"  pruning log: {os.path.relpath(path, root).replace(os.sep, '/')} "
                  f"(+{n} entr{'y' if n == 1 else 'ies'})")
        for e in errors:
            print(f"  ERROR {safe(e)}")
        if errors:
            print("APPLY INCOMPLETE — the errors above name what could not be written.")
            return 1
        if actionable:
            print(f"PRUNED — {len(actionable)} item(s) corrected, old wording preserved "
                  f"in the pruning log(s). REVIEW items above await a ruling.")
        else:
            print("NOTHING TO PRUNE — records match the live program.")
        return 0

    report(root, m, findings, "check")
    repairable = [f for f in findings if f.action in ("repair", "quarantine", "delete")]
    if repairable:
        print(f"STALE RECORDS — {len(repairable)} repairable item(s). "
              f"Run: python tools/prune-stale.py --apply")
        return 1
    if findings:
        print("NOTHING REPAIRABLE — REVIEW items above need a ruling, never an auto-fix.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
