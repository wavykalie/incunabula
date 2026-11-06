#!/usr/bin/env python3
"""length-adjusted.py - the REDTEAM.md B6 sensitivity the study declared and never ran.

Residualises every feature on log10(analysis words), fitting the line within Arm C-dist-2,
then re-runs the primary classifier, its 10..90 band and the 10,000-relabelling permutation
test on the residuals. If a residual row is really a length finding, this is where it shows:
the row either leaves the band or loses its test.

It also prints the candidate-check table a shipped threshold would need: the human p10/p90
from C-dist-2 and that band's measured false-positive rate on a held-out half of the same
corpus (`corpus/dist-features-2/cdist.csv`).

usage:
    python analysis/length-adjusted.py
"""

import csv
import importlib.util
import json
import math
import os
import random
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


an = _load("study_analyze", os.path.join(HERE, "analyze.py"))

FEATURES_V2 = os.path.join(STUDY, "features-v2")
DIST2 = os.path.join(STUDY, "corpus", "dist-features-2")
CDIST2_CSV = os.path.join(DIST2, "cdist.csv")

TWELVE = ("str_open_weather_share", "syn_tag_breath_share", "lex_ttr_rarefied",
          "lex_opener_top1_share", "lex_hedges_per_1k", "syn_para_cv",
          "lex_ly_adverbs_per_1k", "lex_ai_terms_per_1k", "lex_opener_as_share",
          "lex_opener_but_share", "syn_long_sent_share", "syn_sent_words_sd")


def load_books():
    """Arm A and B from the v2 tree, Arm C from the second stratum (never pooled)."""
    arm_of, premise_of, _ = an.load_manifest(os.path.join(STUDY, "books", "manifest.csv"))
    cohort_of = an.load_cohorts(os.path.join(STUDY, "books", "manifest.csv"))
    books = {}
    for base in (FEATURES_V2, DIST2):
        for name in sorted(os.listdir(base)):
            if not name.endswith(".json"):
                continue
            with open(os.path.join(base, name), encoding="utf-8") as fh:
                rec = json.load(fh)
            bid = rec["book"]
            if bid.startswith("C-dist-") and base == FEATURES_V2:
                continue                     # the first stratum is not the baseline here
            arm, premise = an.infer(bid)
            rec["arm"] = arm_of.get(bid, arm) or arm
            rec["premise_id"] = premise_of.get(bid) or premise
            rec["cohort"] = cohort_of.get(bid)
            books[bid] = rec
    return {b: r for b, r in books.items()
            if (r.get("words") or 0) <= 120000 and not r.get("cohort")}


def fit(books, name):
    pairs = [(math.log10(r["words"]), float(r["features"][name]))
             for r in books.values() if r["arm"] == "C"
             and r["features"].get(name) is not None]
    if len(pairs) < 10:
        return None
    mx = st.mean(x for x, _ in pairs)
    my = st.mean(y for _, y in pairs)
    sxx = sum((x - mx) ** 2 for x, _ in pairs)
    slope = sum((x - mx) * (y - my) for x, y in pairs) / sxx if sxx else 0.0
    return my - slope * mx, slope


def residualised(books):
    out = {}
    fits = {n: fit(books, n) for n in TWELVE}
    for bid, rec in books.items():
        features = dict(rec["features"])
        for name in TWELVE:
            if features.get(name) is None or fits[name] is None:
                continue
            intercept, slope = fits[name]
            features[name] = float(features[name]) - (
                intercept + slope * math.log10(rec["words"]))
        out[bid] = dict(rec, features=features)
    return out


def main():
    books = load_books()
    rows = an.analyse(residualised(books), 10.0, 0.5, random.Random(20261030), 10000)
    print("length-adjusted (residualised on log10 words within Arm C-dist-2)")
    print(f"{'feature':<28}{'B med':>9}{'C band':>18}{'eff':>7}{'p':>9}{'resid':>7}")
    for name in TWELVE:
        r = rows[name]
        lo, hi = r["band"]
        print(f"{name:<28}{an.med(r['vals']['B']):>9.3f}{f'{lo:.3f}..{hi:.3f}':>18}"
              f"{r['effect']:>7.2f}{r['perm_p']:>9.4f}"
              f"{'yes' if r['residual'] else 'no':>7}")

    cd = {r["feature"]: r for r in
          csv.DictReader(open(CDIST2_CSV, encoding="utf-8"))}
    nv2 = {r["feature"]: r for r in
           csv.DictReader(open(os.path.join(HERE, "run-v2", "features.csv"),
                               encoding="utf-8"))}
    print("\ncandidate check table from C-dist-2 (n=188, 167 under the filter)")
    print(f"{'feature':<28}{'dir':>9}{'B med':>8}{'p10':>8}{'p90':>8}{'fp':>6}")
    for name in TWELVE:
        if nv2[name].get("residual_tell") != "True":
            continue
        r = cd[name]
        print(f"{name:<28}{nv2[name]['direction']:>9}"
              f"{float(nv2[name]['med_B']):>8.3f}"
              f"{float(r['p10']):>8.3f}{float(r['p90']):>8.3f}"
              f"{100 * float(r['fp_holdout']):>5.0f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
