the ten controls (Freeze 10; was `e940b825763c2281` at Freeze 9; Freeze 12 - name only) |#!/usr/bin/env python3
"""chapter-rates.py - derive density caps from CHAPTERS, not documents.

The caps in `deslop-check.sh` were derived from the worst rate in a whole published
*document* and are then enforced against a *chapter*. Those are different units, and
the difference is not academic: a fixed slice of 2,150 words drawn from a novel that
averages 3,557 gives a materially higher rate than the novel's own average, because
a short stretch of prose is more likely to be a dense one.

Measured on 102 published chapters (`chunk-pd-corpus.py`, stride-sampled from the
140-novel corpus), **five rules fail real published prose** - `D2` on 18.6% of
chapters, `D1` on 14.7%. A gate that fails a fifth of the human canon is not a gate
against machine prose; it is a gate against prose.

This recomputes each cap from the worst chapter actually measured, which is the unit
the scanner gates on, and prints what the corrected value would be. It changes
nothing - the DENSITY table is edited by hand, deliberately, because moving a cap is
a decision someone has to make on the record.

usage:  python chapter-rates.py <scan-output> [--apply-ratio R]
"""

import collections
import os
import re
import sys

# 1.5x the worst published document, from deslop-check.sh's DENSITY header.
TARGET = 1.5

ROW = re.compile(r"^\s*(?:FAIL|warn|ok)\s+([A-Z]\d+[a-z]?)\s+(.+?)\s+([\d.]+)\s+per 1k")

# The scanner's header is `== <path>  (<n> words)`. The PATH CAN CONTAIN SPACES - this
# project's books are called "Hollow Bridge" - so `line.split()[1]` returns
# "../Hollow" and every lookup keyed on it silently matches nothing. A parser that
# quietly finds no data in a file it actually read is worse than one that raises, because
# it still prints a confident report. The path is taken with a regex terminated by the
# word count, which also guarantees the match consumed the whole header.
HEADER = re.compile(r"^==\s+(.*?)\s+\(\d+\s+words\)\s*$")


def header_path(line):
    """The path in a scanner header line, or None if this is not a header."""
    m = HEADER.match(line)
    return m.group(1) if m else None


def read_clean(path):
    """Read a scan output and report how many NUL bytes it contained.

    Returns (lines, nul_count). The count is the caller's to act on: a NUL byte in a
    text report means more than one process has been writing to it, and every number
    derived from such a file is a fiction that looks like a measurement.
    """
    raw = open(path, "rb").read()
    nul = raw.count(b"\x00")
    text = raw.decode("utf-8", "replace")
    text = "".join(ch if ch >= "\x20" or ch == "\n" else " " for ch in text)
    return text.splitlines(), nul


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    path = sys.argv[1]

    # Cap currently in force, read from deslop-check.sh's DENSITY table so the two
    # cannot disagree. Read it from the SCANNER, not from this file - parsing the
    # table out of the tool that is meant to analyse it finds nothing at all, and
    # prints an empty report that reads exactly like a clean one.
    here = os.path.dirname(os.path.abspath(__file__))
    scanner = os.path.join(os.path.dirname(here), "deslop-check.sh")
    src = open(scanner, encoding="utf-8").read()
    caps = {}
    for m in re.finditer(
            r"'([A-Z]\d+[a-z]?)\|[^|]*\|(\d+)\|(\d+)\|[^#]*#", src):
        caps[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    if not caps:
        print("could not read the DENSITY table out of deslop-check.sh; refusing to")
        print("report, because an empty report reads exactly like a clean one")
        return 1

    lines, nul = read_clean(path)
    chapters = [l for l in lines if header_path(l)]
    n = len(chapters)
    if not n:
        print("no chapters in the scan output; a report that read nothing proves nothing")
        return 1

    # Every header must parse. If any do not, the scan output format has changed and the
    # rates below would be keyed on a truncated path - which is how a book called
    # "Hollow Bridge" silently vanished from a report that still printed a verdict.
    unparsed = sum(1 for l in lines if l.startswith("== ") and not header_path(l))
    if unparsed:
        print(f"REFUSING: {unparsed} of {n} header lines did not parse. The scanner's")
        print("output format has changed and this tool would mis-key every chapter.")
        return 1

    # Integrity check, and it is not optional. A scan abandoned on a tool timeout can
    # leave its `awk` stage alive, still writing into the same output file as a later
    # scan; the result is a sparse file whose header count exceeds the number of
    # chapters scanned, and it still prints a plausible per-rule table. The only thing
    # that caught it was counting NUL bytes.
    if nul:
        print(f"REFUSING: {path} holds {nul} NUL bytes.")
        print("That is a sparse file - two writers at independent offsets, i.e. a scan")
        print("that was killed and never stopped writing. Its per-rule table is fiction.")
        print("Kill the strays, delete the file, re-run to a fresh path.")
        return 1
    dupes = [f for f, c in collections.Counter(
        header_path(l) for l in chapters if header_path(l)).items() if c > 1]
    if dupes:
        print(f"REFUSING: {len(dupes)} chapter(s) appear twice in {path} "
              f"(e.g. {dupes[0]}).")
        print("A second writer reached this file, or a scan was concatenated.")
        return 1

    worst = {}          # rule -> (rate, filename, name)
    failures = collections.defaultdict(set)

    cur = None
    for line in lines:
        path = header_path(line)
        if path is not None:
            cur = path.split("/")[-1]
            continue
        m = ROW.match(line)
        if not m:
            continue
        rule, name, rate = m.group(1), m.group(2), float(m.group(3))
        if rule not in worst or rate > worst[rule][0]:
            worst[rule] = (rate, cur, name)
        if line.strip().startswith("FAIL"):
            failures[rule].add(cur)

    print("=" * 78)
    print(f"## chapter-rates   {n} published chapters at ~2,150 words")
    print("=" * 78)
    print()
    print("A cap fails when n * allow_w > allow_n * words. So what has to clear the")
    print("cap is the worst CHAPTER, and the cap was derived from the worst DOCUMENT.")
    print()
    print("  rule   cap      worst CHAPTER   current cap allows   derived   verdict")
    print("  " + "-" * 74)
    offend = []
    for rule in sorted(worst, key=lambda r: -len(failures.get(r, ()))):
        rate, fname, name = worst[rule]
        cap = caps.get(rule)
        if not cap:
            continue
        allow_n, allow_w = cap
        derived = rate * TARGET
        # The smallest expressible cap at or above `derived`, keeping the table's
        # denominator where possible so the change stays a one-number edit.
        n_needed = -(-derived * allow_w // 1000)          # ceil
        n_needed = max(1, int(n_needed))
        nf = len(failures.get(rule, ()))
        pct = 100.0 * nf / n
        verdict = "FAILS PUBLISHED PROSE" if nf else "ok"
        if nf:
            offend.append((rule, name, rate, allow_n, allow_w, n_needed, nf, pct, fname))
        mark = "*" if nf else " "
        print(f" {mark}{rule:<6} {allow_n}/{allow_w:<8} {rate:>6.2f}/1k      "
              f"{rate * allow_w / 1000:>5.1f} hits       {derived:>5.2f}      {verdict}")

    if not offend:
        print("\nNo rule fails published prose.")
        return 0

    print()
    print("=" * 78)
    print(f"{len(offend)} rule(s) fail real published prose. In priority order:")
    print()
    for rule, name, rate, allow_n, allow_w, n_needed, nf, pct, fname in offend:
        print(f"  {rule}  {name}")
        print(f"      cap now      {allow_n}/{allow_w} words = {1000*allow_n/allow_w:.2f}/1k")
        print(f"      worst chapter {rate:.2f}/1k  ({fname})")
        print(f"      x{TARGET:.1f} derives  {rate*TARGET:.2f}/1k  ->  "
              f"{n_needed}/{allow_w} words")
        print(f"      fails {nf} of {n} chapters ({pct:.1f}%)")
        print()
    print("Nothing here has been changed. These are the numbers a cap edit needs, and")
    print("each one is a decision about published prose - see PRINTERS_COPY.md section 7.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
