#!/usr/bin/env python3
"""lint-chapter.py - the drafting linter: one chapter, every rule hit with a span.

WHY THIS EXISTS
  The gates run at phase boundaries and speak in rates; a writer mid-chapter needs
  spans. The field failure this came from: natural phrasing ("athletic leverage",
  chapter 2) and descriptive participles (", reflecting", chapter 8) tripped hard caps
  at FINAL verification, costing a full re-assembly and re-render - when both rows
  fire per chapter and the scanner was always able to say so. What was missing was
  the drafting-speed rendering: which line, which character, which row, now.

WHAT IT IS, AND WHAT IT IS NOT
  It is NOT a gate and it holds no rules of its own. Every pattern, every cap and
  every tier is READ OUT OF tools/prose/deslop-check.sh at runtime - the scanner is
  the single home of the rule table, and this file renders it. Where the two disagree,
  the scanner is right: its arithmetic runs on normalised text with tiers and
  exemptions (A22 self-scan demotion, REPORT tier gating) that this file does not
  reimplement. If the scanner is not where this file expects, the lint refuses to run
  (exit 3) rather than typing the rules from memory - a duplicated rule table is the
  drift this project has been bitten by at instrument level twice already.

  Case handling mirrors the scanner exactly: HARD rows match case-insensitively
  (grep -oiE); the density tiers match case-sensitively (grep -oE). The cap
  comparison is the scanner's own integer arithmetic, n*aw > an*words.

  The one computed row is the sentence-opener cluster (P1), because a span map is
  what makes that row actionable. Its sentence split is this file's approximation -
  the scanner's awk is authoritative and their counts may differ.

EXIT CODES
  0  report produced, every row under its cap
  1  nothing checkable: no readable chapter, or an empty one
  2  report produced, at least one row over cap - the scanner would fail this chapter
  3  the scanner's rule table could not be read - no rules, no lint

usage:  tools/lint-chapter.py CHAPTER.md [CHAPTER.md ...]
        tools/lint-chapter.py --caps        (print the rule table, then exit)
"""

import os
import re
import sys

SCANNER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "prose", "deslop-check.sh")

OPEN_PER_N = 6        # P1: same 2-word opener > 6 per 1000 words
OPEN_SHARE_PCT = 15   # P1: top opener > 15% of all sentences
OPEN_LIST_MIN = 3     # list an opener at this count even when under every cap


def load_rules():
    """Read the rule arrays out of deslop-check.sh. Never a copy: if the parse
    fails or the file moved, this tool must not run on remembered rules."""
    if not os.path.isfile(SCANNER):
        return None, f"scanner not found at {SCANNER}"
    with open(SCANNER, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    arrays = {}
    for m in re.finditer(r"^(HARD|DENSITY|DEMOTED|REPORT|WARN_ONLY)=\(\n(.*?)^\)",
                         text, re.M | re.S):
        rows = []
        for line in m.group(2).splitlines():
            q = re.search(r"'([^']*)'", line)
            if q:
                rows.append(q.group(1))
        arrays[m.group(1)] = rows
    if not arrays.get("DENSITY") or not arrays.get("HARD"):
        return None, "the scanner's rule arrays did not parse - refusing to lint"
    rules = []   # (tier, id, name, an, aw, wn, ww, regex, flags)
    for row in arrays.get("HARD", []):
        parts = row.split("|", 2)
        if len(parts) == 3:
            rules.append(("HARD", parts[0], parts[1], None, None, None, None,
                          parts[2], re.I))
    for tier in ("DENSITY", "DEMOTED", "REPORT"):
        for row in arrays.get(tier, []):
            parts = row.split("|", 6)
            if len(parts) == 7 and parts[2].isdigit():
                rules.append((tier, parts[0], parts[1], int(parts[2]), int(parts[3]),
                              int(parts[4]) if parts[4] else None,
                              int(parts[5]) if parts[5] else None,
                              parts[6], 0))
    for row in arrays.get("WARN_ONLY", []):
        parts = row.split("|", 2)
        if len(parts) == 3:
            rules.append(("WARN_ONLY", parts[0], parts[1], None, None, None, None,
                          parts[2], re.I))
    return rules, None


def normalise(text):
    # Mirror the scanner's read path: stray CRs hide sentence boundaries.
    return text.replace("\r", "")


def strip_gutenberg(text):
    m = re.search(r"^\*\*\* *START OF (?:THE|THIS) PROJECT GUTENBERG.*$",
                  text, re.M)
    if not m:
        return text
    body = re.sub(r"^\*\*\* *END OF (?:THE|THIS) PROJECT GUTENBERG.*$", "", text[m.end():],
                  flags=re.M)
    return body if body.strip() else text


def span(text, pos):
    """1-based line and character offset of an absolute position."""
    line = text.count("\n", 0, pos) + 1
    col = pos - (text.rfind("\n", 0, pos) + 1) + 1
    return line, col


def lint_file(path):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        text = strip_gutenberg(normalise(fh.read()))
    words = max(len(text.split()), 1)
    print("=" * 67)
    print(f"## {path}   {words} words")
    print("=" * 67)
    over = 0

    for tier, rid, name, an, aw, wn, ww, pattern, flags in RULES:
        try:
            rx = re.compile(pattern, flags)
        except re.error as exc:
            print(f"   --    {rid:<5} pattern will not compile ({exc}) - the scanner's")
            print(f"          grep -E may still accept it; the scanner is authoritative")
            continue
        hits = list(rx.finditer(text))
        if not hits:
            continue
        n = len(hits)
        if an is None:                      # HARD / WARN_ONLY: presence rows
            verdict = "FAIL" if tier == "HARD" else "warn"
            if tier != "HARD":
                verdict = "warn"
            print(f"   {verdict:<5} {rid:<5} {name:<22} x{n}  "
                  f"[{tier.lower()}]{'  [demoted from HARD]' if tier == 'DEMOTED' else ''}")
            for h in hits[:8]:
                ln, col = span(text, h.start())
                frag = h.group(0).replace("\n", " ")[:60]
                print(f"          {ln}:{col}  {frag!r}")
            if n > 8:
                print(f"          ... and {n - 8} more")
            if tier == "HARD":
                over = 1
            continue
        rate = n * 1000.0 / words
        if n * aw > an * words:
            if tier == "REPORT":
                tag = f"over {an}/{aw}, reported not gated"
            else:
                tag = f"OVER cap {an}/{aw}"
                over = 1
            verdict = "--" if tier == "REPORT" else "OVER"
        elif wn is not None and n * ww > wn * words:
            verdict, tag = "warn", f"warn band (cap {an}/{aw})"
        else:
            verdict, tag = "ok", f"cap {an}/{aw}"
        print(f"   {verdict:<5} {rid:<5} {name:<22} {rate:.2f} per 1k ({tag})")
        for h in hits[:8]:
            ln, col = span(text, h.start())
            frag = h.group(0).replace("\n", " ")[:60]
            print(f"          {ln}:{col}  {frag!r}")
        if n > 8:
            print(f"          ... and {n - 8} more")

    # P1, approximated for span-mapping. The scanner's awk is authoritative.
    cuts = [0] + [m.end() for m in re.finditer(r"[.!?]+[ \t]+|\n{2,}", text)] + [len(text)]
    sents = [(cuts[i], text[cuts[i]:cuts[i + 1]]) for i in range(len(cuts) - 1)]
    openers = {}
    for start, s in sents:
        words2 = re.findall(r"[A-Za-z']+", s)
        if len(words2) >= 2:
            key = (words2[0] + " " + words2[1]).lower()
            first = re.search(r"[A-Za-z']", s)
            at = start + (first.start() if first else 0)
            openers.setdefault(key, []).append(span(text, at))
    printed = False
    for key, at in sorted(openers.items(), key=lambda kv: -len(kv[1])):
        count = len(at)
        share = 100.0 * count / max(len(sents), 1)
        if count < OPEN_LIST_MIN:
            continue
        if count * 1000 > OPEN_PER_N * words:
            verdict, tag = "OVER", f"over {OPEN_PER_N} per 1k (approximate)"
            over = 1
        elif share > OPEN_SHARE_PCT:
            verdict, tag = "warn", f"top-opener share {share:.0f}% (approximate)"
        else:
            verdict, tag = "--", f"x{count} (approximate)"
        where = ", ".join(f"{ln}:{col}" for ln, col in at[:8])
        print(f"   {verdict:<5} P1    opener {key!r:<24} {tag}")
        print(f"          {where}{'' if count <= 8 else f', ... and {count - 8} more'}")
        printed = True
    if not printed:
        print("   ok    P1    no opener repeated three times (approximate)")

    print()
    print("  This is the drafting rendering of tools/prose/deslop-check.sh's rule table,")
    print("  read live from the scanner. deslop-check.sh is the gate; where the two")
    print("  disagree, the scanner is right. Fix spans here, verify there.")
    return over


def main():
    global RULES
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if "--caps" in sys.argv:
        RULES, err = load_rules()
        if err:
            print(f"lint-chapter: {err}")
            return 3
        for tier, rid, name, an, aw, wn, ww, pattern, flags in RULES:
            cap = f"{an}/{aw}" if an is not None else "presence"
            print(f"{rid:<6} {tier:<9} {name:<24} {cap}")
        return 0
    if not args:
        print(__doc__)
        return 1
    RULES, err = load_rules()
    if err:
        print(f"lint-chapter: {err}")
        print("             No rules, no lint. The rule table lives in the scanner and")
        print("             is never retyped here - that is the drift this design forbids.")
        return 3
    over = 0
    checked = 0
    for arg in args:
        if not os.path.isfile(arg):
            print(f"lint-chapter: no such chapter: {arg}")
            continue
        checked += 1
        over |= lint_file(arg)
        print()
    if checked == 0:
        print("lint-chapter: nothing checkable.")
        return 1
    return 2 if over else 0


RULES = []

if __name__ == "__main__":
    sys.exit(main())
