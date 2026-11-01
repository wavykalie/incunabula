#!/usr/bin/env python3
"""cdist.py - the human distribution every §10 threshold will be derived from.

REDTEAM.md B1 split the human arm by job: C-deep (10 books) rates excerpts, C-dist (>=100
books) supplies every distribution, IQR, threshold and false-positive rate in §9-§10. This
script is the second half of that amendment: it measures C-dist through the frozen extractor
and writes the baseline table.

WHY THE SPLIT-HALF COLUMN EXISTS
  §10 asks "how often does the check fire on Arm C itself?" If the boundary is derived from
  the same ten books it is then tested on, the answer is 10% by construction and the
  question is circular (REDTEAM.md B1). C-dist is large enough to derive the boundary on one
  half and count false positives on the other, so `fp_holdout` is a measurement rather than
  an arithmetic identity.

  The nominal rate is 20%, not 10%: a p10-p90 band cuts 10% from each tail by construction,
  so a perfectly stable band still fires on a fifth of a fresh human sample. A simulated
  null (109 normal draws, hash split, 400 trials) puts that at mean 0.22, sd 0.08 - wider
  than a binomial standard error (0.05), because the band's own quantiles are estimated
  from a finite sample and that error is part of the procedure.

  So the reference is a bootstrap of the *whole* procedure: resample the derivation half,
  draw a band from it, score a resampled holdout, and see how far the observed rate sits
  from that distribution. No constant is hard-coded except the seed and the iteration
  count, both from PREREGISTRATION §6.

  A check that fires on far more than a fifth of held-out human novels is not ready,
  whatever its p-value looked like on Arm B. That number is printed next to every row so
  the report cannot quote a threshold without it.

WHAT IT DOES NOT DO
  It does not decide that a feature is a tell. C-dist has no pipeline in it, so nothing here
  can show that a pipeline moved anything. This table is the denominator of that comparison,
  not the comparison.

usage:
    python analysis/cdist.py --features corpus/dist-features [--out corpus/dist-features]
"""

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))


def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The analyzer owns the statistics (quantile definition, robust SD, Spearman) and the
# extractor owns the feature registry. Importing both is the point: a second copy of
# quantile() is free to drift from the one the classification rules use.
an = _load("study_analyze", os.path.join(HERE, "analyze.py"))
feat = an.feat

# Mirrors PREREGISTRATION.md §1. Listed rather than parsed because the pre-registration is
# prose; if §1 changes, this set changes with it in the same commit.
PRIMARY = {
    "lex_ai_terms_per_1k", "syn_chapter_sentlen_spread", "str_coda_share",
}

FAMILY_ORDER = ("lexical", "syntax", "structure", "names")
FP_Z_LIMIT = 2.0


def load(feature_dir, arm="C"):
    books = {}
    names = sorted(n for n in os.listdir(feature_dir) if n.endswith(".json"))
    for name in names:
        with open(os.path.join(feature_dir, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        got, _ = an.infer(rec["book"])
        if got == arm:
            books[rec["book"]] = rec
    return books


def status(name, meta):
    if meta["direction"] == "none":
        return "descriptive"
    if name in PRIMARY:
        return "primary"
    if meta["replication"]:
        return "replication"
    return "secondary"


def null_z(deriv, hold, fp, band, rng, iters=200):
    """How far the holdout rate sits from what a stable band would produce.

    The band comes from one half and is scored on the other, so the reference distribution
    has to include the error in the quantiles, not just in the holdout count. Resampling the
    derivation values gives that with nothing to tune: if the two halves are exchangeable,
    z is centred at zero by construction, and a feature whose halves genuinely differ gets
    a large z.
    """
    if fp is None or len(deriv) < 10 or len(hold) < 10:
        return None
    sims = []
    for _ in range(iters):
        a = [rng.choice(deriv) for _ in range(len(deriv))]
        b = [rng.choice(deriv) for _ in range(len(hold))]
        lo, hi = an.quantile(a, band / 100.0), an.quantile(a, 1 - band / 100.0)
        sims.append(sum(1 for v in b if v < lo or v > hi) / len(b))
    mu = an.med(sims)
    sdd = st.pstdev(sims)
    return (fp - mu) / sdd if sdd else None


def summarise(books, band, rng):
    """Per feature: the human distribution, and a threshold's false-positive rate.

    Deterministic, so the same corpus always yields the same split and the number is
    reproducible.

    The split is on a hash of the book id, NOT on the slot number. Slot numbers were
    assigned round-robin across era-by-genre cells, so alternating on them put most of one
    era in one half - a split confounded with the stratum it is supposed to be blind to.
    Hashing the id breaks that correlation and keeps the split reproducible.
    """
    ids = sorted(books, key=lambda b: hashlib.sha256(b.encode()).hexdigest())
    deriv = ids[::2]
    hold = ids[1::2]
    rows = []
    for name, meta in feat.FEATURES.items():
        xs = [(b, float(books[b]["features"][name])) for b in ids
              if books[b]["features"].get(name) is not None]
        if not xs:
            rows.append({"feature": name, "family": meta["family"],
                         "direction": meta["direction"], "status": status(name, meta),
                         "n": 0})
            continue
        vals = [v for _, v in xs]
        dvals = [float(books[b]["features"][name]) for b in deriv
                 if books[b]["features"].get(name) is not None]
        hvals = [float(books[b]["features"][name]) for b in hold
                 if books[b]["features"].get(name) is not None]
        lo = an.quantile(dvals, band / 100.0) if dvals else None
        hi = an.quantile(dvals, 1 - band / 100.0) if dvals else None
        fp = z = None
        if hvals and lo is not None and hi is not None:
            fp = sum(1 for v in hvals if v < lo or v > hi) / len(hvals)
            z = null_z(dvals, hvals, fp, band, rng)
        words = [float(books[b]["words"]) for b, _ in xs]
        rho = an.spearman(vals, words) if len(vals) > 4 else None
        med = an.med(vals)
        rows.append({
            "feature": name, "family": meta["family"], "direction": meta["direction"],
            "status": status(name, meta), "n": len(vals), "median": med,
            "q25": an.quantile(vals, 0.25), "q75": an.quantile(vals, 0.75),
            "p10": an.quantile(vals, band / 100.0),
            "p90": an.quantile(vals, 1 - band / 100.0),
            "min": min(vals), "max": max(vals), "c_sd": an.robust_sd(vals),
            "fp_holdout": fp, "fp_z": z, "len_rho": rho,
            "len_confounded": bool(rho is not None and abs(rho) >= 0.5),
        })
    return rows, len(ids), len(deriv), len(hold)


def fmt(v, nd=2):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}" if abs(v) < 1000 else f"{v:.0f}"
    return str(v)


def write(rows, outdir, n, nd, nh, band, arms_note):
    path = os.path.join(outdir, "cdist.csv")
    cols = ("feature", "family", "direction", "status", "n", "median", "q25", "q75",
            "p10", "p90", "min", "max", "c_sd", "fp_holdout", "fp_z", "len_rho",
            "len_confounded")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})
    return path


def report(rows, n, nd, nh, band):
    print(f"C-dist: {n} book(s), derivation {nd}, holdout {nh}, band p{band:g}-p{100-band:g}")
    if n < 30:
        print(f"  WARN n={n} is below 30: this cannot set a threshold (REDTEAM.md B1)")
    conf = [r["feature"] for r in rows if r.get("len_confounded")]
    if conf:
        print(f"  {len(conf)} feature(s) length-confounded at |rho| >= 0.5 "
              f"(PREREGISTRATION §6): {', '.join(conf)}")
    for family in FAMILY_ORDER:
        sub = [r for r in rows if r["family"] == family]
        if not sub:
            continue
        print(f"\n{family} ({len(sub)})")
        print(f"  {'feature':<28} {'status':<12} {'n':>4} {'median':>9} {'IQR':>17} "
              f"{'p10..p90':>17} {'fp(20%)':>7}")
        for r in sub:
            if not r.get("n"):
                print(f"  {r['feature']:<28} {r['status']:<12} {0:>4}  unmeasured")
                continue
            iqr = f"{fmt(r['q25'])} .. {fmt(r['q75'])}"
            bandx = f"{fmt(r['p10'])} .. {fmt(r['p90'])}"
            fp = f"{100 * r['fp_holdout']:.0f}%" if r["fp_holdout"] is not None else "-"
            flag = ""
            if r.get("fp_z") is not None and abs(r["fp_z"]) > FP_Z_LIMIT:
                flag = f"  <- unstable band (z={r['fp_z']:+.1f})"
            print(f"  {r['feature']:<28} {r['status']:<12} {r['n']:>4} "
                  f"{fmt(r['median']):>9} {iqr:>17} {bandx:>17} {fp:>7}{flag}")
    ready = [r for r in rows if r.get("fp_z") is not None
             and abs(r["fp_z"]) <= FP_Z_LIMIT]
    print(f"\n{len(ready)}/{sum(1 for r in rows if r.get('n'))} measured feature(s) hold a "
          f"band whose holdout rate matches its own bootstrap null (|z| <= {FP_Z_LIMIT:g})")


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--features", required=True, help="directory of extractor JSON")
    ap.add_argument("--arm", default="C", help="which arm to summarise (default C)")
    ap.add_argument("--out", help="write cdist.csv here (default: beside the features)")
    ap.add_argument("--band", type=float, default=10.0)
    ap.add_argument("--seed", type=int, default=20261030)
    args = ap.parse_args(argv)

    books = load(args.features, args.arm)
    if not books:
        print(f"no Arm {args.arm} books under {args.features}. A baseline computed from "
              f"zero books is a failure, not a pass.")
        return 1
    rows, n, nd, nh = summarise(books, args.band, random.Random(args.seed))
    outdir = args.out or args.features
    os.makedirs(outdir, exist_ok=True)
    path = write(rows, outdir, n, nd, nh, args.band, args.arm)
    report(rows, n, nd, nh, args.band)
    print(f"-> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
