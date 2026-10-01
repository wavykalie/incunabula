#!/usr/bin/env python3
"""SCRATCH PROTOTYPE - not shipped, delete after use.

Tests whether the recoverable-anomaly idea survives its own confounds before
anything is written into tools/prose/. The question is whether a tic's
CONCENTRATION IN A MOTIVE-BEARING CONTEXT (speech) separates human from
machine prose, or whether it is only re-measuring how much dialogue a format
has.
"""
import re
import glob
import os
import statistics as st

HERE = os.path.abspath(__file__)
PROSE = os.path.dirname(os.path.dirname(HERE))          # tools/prose
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(PROSE)))   # repository root
V = os.path.join(ROOT, "vermillion-study", "corpus")
M = os.path.join(PROSE, "calibration", "corpus", "montgomery")

QUOTED = re.compile(r"[\u201c\"]([^\u201d\"]{0,400})[\u201d\"]")
PG_START = re.compile(r"^\*\*\* *START OF (THE|THIS) PROJECT GUTENBERG.*?$", re.M)
PG_END = re.compile(r"^\*\*\* *END OF (THE|THIS) PROJECT GUTENBERG", re.M)

DET = {
    "frame: antithesis": r"(?:was|were|is|are) not[^.!?]{0,50}[.!?] +(?:It|That|This|He|She|They) (?:was|were|is|are)",
    "frame: which-is-why": r"(?:which|that|this) is (?:also )?why|it is (?:also )?why",
    "em dash": "\u2014",
    "rule of three": r"[^,.;:]{3,30}, [^,.;:]{3,30}, and [^,.;:]{3,30}",
    "-ly adverb": r"(^|[^a-z])[a-z]{4,}ly([^a-z]|$)",
    "intricate/myriad": r"(^|[^a-z])(intricate|myriad|palpable|tapestry)([^a-z]|$)",
    "robust/seamless": r"(^|[^a-z])(robust|seamless|streamlin\w*)([^a-z]|$)",
}


def clean(t):
    m = PG_START.search(t)
    if m:
        t = t[m.end():]
    m = PG_END.search(t)
    if m:
        t = t[:m.start()]
    return t


def analyse(text):
    text = clean(text)
    spans = [(m.start(), m.end()) for m in QUOTED.finditer(text)]
    dial = sum(b - a for a, b in spans)
    total = len(text)
    if total < 20000 or dial == 0:
        return None
    p_dial_text = dial / total
    out = {}
    for name, pat in DET.items():
        hits = list(re.compile(pat, re.I).finditer(text))
        if len(hits) < 8:
            continue
        d = sum(1 for m in hits if any(a <= m.start() < b for a, b in spans))
        E = (d / len(hits)) / p_dial_text
        B = 10
        bins = [0] * B
        for m in hits:
            bins[min(int(m.start() / total * B), B - 1)] += 1
        n = len(hits)
        g = sum((2 * i - B - 1) * v for i, v in enumerate(bins, 1)) / (n * B)
        out[name] = (n, E, g)
    return p_dial_text, out


def pearson(x, y):
    mx, my = st.mean(x), st.mean(y)
    den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** .5
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / max(den, 1e-12)


def collect(pattern):
    rows = []
    for p in sorted(glob.glob(pattern)):
        r = analyse(open(p, encoding="utf-8", errors="ignore").read())
        if r:
            rows.append((p, r[0], r[1]))
    return rows


def med(xs):
    return st.median(xs) if xs else float("nan")


if __name__ == "__main__":
    sets = {
        "HUMAN 19th c": os.path.join(V, "human", "*.txt"),
        "MONTGOMERY": os.path.join(M, "*.txt"),
        "MACHINE": os.path.join(V, "ai", "*.txt"),
    }
    for label, pat in sets.items():
        rows = collect(pat)
        print("=" * 72)
        print("%s   %d measurable   dialogue share median %.1f%%"
              % (label, len(rows), 100 * med([r[1] for r in rows])))
        agg = {}
        for _, _, out in rows:
            for k, (n, E, g) in out.items():
                agg.setdefault(k, []).append((E, g, n))
        print("  %-20s %5s %9s %9s %9s" % ("tic", "docs", "enrich", "Gini", "hits"))
        for k, v in sorted(agg.items(), key=lambda kv: -med([x[0] for x in kv[1]])):
            print("  %-20s %5d %9.2f %9.2f %9.0f"
                  % (k, len(v), med([x[0] for x in v]), med([x[1] for x in v]),
                     med([x[2] for x in v])))
        print()

    print("=" * 72)
    print("CONFOUND TEST: within a corpus, does enrichment track dialogue share?")
    print("If yes, cross-corpus differences are an artefact of format, not a finding.")
    print()
    for label, pat in sets.items():
        rows = collect(pat)
        print("  %s" % label)
        for tic in ("em dash", "rule of three", "-ly adverb"):
            v = [(d, E) for _, d, out in rows for k, (n, E, g) in out.items() if k == tic]
            if len(v) < 8:
                continue
            print("    %-16s n=%3d  r = %+.3f"
                  % (tic, len(v), pearson([x[0] for x in v], [x[1] for x in v])))
