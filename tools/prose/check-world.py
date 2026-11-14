#!/usr/bin/env python3
"""check-world.py - a book's own physics, enforced mechanically.

    usage:  python tools/prose/check-world.py BOOK            (book root)
            python tools/prose/check-world.py BOOK FILE [...]  (just these files)

    exit 0 = clean
    exit 1 = at least one hit (printed with file:line)
    exit 2 = no rules, or an empty rules file (an ungoverned book is NOT a pass)
    exit 3 = the book or its chapters directory is missing

WHY THIS EXISTS
The slop gate checks how prose is written. It cannot check whether the prose
contradicts the world: a chapter can be perfectly clean and still put a truck in a
city whose streets carry nothing heavier than a barrow. That defect was found by
reading, twice, after the chapter was drafted and after a human sweep - so it is
exactly the class of error a person should stop being the only defence against.

The lexicon lives in the BOOK, not in this file: <book>/WORLD_RULES.txt, one rule
per line,

    ID|regex|why it is banned here

`#` starts a comment line; blank lines are ignored. The regex is Python `re`
syntax and is searched case-insensitively. A book with no WORLD_RULES.txt exits 2
and cannot pass, which is the same stance the controls suite takes on a scan that
expands to zero files: not-run is never a pass.

This tool measures nothing and holds no opinion about style. Every hit is a
question for a person ("is this sentence saying the city has a van?"), so the
output prints the line, and the caller decides. It never edits anything.
"""

import os
import re
import sys


def die(msg, code):
    print(msg)
    sys.exit(code)


def load_rules(book):
    path = os.path.join(book, "WORLD_RULES.txt")
    if not os.path.isfile(path):
        die("no WORLD_RULES.txt in %s - this book's physics is ungoverned, "
            "which is not a pass" % book, 2)
    rules = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.rstrip("\n").rstrip("\r")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            # Split on the FIRST and the LAST pipe, never on every pipe: every
            # real rule uses alternation inside its regex, and a naive split cuts
            # the pattern at its first "|" and then reports a syntax error in a
            # rule that is perfectly correct. That is exactly how the first
            # version of this file failed its own positive control.
            if line.count("|") < 2:
                die("%s:%d: expected ID|regex|why, got %r" % (path, n, line), 2)
            rid, rest = line.split("|", 1)
            pattern, why = rest.rsplit("|", 1)
            rid, pattern, why = rid.strip(), pattern.strip(), why.strip()
            try:
                rules.append((rid, re.compile(pattern, re.IGNORECASE), why))
            except re.error as exc:
                die("%s:%d: bad regex %r (%s)" % (path, n, pattern, exc), 2)
    if not rules:
        die("%s has no rules - an empty lexicon cannot pass a book" % path, 2)
    return rules


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
    rules = load_rules(book)
    files = targets(book, argv[2:])

    hits = 0
    per_rule = {}
    for path in files:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, 1):
                for rid, rx, why in rules:
                    for m in rx.finditer(line):
                        hits += 1
                        per_rule[rid] = per_rule.get(rid, 0) + 1
                        snippet = line.strip()
                        if len(snippet) > 120:
                            start = max(0, m.start() - 45)
                            snippet = "..." + snippet[start:start + 120] + "..."
                        print("%s:%d: %s  [%s]  %s"
                              % (path, lineno, m.group(0), rid, why))
                        print("        %s" % snippet)
                        break  # one report per rule per line is enough to fix it

    print("")
    print("scanned %d file(s) against %d rule(s): %s"
          % (len(files), len(rules), os.path.join(book, "WORLD_RULES.txt")))
    if hits:
        print("hits by rule: " + ", ".join("%s x%d" % (k, per_rule[k]) for k in sorted(per_rule)))
        print("RESULT: FAIL - the world contradicts itself on the page above.")
        return 1
    print("RESULT: PASS - nothing on these pages breaks this book's physics.")
    print("        Mechanical only: the rules cover the objects that have been named,")
    print("        not the ones nobody has thought of yet.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
