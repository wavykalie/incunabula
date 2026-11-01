#!/usr/bin/env python3
"""analyze.py - distributions, paired A-vs-B, and the residual-tell rule.

Design §9, with the four corrections in study/REDTEAM.md M1-M3 applied. The output is a
report and three CSVs; every number in them comes from one run of the frozen extractor on
filed texts, which is the only traceability claim §9.2 makes.

WHAT THIS DELIBERATELY DOES NOT DO
  Blend features into an "AI-ness score". The design forbids it for a good reason: the
  per-feature pattern is the only thing that tells the scanner what to check.

THE FIVE CATEGORIES, AND WHY FIVE
  §9.6 has four (fixed / partial / unchanged / worsened) and §9.5 adds "unclear" without
  defining it, so a borderline feature has to be forced into a win or a loss. Here:

    fixed      Arm B's median lies inside Arm C's central `--band` (default 10-90th pct)
    worsened   |medianB - medianC| > |medianA - medianC| + 0.2 sdC
    partial    B closed at least half the A-to-C gap
    unchanged  |medianB - medianA| <= 0.2 sdC
    unclear    anything else, INCLUDING the case where A had no gap to close

  "unclear" is a result and stays in the report. It is never counted as fixed.

DIRECTION
  Each feature declares whether lower or higher is more human. "twosided" compares the
  absolute distance from the human median, because a sentence-length variance or a TTR
  has no good direction and a signed test would invert on some rows.

RESIDUAL TELL (the §10 candidates)
  Requires all three: B's median outside C's central band, an effect at least
  `--min-effect` human standard deviations wide, and a permutation p below .05 on the
  20-vs-C comparison. The band alone is what REDTEAM.md B1 objects to; the effect floor
  and the test are what make the row a candidate rather than a coincidence.

usage:
    python analyze.py --features DIR [--manifest CSV] [--out DIR]
"""

import argparse
import csv
import importlib.util
import json
import math
import os
import random
import statistics as st
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))
EXTRACT = os.path.join(STUDY, "extract", "features.py")


def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


feat = _load("study_features", EXTRACT)

ARMS = ("A", "B", "C")
ARM_NAME = {"A": "naive", "B": "pipeline", "C": "human"}
MANIFEST_FIELDS = ("book_id", "arm", "premise_id", "genre", "word_count", "chapter_count",
                   "model_id", "deviations")


# ------------------------------------------------------------------ statistics
def quantile(vals, q):
    """Linear-interpolated quantile, the same definition measure.py uses."""
    xs = sorted(vals)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def med(vals):
    return st.median(vals) if vals else None


def sd(vals):
    return st.stdev(vals) if len(vals) > 1 else 0.0


def robust_sd(vals):
    """IQR/1.349: the small-sample spread estimate, less hostage to one outlier."""
    if len(vals) < 3:
        return sd(vals)
    iqr = quantile(vals, .75) - quantile(vals, .25)
    return iqr / 1.349 if iqr else sd(vals)


def permutation_p(b, c, rng, iters=10000):
    """Two-sided permutation test on the difference of medians.

    Under the null the arm label carries no information, so the observed |medianB -
    medianC| is compared against the same statistic under relabelling. This is a test of
    "no difference", not of "residual"; the residual rule needs the effect floor too.
    """
    if len(b) < 2 or len(c) < 2:
        return None
    obs = abs(med(b) - med(c))
    pool = list(b) + list(c)
    n = len(b)
    hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        if abs(med(pool[:n]) - med(pool[n:])) >= obs - 1e-12:
            hits += 1
    return (hits + 1) / (iters + 1)


def sign_test(deltas):
    """Two-sided exact binomial on the signs of the paired deltas (zeros dropped)."""
    d = [x for x in deltas if abs(x) > 1e-12]
    if not d:
        return None, 0, 0
    k = sum(1 for x in d if x < 0)       # negative = moved toward the human median
    n = len(d)
    p = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / (2 ** (n - 1))
    return min(1.0, p), k, n


def bh(pvals):
    """Benjamini-Hochberg q values, in the input order."""
    idx = [i for i, p in enumerate(pvals) if p is not None]
    if not idx:
        return [None] * len(pvals)
    ordered = sorted(((pvals[i], i) for i in idx))
    m = len(ordered)
    q = {}
    running = 1.0
    for rank in range(m, 0, -1):
        p, i = ordered[rank - 1]
        running = min(running, p * m / rank)
        q[i] = running
    return [q.get(i) for i in range(len(pvals))]


def spearman(x, y):
    if len(x) < 4 or len(set(x)) < 2 or len(set(y)) < 2:
        return None
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


# ------------------------------------------------------------------ loading
def load_manifest(path):
    arm_of, premise_of, rows = {}, {}, {}
    if not path or not os.path.exists(path):
        return arm_of, premise_of, rows
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            bid = (row.get("book_id") or "").strip()
            if not bid:
                continue
            arm_of[bid] = (row.get("arm") or "").strip().upper()[:1]
            premise_of[bid] = (row.get("premise_id") or "").strip()
            rows[bid] = row
    return arm_of, premise_of, rows


def infer(bid):
    """Fall back to the filing convention: A-01 / B-01 / C-01."""
    arm = bid[:1].upper() if bid[:1].upper() in ARMS else "?"
    premise = bid.split("-", 1)[1] if "-" in bid else bid
    return arm, premise


def load_books(feature_dir, manifest):
    arm_of, premise_of, mrows = load_manifest(manifest)
    books = {}
    for name in sorted(os.listdir(feature_dir)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(feature_dir, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        bid = rec["book"]
        arm, premise = infer(bid)
        arm = arm_of.get(bid, arm) or arm
        premise = premise_of.get(bid) or premise
        rec["arm"], rec["premise_id"] = arm, premise
        rec["manifest"] = mrows.get(bid, {})
        books[bid] = rec
    return books


# ------------------------------------------------------------------ per-feature
def classify(meta, arm_vals, c_med, c_sd, band_lo, band_hi):
    """Return (class, d_a, d_b, no_gap).

    The no-gap test comes FIRST. A feature on which Arm A already sits at the human median
    has nothing to fix, and calling that "fixed" would put a win in the report for work
    nobody did - the same error as crediting the pipeline for a row it did not move. These
    rows are reported as unclear with the note "no A-vs-C gap", and they are a result: the
    hypothesis died.
    """
    a, b = arm_vals.get("A", []), arm_vals.get("B", [])
    if not a or not b or c_med is None:
        return "unmeasured", None, None, False
    med_a, med_b = med(a), med(b)
    d_a, d_b = med_a - c_med, med_b - c_med
    if meta["direction"] == "twosided":
        d_a, d_b = abs(d_a), abs(d_b)
    no_gap = (abs(d_a) <= 0.25 * c_sd) if c_sd else (abs(d_a) == 0)
    if meta["direction"] == "none":
        return "descriptive", d_a, d_b, no_gap
    if no_gap:
        return "unclear", d_a, d_b, True

    # When every human book scored the same, the noise scale cannot be c_sd (it is zero,
    # which would make "unchanged" unreachable and let a 92%-vs-100% coda share read as
    # "unclear"). Fall back to the gap being closed: silent on a feature that moved 8% of
    # the way is "unchanged", and that is the honest label.
    scale = c_sd if c_sd else abs(d_a)
    moved = abs(med_b - med_a)
    if band_lo is not None and band_lo <= med_b <= band_hi:
        return "fixed", d_a, d_b, False
    if abs(d_b) > abs(d_a) + 0.2 * scale:
        return "worsened", d_a, d_b, False
    if abs(d_b) <= 0.5 * abs(d_a):
        return "partial", d_a, d_b, False
    if moved <= 0.2 * scale:
        return "unchanged", d_a, d_b, False
    return "unclear", d_a, d_b, False


def analyse(books, band_pct, min_effect, rng, iters):
    order = [k for k in feat.FEATURES]
    rows = {}
    for name in order:
        meta = feat.FEATURES[name]
        vals = {a: [] for a in ARMS}
        for bid, rec in books.items():
            v = rec["features"].get(name)
            if v is None or rec["arm"] not in vals:
                continue
            vals[rec["arm"]].append(float(v))
        if not vals["C"] or len(vals["C"]) < 3:
            rows[name] = {"meta": meta, "vals": vals, "class": "unmeasured",
                          "reason": "fewer than 3 human books"}
            continue

        c = vals["C"]
        c_med = med(c)
        c_sd = robust_sd(c) or 0.0
        lo, hi = quantile(c, band_pct / 100.0), quantile(c, 1 - band_pct / 100.0)
        klass, d_a, d_b, no_gap = classify(meta, vals, c_med, c_sd, lo, hi)

        # paired A-vs-B, same premise
        by_prem = defaultdict(dict)
        for bid, rec in books.items():
            v = rec["features"].get(name)
            if v is None or rec["arm"] not in ("A", "B"):
                continue
            by_prem[rec["premise_id"]][rec["arm"]] = float(v)
        deltas = []
        for pid, pair in by_prem.items():
            if "A" in pair and "B" in pair:
                deltas.append(abs(pair["B"] - c_med) - abs(pair["A"] - c_med))
        sp, toward, npairs = sign_test(deltas)

        p = permutation_p(vals["B"], c, rng, iters)
        effect = abs(med(vals["B"]) - c_med) / c_sd if c_sd else None
        outside = med(vals["B"]) < lo or med(vals["B"]) > hi
        residual = bool(meta["direction"] != "none" and outside and effect is not None
                        and effect >= min_effect and p is not None and p < 0.05)

        gap = abs(d_a) if d_a is not None else 0.0
        share_closed = None
        if not no_gap and gap > 0:
            share_closed = 1 - abs(d_b) / gap

        pairs_xy = [(rec["words"], float(rec["features"][name]))
                    for rec in books.values()
                    if rec["arm"] in ARMS and rec["features"].get(name) is not None]
        rho = spearman([p0 for p0, _ in pairs_xy], [p1 for _, p1 in pairs_xy]) if pairs_xy else None

        rows[name] = {
            "meta": meta, "vals": vals, "class": klass, "c_med": c_med, "c_sd": c_sd,
            "band": (lo, hi), "d_a": d_a, "d_b": d_b, "share_closed": share_closed,
            "pairs_toward": toward, "pairs_n": npairs, "sign_p": sp, "perm_p": p,
            "effect": effect, "residual": residual, "len_rho": rho,
            "outside": outside, "no_gap": no_gap, "flat_c": c_sd == 0,
        }

    for family in sorted({r["meta"]["family"] for r in rows.values()}):
        names = [n for n, r in rows.items() if r["meta"]["family"] == family]
        qs = bh([rows[n].get("perm_p") for n in names])
        for n, q in zip(names, qs):
            rows[n]["q"] = q
    return rows


# ------------------------------------------------------------------ cross-book
def jaccard(a, b):
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb) if sa and sb else 0.0


def cross_book(books):
    out = {}
    for arm in ARMS:
        recs = [r for r in books.values() if r["arm"] == arm]
        if len(recs) < 2:
            out[arm] = {"n": len(recs)}
            continue
        open_pairs = [jaccard(a["cross"]["opening"], b["cross"]["opening"])
                      for i, a in enumerate(recs) for b in recs[i + 1:]]
        close_pairs = [jaccard(a["cross"]["closing"], b["cross"]["closing"])
                       for i, a in enumerate(recs) for b in recs[i + 1:]]

        name_books = defaultdict(set)
        for r in recs:
            for n in r["details"]["names"]["firsts"]:
                name_books[n].add(r["book"])
        reuse = {n: sorted(b) for n, b in name_books.items() if len(b) >= 2}
        threshold = max(2, int(round(0.2 * len(recs))))

        chapter_counts = [r["features"]["str_chapters"] for r in recs
                          if r["features"].get("str_chapters") is not None]
        cd = [r["features"]["str_coda_share"] for r in recs
              if r["features"].get("str_coda_share") is not None]
        frames = Counter()
        for r in recs:
            fs = r["details"].get("frame_share") or {}
            if fs:
                frames[max(fs.items(), key=lambda kv: kv[1])[0]] += 1

        out[arm] = {
            "n": len(recs),
            "opening_similarity_median": med(open_pairs),
            "opening_similarity_max": max(open_pairs) if open_pairs else None,
            "closing_similarity_median": med(close_pairs),
            "closing_similarity_max": max(close_pairs) if close_pairs else None,
            "names_in_multiple_books": len(reuse),
            "names_at_or_above_threshold": {n: b for n, b in reuse.items()
                                            if len(b) >= threshold},
            "name_reuse": reuse,
            "chapter_count_sd": sd(chapter_counts),
            "books_closing_on_coda": sum(1 for v in cd if v) if cd else 0,
            "dominant_frame_counts": dict(frames),
        }
    return out


# ------------------------------------------------------------------ report
def fmt(v, nd=2):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    return f"{v:.{nd}f}"


def write_outputs(books, rows, cross, outdir, args):
    os.makedirs(outdir, exist_ok=True)

    with open(os.path.join(outdir, "books.csv"), "w", encoding="utf-8", newline="") as fh:
        wcsv = csv.writer(fh)
        names = [n for n in feat.FEATURES]
        wcsv.writerow(["book_id", "arm", "premise_id", "words", "chapters"] + names)
        for bid in sorted(books):
            r = books[bid]
            wcsv.writerow([bid, r["arm"], r["premise_id"], r["words"], r["chapters"]] +
                          [r["features"].get(n) for n in names])

    with open(os.path.join(outdir, "features.csv"), "w", encoding="utf-8", newline="") as fh:
        wcsv = csv.writer(fh)
        wcsv.writerow(["feature", "family", "direction", "replication", "class",
                       "n_A", "med_A", "n_B", "med_B", "n_C", "med_C", "sd_C",
                       "band_lo", "band_hi", "effect_d", "share_closed",
                       "pairs_toward_human", "pairs_n", "sign_p", "perm_p", "bh_q",
                       "residual_tell", "len_rho"])
        for name, r in rows.items():
            v = r["vals"]
            lo, hi = r.get("band", (None, None))
            wcsv.writerow([
                name, r["meta"]["family"], r["meta"]["direction"],
                r["meta"]["replication"], r["class"],
                len(v["A"]), fmt(med(v["A"]), 4), len(v["B"]), fmt(med(v["B"]), 4),
                len(v["C"]), fmt(r.get("c_med"), 4), fmt(r.get("c_sd"), 4),
                fmt(lo, 4), fmt(hi, 4), fmt(r.get("effect"), 3),
                fmt(r.get("share_closed"), 3), r.get("pairs_toward"), r.get("pairs_n"),
                fmt(r.get("sign_p"), 4), fmt(r.get("perm_p"), 4), fmt(r.get("q"), 4),
                r.get("residual", False), fmt(r.get("len_rho"), 2),
            ])

    lines = []
    add = lines.append
    n = {a: sum(1 for r in books.values() if r["arm"] == a) for a in ARMS}
    add("# Study analysis\n")
    add(f"Books: A={n['A']}  B={n['B']}  C={n['C']}   "
        f"band=central {100 - 2 * args.band:.0f}% of Arm C   "
        f"min effect={args.min_effect} sdC\n")
    if getattr(args, "max_words", None):
        add(f"> Length filter: books above {args.max_words:,} analysis words are excluded. "
            f"The long-form stratum is exploratory and is never pooled with the primary "
            f"pairs (`DECISIONS.md` §2).\n")
    if getattr(args, "exclude_books", ""):
        add(f"> Excluded by id: `{args.exclude_books}`. These are the voice-sensitivity "
            f"books, compared to their own twins separately and never pooled into the "
            f"primary distributions or pairing (`DECISIONS.md` §3).\n")
    if n["C"] < 30:
        add(f"> **Arm C is n={n['C']}.** Thresholds derived from fewer than ~30 human books "
            f"are unstable and are not the basis for a scanner check "
            f"(study/REDTEAM.md B1). Treat every classification below as a hypothesis, "
            f"and derive the shipped threshold from the C-dist corpus.\n")

    counts = Counter(r["class"] for r in rows.values())
    add("## Classification by family\n")
    cats = ("fixed", "partial", "unchanged", "worsened", "unclear", "unmeasured",
            "descriptive")
    add("| family | " + " | ".join(cats) + " |")
    add("|---|" + "---|" * len(cats))
    for family in ("lexical", "syntax", "structure", "names"):
        sub = [r for r in rows.values() if r["meta"]["family"] == family]
        row = [sum(1 for r in sub if r["class"] == c) for c in cats]
        add(f"| {family} | " + " | ".join(str(x) for x in row) + " |")
    add(f"\n`descriptive` rows are book-level outcomes (length, chapter count, cast size) "
        f"with no human direction; they are reported and never scored.")
    add("")

    for family in ("lexical", "syntax", "structure", "names"):
        add(f"## {family}\n")
        add("| feature | A med | B med | C med | C band | class | closed | pairs | p | q | note |")
        add("|---|---|---|---|---|---|---|---|---|---|---|")
        for name, r in rows.items():
            if r["meta"]["family"] != family:
                continue
            v = r["vals"]
            lo, hi = r.get("band", (None, None))
            note = ""
            if r["meta"]["replication"]:
                note = "replication"
            if r.get("residual"):
                note = (note + " " if note else "") + "**residual**"
            if r.get("no_gap"):
                note = (note + " " if note else "") + "no A-vs-C gap"
            if r.get("flat_c"):
                note = (note + " " if note else "") + "C has no spread"
            if r.get("len_rho") is not None and abs(r["len_rho"]) >= 0.5:
                note += " len-confounded"
            add("| `{}` | {} | {} | {} | {}..{} | {} | {} | {}/{} | {} | {} | {} |".format(
                name, fmt(med(v["A"])), fmt(med(v["B"])), fmt(r.get("c_med")),
                fmt(lo), fmt(hi), r["class"], fmt(r.get("share_closed")),
                r.get("pairs_toward") if r.get("pairs_toward") is not None else "-",
                r.get("pairs_n") or 0, fmt(r.get("perm_p"), 3), fmt(r.get("q"), 3), note))
        add("")

    res = [n for n, r in rows.items() if r.get("residual")]
    add("## Residual tells (candidate scanner checks)\n")
    if res:
        add("| feature | B med | C band | effect (sd) | perm p | BH q |")
        add("|---|---|---|---|---|---|")
        for name in res:
            r = rows[name]
            add(f"| `{name}` | {fmt(med(r['vals']['B']))} | "
                f"{fmt(r['band'][0])}..{fmt(r['band'][1])} | {fmt(r['effect'])} | "
                f"{fmt(r['perm_p'], 4)} | {fmt(r.get('q'), 4)} |")
        add("\nEach row still needs §10's remaining steps before it is a check: a human "
            "baseline from C-dist, a threshold measured on that corpus, a false-positive "
            "rate on it, and Kalie's review.\n")
    else:
        add("None. With this Arm C, no feature cleared all three conditions. That is a "
            "result, not a failure to look hard enough.\n")

    add("## Cross-book rows (arm-level)\n")
    add("| row | A | B | C |")
    add("|---|---|---|---|")
    for key in ("opening_similarity_median", "opening_similarity_max",
                "closing_similarity_median", "closing_similarity_max",
                "names_at_or_above_threshold", "chapter_count_sd", "books_closing_on_coda"):
        vals = []
        for arm in ARMS:
            v = cross.get(arm, {}).get(key)
            vals.append(str(len(v)) + " names" if isinstance(v, dict) else fmt(v))
        add(f"| {key} | " + " | ".join(vals) + " |")
    add("")
    for arm in ARMS:
        c = cross.get(arm, {})
        if c.get("names_at_or_above_threshold"):
            top = sorted(c["names_at_or_above_threshold"].items(),
                         key=lambda kv: -len(kv[1]))[:6]
            add(f"- Arm {arm}: recurring first names (>= threshold): " +
                ", ".join(f"{k} ({len(v)} books)" for k, v in top))
    add("")

    add("## Limits of this run\n")
    add("- Mechanical features only. They find tells; they do not judge whether a book is "
        "good (design §10).")
    add("- A null result at these n is not evidence the tell is absent, only that it was "
        "not large enough to show (design §9.8).")
    add("- Names are extracted from prose as a proper-noun inventory, so recurring place "
        "names inflate the counts. Both arms are measured identically, which is what makes "
        "the comparison fair; the inventory is not a cast list.")
    add("- Every row this repo has already measured as a null or with the opposite sign is "
        "marked `replication` and is not a primary endpoint (study/REDTEAM.md B2).")
    add("- `len-confounded` marks |Spearman rho| >= 0.5 against book length; the "
        "length-matched sensitivity run in design §7 has not been applied here.")
    add("- `no A-vs-C gap` marks a feature on which Arm A already sat at the human median. "
        "Those rows are counted as unclear, not fixed: the pipeline cannot be credited "
        "with closing a gap that was not there.")
    add("- `C has no spread` marks a feature every human book scored identically on. No "
        "effect size can be computed against a zero-variance baseline, so those rows are "
        "reported and never called residual tells.")

    with open(os.path.join(outdir, "report.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    return os.path.join(outdir, "report.md")


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--features", required=True, help="directory of extractor JSON")
    ap.add_argument("--manifest", help="manifest.csv (arm and premise per book)")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--band", type=float, default=10.0,
                    help="percent trimmed at each tail of Arm C (default 10)")
    ap.add_argument("--min-effect", type=float, default=0.5,
                    help="residual-tell effect floor, in human SDs (default 0.5)")
    ap.add_argument("--max-words", type=int, default=None,
                    help="drop books above this analysis word count (excludes the "
                         "exploratory long-form stratum from the primary analysis)")
    ap.add_argument("--exclude-books", default="",
                    help="comma-separated book ids or unique substrings to drop, e.g. the "
                         "voice-sensitivity books (B-02V,B-03V,B-09V,B-02W,B-03W,B-09W)")
    ap.add_argument("--iters", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20261030)
    args = ap.parse_args(argv)

    books = load_books(args.features, args.manifest)
    if not books:
        print(f"no extractor JSON under {args.features}. A report that read nothing "
              f"proves nothing.")
        return 1
    dropped = [b for b, r in books.items()
               if args.max_words and (r.get("words") or 0) > args.max_words]
    for b in dropped:
        books.pop(b)
    if dropped:
        print(f"length filter {args.max_words:,}: dropped {len(dropped)} long-form "
              f"book(s) {', '.join(sorted(dropped))}")
    pats = [p.strip() for p in (args.exclude_books or "").split(",") if p.strip()]
    by_id = [b for b in books if any(p in b for p in pats)]
    for b in by_id:
        books.pop(b)
    if by_id:
        print(f"excluded {len(by_id)} book(s) by id: {', '.join(sorted(by_id))}")
    rng = random.Random(args.seed)
    rows = analyse(books, args.band, args.min_effect, rng, args.iters)
    cross = cross_book(books)
    path = write_outputs(books, rows, cross, args.out, args)

    counts = Counter(r["class"] for r in rows.values())
    n = {a: sum(1 for r in books.values() if r["arm"] == a) for a in ARMS}
    print(f"books A={n['A']} B={n['B']} C={n['C']}   "
          f"{' '.join(f'{k}={v}' for k, v in sorted(counts.items()))}")
    print(f"residual tells: {sum(1 for r in rows.values() if r.get('residual'))}")
    print(f"-> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
