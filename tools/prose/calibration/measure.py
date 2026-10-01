#!/usr/bin/env python
"""Measure the deslop-check.sh metrics against a human-written corpus.

The caps in tools/deslop-check.sh were guesses. This measures the same
quantities on published prose (the negative control) so the caps can be set
from data. Ported faithfully from the shell scanner, quirks included.

    usage: measure.py CORPUS_DIR [CORPUS_DIR ...]
"""
import os
import re
import sys
import glob
import statistics as st

# ---------------------------------------------------------------- rule set
# Mirrors the HARD array in tools/deslop-check.sh.
HARD = [
    ("A1", "delve family", r"\b(delve|delves|delving|leverage[ds]?|leveraging|utilize[ds]?|utilizing|streamlin(e|es|ed|ing)|harness(es|ed|ing)?|robust|seamless|cutting-edge)\b"),
    ("A2", "magic adverbs", r"\b(quietly|deeply|fundamentally|remarkably|arguably|profoundly|undeniably|inevitably|subtly)\b"),
    ("A3", "grandiose nouns", r"\b(tapestry|landscape|paradigm|synergy|ecosystem|framework|realm|myriad|intricac(y|ies)|intricate|vibrant|palpable|indelible)\b"),
    ("A4", "serves-as dodge", r"\b(serves as|serving as|stands as|standing as|acts as|marking a|represents a|represents an|is a testament)\b"),
    ("A5", "negative parallelism", r"\b(is not|was not|are not|were not|isn.?t|wasn.?t|aren.?t|weren.?t|rather than) (just|merely|only|about)\b|\bnot merely\b|\bnot only\b[^.]{0,60}\bbut also\b|\bnot because\b[^.]{0,60}\bbut because\b"),
    ("A6", "not X not Y", r"\bNot [a-z].{0,30}\. Not [a-z]"),
    ("A7", "the X? a Y", r"\bThe (result|worst part|scary part|problem|answer|truth|catch|kicker)\? "),
    ("A8", "false suspense", r"\b(here.s the (thing|kicker|catch|problem)|here.s where it gets|here.s what most people)\b"),
    ("A9", "teacher voice", r"\b(let.s (break this down|unpack|explore|dive in)|think of it (as|like)|imagine a world where)\b"),
    ("A10", "filler transition", r"\b(it.s worth noting|it bears mentioning|importantly,|interestingly,|notably,|at its core|when it comes to|due to the fact that|in order to)\b"),
    ("A11", "signposted conclusion", r"\b(in conclusion|to sum up|in summary|all in all|and so we return)\b"),
    ("A12", "despite the challenges", r"\bdespite (these|its|the) (challenges|obstacles|setbacks)\b"),
    ("A13", "truth-is-simple", r"\b(the (reality|truth) is (simple|simpler|clear)|history is (clear|unambiguous)|the evidence is clear)\b"),
    ("A14", "stakes inflation", r"\b(fundamentally reshape|define the next era|something entirely new|change everything|the very nature of)\b"),
    ("A15", "superficial -ing", r", (realizing|knowing|feeling|understanding|reflecting|highlighting|underscoring|emphasizing|symbolizing|showcasing|ensuring|allowing|signaling|a reminder of)\b"),
    ("A16", "vague attribution", r"\b(experts (say|argue|believe|suggest)|observers (have|noted|say)|industry reports|some critics|many would argue|several publications)\b"),
    ("A17", "invented label", r"\bthe [a-z]+ (paradox|trap|creep|divide|vacuum|inversion)\b"),
    ("A18", "gerund litany", r"(^|[.!?] )([A-Z][a-z]+ing [^.!?]{0,40}\. ){2,}"),
    ("A19", "listicle in prose", r"\b(The (first|second|third|fourth) (wall|takeaway|thing|point|problem|reason) is)\b"),
    ("A20", "unicode decoration", r"[→⇒←↔\u201c\u201d\u2018\u2019]"),
    ("A21", "chatbot artifact", r"\b(I hope this helps|let me know if|great question|as an AI)\b"),
    ("A22", "excluded-book residue", r"\bWhat the [A-Z][a-z]+ Kept\b|\b(absorbed|absorbing|absorption|guest book|a ledger|the ledger)\b"),
    ("A23", "parenthetical dash", r"—[^—\n]{1,70}—"),
]

HARD_C = [(i, n, re.compile(p, re.I)) for i, n, p in HARD]

# DENSITY array. The current caps are the thing under calibration.
DENSITY = [
    ("D1", "em dash", re.compile(r"—")),
    ("D2", "rule of three", re.compile(r"[^,.;:]{3,30}, [^,.;:]{3,30}, and [^,.;:]{3,30}")),
]

FRAG_RUN = 4   # current threshold
ANAPHORA_MAX = 2

# Files whose register is not narrative prose. Excluded from every measurement.
BACK_MATTER = ("afterword", "appendix")


def sentences(text):
    """Same split as the shell scanner: break on [.!?] followed by a space."""
    return [s for s in re.split(r"(?<=[.!?]) ", text) if s.strip()]


def measure(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    words = len(raw.split())
    if words == 0:
        return None
    per_k = lambda n: n * 1000.0 / words
    out = {"file": os.path.basename(path), "words": words,
           "hard": {}, "dens": {}, "counts": {}}

    for rid, name, rx in HARD_C:
        hits = rx.findall(raw)
        n = len(hits) if hits and isinstance(hits[0], str) else len(rx.findall(raw))
        # findall returns groups when the pattern has them; count matches instead
        n = len([m for m in rx.finditer(raw)])
        if n:
            out["hard"][rid] = (name, n, per_k(n))

    for rid, name, rx in DENSITY:
        n = len(rx.findall(raw))
        out["dens"][rid] = (name, n, per_k(n))

    sents = sentences(raw)

    # P1 anaphora: same two-word opener, filtered the way the shell scanner does
    openers = {}
    for s in sents:
        s = re.sub(r"^[^A-Za-z]*", "", s)
        toks = s.split()
        if len(toks) >= 2:
            key = (toks[0] + " " + toks[1]).lower()
            if re.fullmatch(r"[a-z]+ [a-z]+", key):
                openers[key] = openers.get(key, 0) + 1
    top = max(openers.values()) if openers else 0
    out["counts"]["P1_max_opener"] = top
    out["counts"]["P1_per_k"] = per_k(top)
    out["counts"]["P1_share"] = 100.0 * top / max(1, len(sents))
    out["counts"]["P1_top"] = sorted(openers.items(), key=lambda kv: -kv[1])[:3]

    # P2 duplicate sentences (8+ words, normalised length > 40)
    seen, dups, examples = set(), 0, []
    for s in sents:
        if len(s.split()) >= 8:
            norm = re.sub(r"[^a-z ]", "", s.lower())
            if len(norm) > 40:
                if norm in seen:
                    dups += 1
                    examples.append(s.strip()[:90])
                seen.add(norm)
    out["counts"]["P2_dups"] = dups
    out["counts"]["P2_examples"] = examples

    # P3 longest run of consecutive sentences with <= 4 words
    best = run = 0
    for s in sents:
        n = len(re.findall(r"[A-Za-z]", s))
        nw = len(s.split())
        if 1 <= nw <= 4:
            run += 1
            best = max(best, run)
        else:
            run = 0
    out["counts"]["P3_max_run"] = best

    out["counts"]["ly_adv_per_k"] = per_k(len(re.findall(r"\b[a-z]{4,}ly\b", raw)))
    out["counts"]["short_sent_pct"] = 100.0 * sum(
        1 for s in sents if 1 <= len(s.split()) <= 4) / max(1, len(sents))
    return out


def pct(vals, q):
    if not vals:
        return float("nan")
    vals = sorted(vals)
    if len(vals) == 1:
        return vals[0]
    k = (len(vals) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(vals) - 1)
    return vals[lo] + (vals[hi] - vals[lo]) * (k - lo)


def collect(dirs):
    """A dir contributes *.txt plus final chapter-*.md; -report and
    -pre-disruption variants are drafts, not published prose. Non-narrative back
    matter (afterword/appendix) is excluded: it is not prose, and its register
    inflates every rate it touches. Keep this rule in sync with CALIBRATION.md
    and with the two-control runner in tools/validate-controls.sh."""
    files = []
    skipped = []
    for d in dirs:
        if os.path.isdir(d):
            for f in sorted(glob.glob(os.path.join(d, "*.txt"))):
                if any(k in os.path.basename(f).lower() for k in BACK_MATTER):
                    skipped.append(f)
                    continue
                files.append(f)
            for f in sorted(glob.glob(os.path.join(d, "*.md"))):
                base = os.path.basename(f)
                if any(k in base.lower() for k in BACK_MATTER):
                    skipped.append(f)
                    continue
                if re.fullmatch(r"chapter-\d+\.md", base):
                    files.append(f)
        else:
            files.append(d)
    if skipped:
        sys.stderr.write("excluded %d non-narrative back-matter file(s): %s\n" % (
            len(skipped), ", ".join(os.path.basename(s) for s in skipped)))
    return files


def main(dirs):
    rows = []
    for f in collect(dirs):
        r = measure(f)
        if r:
            r["corpus"] = os.path.basename(os.path.dirname(f))
            rows.append(r)

    rows.sort(key=lambda r: -r["words"])
    print("=== PER DOCUMENT ===")
    print("%-46s %7s %6s %6s %6s %5s %5s %6s %7s" % (
        "doc", "words", "D1", "D2", "P1mx", "P2", "P3run", "-ly/k", "shrt%"))
    for r in rows:
        c = r["counts"]
        d1 = r["dens"].get("D1", ("", 0, 0))[2]
        d2 = r["dens"].get("D2", ("", 0, 0))[2]
        flag = ""
        if d1 > 4 or d2 > 8 or c["P1_max_opener"] > ANAPHORA_MAX or c["P3_max_run"] >= FRAG_RUN or c["P2_dups"]:
            flag = "  <- would FAIL under current caps"
        print("%-46s %7d %6.1f %6.1f %6d %5d %5d %6.1f %7.1f%s" % (
            r["file"][:46], r["words"], d1, d2, c["P1_max_opener"],
            c["P2_dups"], c["P3_max_run"], c["ly_adv_per_k"],
            c["short_sent_pct"], flag))

    print()
    print("=== DISTRIBUTIONS (per document, n=%d) ===" % len(rows))
    series = {
        "D1 em dash /1k": [r["dens"].get("D1", ("", 0, 0))[2] for r in rows],
        "D2 rule-of-three /1k": [r["dens"].get("D2", ("", 0, 0))[2] for r in rows],
        "P1 max repeated opener": [r["counts"]["P1_max_opener"] for r in rows],
        "P2 duplicate sentences": [r["counts"]["P2_dups"] for r in rows],
        "P3 max short-sent run": [r["counts"]["P3_max_run"] for r in rows],
        "-ly adverbs /1k": [r["counts"]["ly_adv_per_k"] for r in rows],
        "short sentences %": [r["counts"]["short_sent_pct"] for r in rows],
    }
    print("%-26s %7s %7s %7s %7s %7s %7s %7s" % (
        "metric", "median", "p75", "p90", "p95", "p99", "max", "cur cap"))
    caps = {"D1 em dash /1k": "4", "D2 rule-of-three /1k": "8",
            "P1 max repeated opener": str(ANAPHORA_MAX), "P2 duplicate sentences": "0",
            "P3 max short-sent run": str(FRAG_RUN - 1), "-ly adverbs /1k": "note",
            "short sentences %": "note"}
    for k, vals in series.items():
        print("%-26s %7.1f %7.1f %7.1f %7.1f %7.1f %7.1f %7s" % (
            k, st.median(vals), pct(vals, .75), pct(vals, .90), pct(vals, .95),
            pct(vals, .99), max(vals), caps[k]))

    print()
    print("=== BY CORPUS (translation skew check) ===")
    for corpus in sorted(set(r["corpus"] for r in rows)):
        sub = [r for r in rows if r["corpus"] == corpus]
        print("-- %s  (n=%d, %d words)" % (
            corpus, len(sub), sum(r["words"] for r in sub)))
        print("   %-26s %7s %7s %7s" % ("metric", "median", "p90", "max"))
        loc = {
            "D1 em dash /1k": [r["dens"].get("D1", ("", 0, 0))[2] for r in sub],
            "D2 rule-of-three /1k": [r["dens"].get("D2", ("", 0, 0))[2] for r in sub],
            "A20 curly quote /1k": [r["hard"].get("A20", ("", 0, 0))[2] for r in sub],
            "A23 parenthetical /1k": [r["hard"].get("A23", ("", 0, 0))[2] for r in sub],
            "P1 repeats /1k": [r["counts"]["P1_per_k"] for r in sub],
            "P1 top-opener share %": [r["counts"]["P1_share"] for r in sub],
            "P3 max short-sent run": [r["counts"]["P3_max_run"] for r in sub],
            "-ly adverbs /1k": [r["counts"]["ly_adv_per_k"] for r in sub],
        }
        for k, vals in loc.items():
            print("   %-26s %7.1f %7.1f %7.1f" % (
                k, st.median(vals), pct(vals, .90), max(vals)))

    print()
    print("=== HARD RULE HITS ACROSS THE CORPUS ===")
    print("  maxdoc/1k = worst single document's rate (drives any cap)")
    agg = {}
    total_words = sum(r["words"] for r in rows)
    for r in rows:
        for rid, (name, n, pk) in r["hard"].items():
            a = agg.setdefault(rid, {"name": name, "hits": 0, "docs": 0, "max": 0.0})
            a["hits"] += n
            a["docs"] += 1
            a["max"] = max(a["max"], pk)
    print("%-5s %-24s %6s %6s %10s %10s" % (
        "id", "rule", "hits", "docs", "hits/1M", "maxdoc/1k"))
    for rid in sorted(agg, key=lambda x: (len(x), x)):
        a = agg[rid]
        print("%-5s %-24s %6d %6d %10.1f %10.2f" % (
            rid, a["name"], a["hits"], a["docs"],
            a["hits"] * 1e6 / total_words, a["max"]))
    print("corpus words: %d" % total_words)
    clean = [i for i, n, _ in HARD if i not in agg]
    print("rules never triggered by published prose: %s" % ", ".join(clean))

    print()
    print("=== P2 DUPLICATE SENTENCE EXAMPLES (published prose) ===")
    found = False
    for r in rows:
        for ex in r["counts"].get("P2_examples", []):
            print("  %-40s  %s" % (r["file"][:40], ex))
            found = True
    if not found:
        print("  none")


if __name__ == "__main__":
    main(sys.argv[1:])
