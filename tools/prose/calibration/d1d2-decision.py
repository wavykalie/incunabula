the ten controls (Freeze 10; was `e940b825763c2281` at Freeze 9; Freeze 12 - name only) |#!/usr/bin/env python3
"""d1d2-decision.py - can a D1/D2 cap separate AI prose from published prose at all?

§12 established that `D1`, `D2` and `A25` fail 14.7%, 18.6% and 1.0% of published
chapters. The open question was whether to RAISE the caps (1.5x the worst published
chapter: D1 51/1k, D2 13/1k) or DEMOTE the rows to warn.

That question has an answer that does not require a preference between the two, and it is
the only question that matters: **does the AI control sit above the published chapter
distribution?** If it does, a cap exists between them and should be raised to it. If it
does not, no cap can do the job the row exists for, and raising it to the published
maximum only buys a gate that passes everything.

So this measures both distributions from the same code path, per chapter, and reports the
overlap directly.

usage:  python d1d2-decision.py <published-scan> --control <book-dir> [<book-dir> ...]
"""

import os
import re
import statistics as st
import sys

ROW = re.compile(r"^\s*(?:FAIL|warn|ok|--)\s+(A\d+[a-z]?|D[123]|P\d+)\s+(.+?)\s+([\d.]+)\s+per 1k")
# The header is `== <path>  (<n> words)`. The path can CONTAIN SPACES - this project's
# books are called "Hollow Bridge" - so `line.split()[1]` yields "../Hollow" and
# every downstream lookup silently finds nothing. A parser that quietly returns an empty
# result on a book it actually read is worse than one that crashes, so the path is taken
# with a regex and the word count is required to terminate it.
HEADER = re.compile(r"^==\s+(.*?)\s+\(\d+\s+words\)\s*$")


def read_clean(path):
    raw = open(path, "rb").read()
    nul = raw.count(b"\x00")
    text = raw.decode("utf-8", "replace")
    text = "".join(c if c >= "\x20" or c == "\n" else " " for c in text)
    return text.splitlines(), nul


CHAPTER = re.compile(r"^chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)


def control_rates(book_dirs, rule):
    """Run the scanner on each control book's CHAPTERS and pull this rule's rate.

    The scanner accepts a book directory and will cheerfully scan every .md in it -
    ASSUMPTIONS.md, FINISHED.md, foundation.md and the rest - none of which are prose.
    Those files carry their own rates and they are not chapters, so the control has to
    be pointed at the chapter directory explicitly or the comparison is meaningless.
    Passing the book path and taking the first result gave ONE "chapter" per book and a
    confident verdict built on it.
    """
    import subprocess
    scanner = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "deslop-check.sh")
    out = {}
    for d in book_dirs:
        target = d
        for cand in (os.path.join(d, "manuscript", "chapters"),
                     os.path.join(d, "chapters"), d):
            if os.path.isdir(cand) and any(
                    CHAPTER.match(f) for f in os.listdir(cand)):
                target = cand
                break
        proc = subprocess.run(["bash", scanner, target], capture_output=True, text=True,
                              errors="replace")
        cur = None
        for line in proc.stdout.splitlines():
            h = HEADER.match(line)
            if h:
                name = h.group(1).split("/")[-1]
                cur = name if CHAPTER.match(name) else None
                continue
            if cur is None:
                continue
            m = ROW.match(line)
            if m and m.group(1) == rule:
                out[cur] = float(m.group(3))
    return out


def main():
    if len(sys.argv) < 3 or "--control" not in sys.argv:
        print(__doc__.strip())
        return 2
    scan = sys.argv[1]
    i = sys.argv.index("--control")
    books = sys.argv[i + 1:]
    controls = [b for b in books if not b.endswith(".txt")]

    lines, nul = read_clean(scan)
    if nul:
        print(f"REFUSING: {scan} holds {nul} NUL bytes (two writers, sparse file).")
        return 1
    pub = {}
    for line in lines:
        m = ROW.match(line)
        if m:
            pub.setdefault(m.group(1), []).append(float(m.group(3)))

    # The cap each row is currently held to, per 1k. Read from the scanner rather than
    # hardcoded here, so a cap edit cannot leave this tool comparing against a number the
    # gate no longer uses.
    caps = {}
    scanner_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "deslop-check.sh"), encoding="utf-8").read()
    for m in re.finditer(r"'([A-Z]\d+[a-z]?)\|([^|]+)\|(\d+)\|(\d+)\|", scanner_src):
        caps[m.group(1)] = 1000.0 * int(m.group(3)) / int(m.group(4))

    # Which rows the scanner can no longer fail, read from the REPORT block.
    report_block = scanner_src.split("REPORT=(", 1)
    report_only = set()
    if len(report_block) == 2:
        for m in re.finditer(r"'([A-Z]\d+[a-z]?)\|", report_block[1].split("\n)", 1)[0]):
            report_only.add(m.group(1))

    for rule in ("A25", "A24", "A23", "A15b", "D1", "D2", "D3"):
        if rule not in caps or rule not in pub:
            continue
        pv = sorted(pub[rule])
        n = len(pv)
        print("=" * 78)
        print(f"## {rule}   published chapters n={n}, control books n={len(controls)}")
        print("=" * 78)
        print()
        print(f"  published chapters   p50 {st.median(pv):6.2f}  p95 {pv[int(.95*(n-1))]:6.2f}"
              f"  p99 {pv[int(.99*(n-1))]:6.2f}  max {pv[-1]:6.2f}   per 1k")
        cap = caps[rule]
        nfail = sum(1 for v in pv if v > cap)
        # Rows the scanner can no longer fail are marked, so a report of "0% fail" is not
        # read as "the cap is comfortably clear" when in fact the row cannot fail at all.
        tier = " (REPORT-ONLY, cannot fail)" if rule in report_only else ""
        print(f"  current cap          {cap:6.2f}{tier}"
              f"  ->  {100*nfail/n:5.1f}% of published chapters fail")

        ctrl = {}
        for d in controls:
            r = control_rates([d], rule)
            if r:
                ctrl[os.path.basename(d.rstrip('/'))] = sorted(r.values())
        if not ctrl:
            print("  (no control measured)")
            print()
            continue
        for name, cv in sorted(ctrl.items()):
            above = sum(1 for v in cv if v > pv[-1])
            print(f"  {name:<24} p50 {st.median(cv):6.2f}  max {max(cv):6.2f}"
                  f"    {above} of {len(cv)} chapters exceed the WORST published chapter")
        allc = [v for cv in ctrl.values() for v in cv]
        if allc:
            print(f"  control pooled        p50 {st.median(allc):6.2f}  max {max(allc):6.2f}")
        print()
        # The decision hinges on this comparison alone.
        if allc and max(allc) <= pv[-1]:
            print(f"  VERDICT: the control never exceeds the published maximum ({pv[-1]:.2f}/1k).")
            print("  No cap can separate them. Raising the cap to clear published prose")
            print("  would produce a row that passes every book, machine and human alike.")
        elif allc and st.median(allc) > pv[int(.95 * (n - 1))]:
            print("  VERDICT: the control sits above the 95th percentile of published")
            print("  chapters, so a cap exists between them and raising it preserves the row.")
        else:
            print("  VERDICT: the control overlaps the published distribution. A cap here")
            print("  would be choosing which human books to reject, not which books to catch.")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
