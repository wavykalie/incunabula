#!/usr/bin/env python3
"""check-waivers.py — a waiver ledger that counts, so the recurring waiver is code.

A uniformity failure may be "fixed or waived in writing" (skills/composing, the
review gate), and the length floor may be waived per chapter with a recorded
reason (the maintenance gate). The writing used to live in whatever per-chapter
report happened to hold it, and nothing cross-read the reports: the documented
failure mode - "the same waiver recurring across books is itself the pattern"
(check-uniformity.py) - was caught only if a human re-read every report. A
repeated waiver stops being a local decision and becomes a property of the
pipeline, and that transition is exactly what a machine can see and a reader
cannot.

So the ledger is one file per book - maintenance/WAIVERS.md - written by the
runner's declaration command (tools/run-phases.sh BOOK --waive RULE --chapter N
--reason TEXT), and this is its auditor.

THE ENTRY FORMAT, exactly:

    ## W-001 — 2026-10-15 — chapter 4 — U4
    - reason: the novella is seven matched movements; evenness is the design.

Five things per entry, and no others are optional: an id (W-NNN), a date, a
chapter (a number, or `book` for a book-scoped row such as U1-U6), a rule (the
row id - U4, L2, floor - or the gate id), and a reason. An entry without a
reason is a skip wearing a waiver's clothes, and this tool refuses it.

WHAT IT CHECKS
  The same rule waived in MORE THAN N consecutive chapters fails, N=3 by
  default (overridable with --max-consecutive, and printed in every report so
  the number is never folklore). At N=3 the fourth consecutive chapter is the
  fail: three chapters are a run, four are the pattern. This is the mechanical
  short-term catch; press-ledger's errata path remains the long-term one - a
  rule waived by a second BOOK is an ERRATA.md entry ("Errata, not waivers"),
  and this per-book ledger cannot see across books. It says so in every run.

  Book-scoped entries (`chapter: book`) do not take part in consecutive runs -
  there is nothing to be consecutive across - and are listed as declared.

THE RESIDUAL GAP, stated because not-run is never a pass: a waiver written only
into a per-chapter report is invisible here. This tool audits the ledger, not
the reports. The runner's --waive command is the declaration path, and the
runner creates the ledger empty before this row runs, so a book that has never
waived anything reports the healthy state rather than NOT RUN by accident.

usage:  python tools/prose/check-waivers.py BOOK_ROOT [--max-consecutive N]
exit 0 = no recurring pattern (a ledger with zero entries is the healthy state)
exit 1 = the same rule is waived in more than N consecutive chapters - the
         waiver is the pattern; halt for human review
exit 2 = no ledger to audit (NOT RUN, never a pass)
exit 3 = the ledger exists but an entry is malformed (refusal; a half-parsed
         ledger is the one thing worse than none)
"""

import os
import re
import sys

DEFAULT_MAX_CONSECUTIVE = 3

ENTRY = re.compile(
    r"^##\s+(W-\d+)\s*[-\u2013\u2014]\s*(\d{4}-\d{2}-\d{2})\s*[-\u2013\u2014]\s*"
    r"chapter\s+([A-Za-z0-9_.-]+)\s*[-\u2013\u2014]\s*(\S+)\s*$",
    re.M | re.I,
)
REASON = re.compile(r"^-\s+reason:\s+(.*\S)\s*$", re.M | re.I)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def split_entries(text):
    """[(id, date, chapter, rule, body)] for every entry heading, in file order."""
    marks = list(ENTRY.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group(1), m.group(2), m.group(3), m.group(4), text[m.end():end]))
    return out


def malformed_headings(text):
    """`## W-...` headings that do not parse into the required five things."""
    bad = []
    for line in text.splitlines():
        if line.startswith("##") and re.match(r"^##\s*W-\d+", line, re.I):
            if not ENTRY.match(line):
                bad.append(line.strip())
    return bad


def longest_runs(chapters):
    """Maximal runs of consecutive chapter numbers; [(start, end, length)]."""
    runs = []
    ordered = sorted(set(chapters))
    for n in ordered:
        if runs and n == runs[-1][1] + 1:
            runs[-1][1] = n
            runs[-1][2] += 1
        else:
            runs.append([n, n, 1])
    return [(a, b, ln) for a, b, ln in runs]


def main():
    args = sys.argv[1:]
    max_consecutive = DEFAULT_MAX_CONSECUTIVE
    roots = []
    i = 0
    while i < len(args):
        if args[i] == "--max-consecutive":
            if i + 1 >= len(args):
                print("check-waivers: --max-consecutive needs a number")
                return 3
            try:
                max_consecutive = int(args[i + 1])
            except ValueError:
                print("check-waivers: --max-consecutive needs a number, got %r" % args[i + 1])
                return 3
            i += 2
        else:
            roots.append(args[i])
            i += 1

    if not roots:
        print("check-waivers: usage: python tools/prose/check-waivers.py BOOK_ROOT "
              "[--max-consecutive N]")
        return 3

    total_failed = 0
    for root in roots:
        ledger = os.path.join(root, "maintenance", "WAIVERS.md")
        if not os.path.isfile(ledger):
            print("check-waivers: %s" % ledger)
            print("               NO LEDGER - nothing to audit. NOT RUN, never a pass.")
            print("               (A waiver written only into a per-chapter report is")
            print("               invisible to this check; declare waivers with")
            print("               'bash tools/run-phases.sh %s --waive RULE --chapter N "
                  "--reason TEXT'.)" % root)
            return 2
        text = read(ledger)

        bad = malformed_headings(text)
        if bad:
            print("check-waivers: %s holds a malformed entry heading:" % ledger)
            for line in bad:
                print("               %s" % line)
            print("               Required: ## W-NNN — date — chapter N — rule, with a "
                  "- reason: line.")
            print("               Refusing to half-read a ledger (exit 3).")
            return 3

        entries = split_entries(text)
        by_rule = {}
        declared = []
        for wid, date, chapter, rule, body in entries:
            tag = "%s (%s)" % (wid, date)
            if not DATE.match(date):
                print("check-waivers: %s: entry %s has an unparseable date" % (ledger, tag))
                return 3
            if not REASON.search(body):
                print("check-waivers: %s: entry %s (%s) has NO REASON." % (ledger, tag, rule))
                print("               A waiver without a reason is a skip wearing a "
                      "waiver's clothes. Refusing (exit 3).")
                return 3
            if chapter.lower() in ("book", "*"):
                declared.append((wid, date, rule, "book"))
                continue
            if not chapter.isdigit():
                print("check-waivers: %s: entry %s has a non-numeric chapter %r "
                      "(use a number, or 'book' for a book-scoped row)" % (ledger, tag, chapter))
                return 3
            by_rule.setdefault(rule, set()).add(int(chapter))
            declared.append((wid, date, rule, "chapter %s" % chapter))

        print("=" * 67)
        print("## waivers   %s   %d entr%s   cap: more than %d consecutive chapters fails"
              % (root, len(declared), "y" if len(declared) == 1 else "ies", max_consecutive))
        print("=" * 67)
        for wid, date, rule, scope in declared:
            print("   %-7s %-12s %-10s %s" % (wid, date, rule, scope))
        if not declared:
            print("   (ledger present, zero waivers - the healthy state)")

        failed_rules = []
        for rule in sorted(by_rule):
            runs = longest_runs(by_rule[rule])
            worst = max(runs, key=lambda r: r[2])
            chapters = ", ".join(str(c) for c in sorted(by_rule[rule]))
            print()
            print("   %-10s chapters %-24s longest run %d" % (rule, chapters, worst[2]))
            for a, b, ln in runs:
                if ln > max_consecutive:
                    print("          FAIL  chapters %d-%d are %d consecutive waivers - "
                          "the cap is %d" % (a, b, ln, max_consecutive))
                    print("                the waiver is the pattern. This is no longer a")
                    print("                local decision: halt for human review.")
                    print("                (The long-term catch is press-ledger's errata")
                    print("                path - a rule waived by a second book is an")
                    print("                ERRATA.md entry. This is the short-term one.)")
                    failed_rules.append(rule)
                elif ln == max_consecutive:
                    print("          run   chapters %d-%d (%d) - at the number press-ledger"
                          % (a, b, ln))
                    print("                names: the same justification three times is not")
                    print("                book-specific. One more chapter and this halts.")
        if declared:
            print()
            print("   gap: a waiver recorded only in a per-chapter report is invisible")
            print("        here. This tool audits the ledger, not the reports.")
        print()
        if failed_rules:
            print("WAIVER PATTERN - rule(s) %s exceed the consecutive cap. NOT CLEAR."
                  % ", ".join(failed_rules))
            total_failed += 1
        else:
            print("WAIVERS OK - no rule exceeds %d consecutive chapters." % max_consecutive)

    return 1 if total_failed else 0


if __name__ == "__main__":
    sys.exit(main())
