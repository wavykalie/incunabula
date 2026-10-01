#!/usr/bin/env python3
"""arc-short-book.py - does A1 fail a real short book made of published prose?

`arc-units.py` showed that 12.7% of individual 4,000-word windows in published novels
sit below A1's floor, while 0 of 40 novel *means* do. The floor is derived on the mean.
This asks the question that matters operationally: take a published novel, cut it down
to the length of a short book, and run the actual gate on it.

Nothing here simulates the metric. It writes real prose to a real chapter directory and
executes `check-arc.py` on it, so the number that comes back is the number an editor
would see.

usage:  python arc-short-book.py <corpus-dir> [--books N] [--lengths 2000,4000,8000,16000]
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROSE = os.path.dirname(HERE)
GATE = os.path.join(PROSE, "check-arc.py")

DEFAULT_LENGTHS = (2000, 4000, 8000, 16000, 32000)


def slice_words(text, want):
    """Take the first `want` words of a novel, cutting on a sentence boundary."""
    out, n = [], 0
    for piece in re.split(r"(?<=[.!?])\s+", text):
        n += len(piece.split())
        out.append(piece)
        if n >= want:
            break
    return " ".join(out)


def run_gate(directory):
    proc = subprocess.run([sys.executable, GATE, directory],
                          capture_output=True, text=True, errors="replace")
    m = re.search(r"reversals per bin\s+([\d.]+)\s+\(mean of (\d+) windows?", proc.stdout)
    if m:
        return float(m.group(1)), int(m.group(2))
    if "unmeasured" in proc.stdout.lower():
        return None, 0
    return None, 0


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    corpus = sys.argv[1]
    nbooks = 12
    if "--books" in sys.argv:
        nbooks = int(sys.argv[sys.argv.index("--books") + 1])
    lengths = DEFAULT_LENGTHS
    if "--lengths" in sys.argv:
        lengths = tuple(int(x) for x in
                        sys.argv[sys.argv.index("--lengths") + 1].split(","))

    files = sorted(f for f in os.listdir(corpus) if f.lower().endswith(".txt"))
    picks, total = [], 0
    for name in files:
        with open(os.path.join(corpus, name), encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        if len(text.split()) < max(lengths) + 500:
            continue
        picks.append((name, text))
        if len(picks) >= nbooks:
            break

    if not picks:
        print("no source long enough; a report that read nothing proves nothing")
        return 1

    print("=" * 78)
    print(f"## arc-short-book   {len(picks)} published novels, truncated to book lengths")
    print("=" * 78)
    print()
    print("Real published prose, real chapter files, the real gate. Only the LENGTH")
    print("changes. A1 fails under 0.45.")
    print()
    print("  book length    books   windows   median A1   FAILING the floor")
    verdicts = {}
    for length in lengths:
        rows = []
        tmp = tempfile.mkdtemp(prefix="arcbook")
        try:
            for name, text in picks:
                d = os.path.join(tmp, name[:-4])
                os.makedirs(d, exist_ok=True)
                # Split into chapters the way a short book would be, so MIN_CHAPTERS
                # is satisfied and the gate actually runs rather than reporting
                # unmeasured - which is itself a finding worth seeing separately.
                body = slice_words(text, length)
                words = body.split()
                nch = max(4, min(12, len(words) // 2000 + 1))
                per = len(words) // nch
                for i in range(nch):
                    chunk = " ".join(words[i * per:(i + 1) * per])
                    if chunk.strip():
                        with open(os.path.join(d, f"chapter-{i+1:02d}.md"),
                                  "w", encoding="utf-8") as fh:
                            fh.write(chunk)
                score, wins = run_gate(d)
                if score is not None:
                    rows.append((name, score, wins))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        if not rows:
            print(f"  {length:>10}  {'-':>6}   {'unmeasured':>8}    "
                  f"the gate declined every one")
            verdicts[length] = None
            continue
        scores = sorted(r[1] for r in rows)
        fails = [r for r in rows if r[1] < 0.45]
        med = scores[len(scores) // 2]
        wins = sorted(r[2] for r in rows)[len(rows) // 2]
        pct = 100.0 * len(fails) / len(rows)
        flag = "*" if fails else " "
        print(f" {flag}{length:>9}  {len(rows):>6}   {wins:>7}   {med:>9.3f}   "
              f"{len(fails):>3} of {len(rows)} ({pct:.0f}%)")
        verdicts[length] = (len(fails), len(rows), med)

    print()
    print("=" * 78)
    bad = [(k, v) for k, v in verdicts.items() if v and v[0]]
    if bad:
        print("A1 fails PUBLISHED PROSE at these book lengths:")
        for k, (f, n, med) in bad:
            print(f"    {k:>6} words  {f}/{n} books below 0.45  (median {med:.3f})")
        print()
        print("A1's floor is derived from the mean over ~15 windows of a full novel.")
        print("A short book is one or two windows, and a single window from published")
        print("prose falls below the floor 12.7% of the time.")
    else:
        print("No book length produced a false failure.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
