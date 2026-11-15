#!/usr/bin/env python3
"""check-diction.py - a book's own lexical register, enforced mechanically.

    usage:  python tools/prose/check-diction.py BOOK            (book root)
            python tools/prose/check-diction.py BOOK FILE [...]  (just these files)

    exit 0 = clean
    exit 1 = a banned word, or a required word below its floor
    exit 2 = no rules, or an empty rules file (an ungoverned book is NOT a pass)
    exit 3 = the book or its chapters directory is missing

WHY THIS EXISTS
check-world.py asks whether the prose contradicts the book's physics. It has no
opinion about the words. So a book could pass every gate in this repository while
reading like it was written in 1880, and one did: The Parts Still Warm, whose own
direction file called the city Victorian, whose WORLD_RULES.txt removed every
modern object from the street, and which therefore had no vocabulary left for the
street except the period's. Fourteen briefs in the same project said "Nothing
Victorian". Nothing measured the difference, so nothing noticed.

The failure has two halves and the second is the one the world gate could not see:
the rules SUBTRACTED (no van, no tyre, no fuel) and never ADDED. A world defined
only by what it forbids leaves the writer the oldest surviving noun. So this gate
has two row kinds, and the second kind is the point:

    X1|regex|why it is wrong here                    a hit FAILS
    R1|regex|floor_per_10k|why it must be present    a rate BELOW the floor FAILS

The lexicon lives in the BOOK, not in this file: <book>/DICTION_RULES.txt. `#`
starts a comment line; blank lines are ignored. Regex is Python `re`, searched
case-insensitively. A book with no rules file exits 2, the same stance check-world
takes: not-run is never a pass.

WHAT THIS CANNOT DO, AND WHY IT STILL GATES
The rules are written by someone, so the gate catches the words that were thought
of and not the next one. It holds no corpus and cannot say a book IS modern; it can
only say the book is not still saying the words its own note names, and that the
vocabulary it needs has not vanished. Each required floor is a third of the rate
the repaired book measured, which is one book's evidence - enough to catch a drift
to zero, not enough to call a threshold. That is written in the rules file, where
the next person will read it.

A hit is a question, not a verdict. It prints the line and never edits anything.
"""

import os
import re
import sys


def die(msg, code):
    print(msg)
    sys.exit(code)


def load_rules(book):
    path = os.path.join(book, "DICTION_RULES.txt")
    if not os.path.isfile(path):
        die("no DICTION_RULES.txt in %s - this book's lexical register is "
            "ungoverned, which is not a pass" % book, 2)
    bans, needs = [], []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            # Split on the FIRST pipe and the LAST pipe only. Every real regex
            # here uses alternation, so a naive split cuts a correct pattern at
            # its first "|" and then reports a syntax error in it.
            if line.count("|") < 2:
                die("%s:%d: expected ID|regex|why (or ID|regex|floor|why), got %r"
                    % (path, n, line), 2)
            rid, rest = line.split("|", 1)
            rid = rid.strip()
            try:
                if rid.upper().startswith("R"):
                    # R1|regex|floor|why -> the floor and the why are the last
                    # two fields; everything between is the pattern.
                    pattern, tail = rest.rsplit("|", 1)
                    pattern, floor = pattern.rsplit("|", 1)
                    why = tail.strip()
                    needs.append((rid, re.compile(pattern.strip(), re.IGNORECASE),
                                  float(floor.strip()), why))
                else:
                    pattern, why = rest.rsplit("|", 1)
                    bans.append((rid, re.compile(pattern.strip(), re.IGNORECASE),
                                 why.strip()))
            except (re.error, ValueError) as exc:
                die("%s:%d: bad rule %r (%s)" % (path, n, line, exc), 2)
    if not bans and not needs:
        die("%s has no rules - an empty lexicon cannot pass a book" % path, 2)
    return path, bans, needs


def targets(book, files):
    if files:
        return files
    chapters = os.path.join(book, "manuscript", "chapters")
    if not os.path.isdir(chapters):
        die("no manuscript/chapters under %s" % book, 3)
    found = sorted(
        os.path.join(chapters, f)
        for f in os.listdir(chapters)
        if f.endswith(".md")
    )
    if not found:
        die("no .md chapters under %s - a scan of nothing is a failure, not a pass"
            % chapters, 3)
    return found


def main(argv):
    if len(argv) < 2:
        die(__doc__.strip(), 3)
    book = argv[1]
    if not os.path.isdir(book):
        die("not a book directory: %s" % book, 3)
    rules_path, bans, needs = load_rules(book)
    files = targets(book, argv[2:])

    hits = 0
    per_rule = {}
    words = 0
    present = {rid: 0 for rid, _, _, _ in needs}

    for path in files:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, 1):
                words += len(line.split())
                for rid, rx, why in bans:
                    m = rx.search(line)
                    if not m:
                        continue
                    hits += 1
                    per_rule[rid] = per_rule.get(rid, 0) + 1
                    snippet = line.strip()
                    if len(snippet) > 120:
                        start = max(0, m.start() - 45)
                        snippet = "..." + snippet[start:start + 120] + "..."
                    print("%s:%d: %s  [%s]  %s"
                          % (path, lineno, m.group(0), rid, why))
                    print("        %s" % snippet)
                for rid, rx, _, _ in needs:
                    present[rid] += len(rx.findall(line))

    # A rate on nothing is not a pass. The floors are per 10,000 words.
    if words == 0:
        die("no words in %d file(s) - a scan of nothing is a failure, not a pass"
            % len(files), 3)
    scale = 10000.0 / words

    print("")
    for rid, rx, floor, why in needs:
        rate = present[rid] * scale
        state = "ok" if rate >= floor else "BELOW FLOOR"
        print("%s %-10.1f per 10k  (floor %.1f)  %s"
              % (rid, rate, floor, state))
        print("     %s" % why)
    if needs:
        print("")

    print("scanned %d file(s), %d words, against %d ban(s) and %d requirement(s): %s"
          % (len(files), words, len(bans), len(needs), rules_path))
    if hits:
        print("hits by rule: " + ", ".join("%s x%d" % (k, per_rule[k]) for k in sorted(per_rule)))
    short = [rid for rid, _, floor, _ in needs if present[rid] * scale < floor]
    if hits or short:
        if short:
            print("below floor: " + ", ".join(short))
        print("RESULT: FAIL - the page is not written in the register this book declared.")
        return 1
    print("RESULT: PASS - no word on these pages dates the book, and the vocabulary")
    print("        it needs to keep is still on the page.")
    print("        Mechanical only: the rules cover the words someone thought of.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
