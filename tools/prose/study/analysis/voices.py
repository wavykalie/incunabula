#!/usr/bin/env python3
"""voices.py - the voice-sensitivity arm: is a movement the hand, or voice-ness?

DECISIONS.md §3 files six books: two authored ductuses, each drafted on the same three
premises, each compared with its own UNASSIGNED twin (`B-02V` vs `B-02`). Holding the
pipeline, the premise and the drafting model constant, the per-premise difference is the
voice's reach on that feature. One voice cannot say whether that reach is *this hand* or
*voice-ness in general*; two can:

    voice-ness   both voices move it the same way, by comparable amounts -> any ductus
    hand         opposite directions, or the same direction at very different size
    one-hand     only one voice moves it -> that contract's idiosyncrasy, not generalised
    inert        neither voice moves it -> this row does not respond to a voice at all
    unstable     a voice's three premises disagree in sign; report, do not classify

UNITS
  Every delta is (voice - twin) in units of Arm C's robust SD for that feature, so rows on
  different scales share one table and "clearly different magnitudes" has a meaning. Arm C
  must be in the same feature tree, or no row can be scaled and this exits 2.

WHAT THIS IS NOT
  Not a ranking of the two voices, and not a claim about ductuses in general. Two
  contracts on three premises is a contrast, not a population, and the report says so in
  the body rather than in a footnote.

usage:
    python analysis/voices.py --features DIR [--manifest CSV] [--out DIR]
"""

import argparse
import csv
import importlib.util
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))
EXTRACT = os.path.join(STUDY, "extract", "features.py")

# The suffix is the voice, and the manifest's ductus_id must agree with it (§3). Keyed by
# contract slug rather than by suffix so a third voice would be one line here.
VOICES = (("V", "study-voice-a"), ("W", "study-voice-b"))
VOICE_ID = re.compile(r"^(B)-(\d+)([A-Z]+)$")
TWIN_ID = re.compile(r"^(B)-(\d+)$")


def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


feat = _load("study_features", EXTRACT)
SUFFIX_OF = {slug: suf for suf, slug in VOICES}


# ------------------------------------------------------------------ statistics
def quantile(vals, q):
    xs = sorted(vals)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def robust_sd(vals):
    """IQR/1.349, the same estimator analyze.py uses, so the two tables can be read
    together. Falls back to the sample SD when the IQR collapses."""
    if len(vals) < 2:
        return None
    if len(vals) >= 3:
        iqr = quantile(vals, .75) - quantile(vals, .25)
        if iqr:
            return iqr / 1.349
    return st.stdev(vals)


# ------------------------------------------------------------------ loading
def load(feature_dir):
    books = {}
    for name in sorted(os.listdir(feature_dir)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(feature_dir, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        books[rec["book"]] = rec
    return books


def manifest_ductus(path):
    out = {}
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            bid = (row.get("book_id") or "").strip()
            if bid:
                out[bid] = (row.get("ductus_id") or "").strip()
    return out


def triplets(books):
    """twin id -> {"twin": rec, "V": rec, "W": rec}, for whatever is filed."""
    out = {}
    for bid, rec in books.items():
        m = VOICE_ID.match(bid)
        if m:
            out.setdefault(f"{m.group(1)}-{m.group(2)}", {})[m.group(3)] = rec
        elif TWIN_ID.match(bid):
            out.setdefault(bid, {})["twin"] = rec
    return {k: v for k, v in out.items() if "twin" in v}


# ------------------------------------------------------------------ the verdict
def voice_effect(group, suffix, name, scale):
    """(median signed effect in SDC, sign agreement, n premises) for one voice."""
    deltas = []
    for twin, parts in sorted(group.items()):
        v = parts.get(suffix)
        if not v:
            continue
        tv, vv = parts["twin"]["features"].get(name), v["features"].get(name)
        if tv is None or vv is None:
            continue
        deltas.append((float(vv) - float(tv)) / scale)
    if not deltas:
        return None, None, 0
    eff = st.median(deltas)
    # Disagreement is both directions appearing, not a zero: a voice that leaves a feature
    # exactly where the twin had it has not "failed to agree" with itself, it has not
    # moved the row at all - which is `inert` or `one-hand`, not `unstable`.
    agree = not (any(d > 0 for d in deltas) and any(d < 0 for d in deltas))
    return eff, agree, len(deltas)


def classify(v_eff, w_eff, v_moves, w_moves, v_agree, w_agree, min_move):
    """One verdict per feature, from the two voices' effects.

    A voice "moves" a feature when the median delta clears `min_move` human SDs (the same
    floor analyze.py uses for a residual tell) AND every premise agrees in sign. A voice
    whose premises disagree is reported as such rather than averaged into confidence: with
    three premises, a sign flip is the honest signal that three books cannot decide it.
    """
    unstable = (v_eff is not None and not v_agree) or (w_eff is not None and not w_agree)
    if unstable:
        return "unstable"
    if not v_moves and not w_moves:
        return "inert"
    if v_moves and not w_moves or w_moves and not v_moves:
        return "one-hand"
    ratio = max(abs(v_eff), abs(w_eff)) / max(min(abs(v_eff), abs(w_eff)), 1e-9)
    if (v_eff > 0) != (w_eff > 0):
        return "hand"
    return "voice-ness" if ratio <= 2.0 else "hand"


# ------------------------------------------------------------------ report
def analyse(books, manifest, min_move, min_premises):
    group = triplets(books)
    c_books = [r for bid, r in books.items() if bid.startswith("C-")]
    rows = []
    for name, meta in feat.FEATURES.items():
        c_vals = [r["features"][name] for r in c_books if r["features"].get(name) is not None]
        scale = robust_sd(c_vals) if len(c_vals) >= 3 else None
        if not scale:
            continue
        v_eff, v_agree, v_n = voice_effect(group, "V", name, scale)
        w_eff, w_agree, w_n = voice_effect(group, "W", name, scale)
        if not v_n and not w_n:
            continue
        v_moves = bool(v_n >= min_premises and v_agree and abs(v_eff) >= min_move)
        w_moves = bool(w_n >= min_premises and w_agree and abs(w_eff) >= min_move)
        rows.append({
            "feature": name, "family": meta["family"], "direction": meta["direction"],
            "n_premises": max(v_n, w_n), "scale": scale,
            "v_effect": v_eff, "w_effect": w_eff,
            "v_agree": v_agree, "w_agree": w_agree,
            "verdict": classify(v_eff, w_eff, v_moves, w_moves,
                                v_agree, w_agree, min_move),
        })
    return rows, group


def fmt(v, nd=2):
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    return f"{v:+.{nd}f}" if nd and v != 0 else f"{v:.{nd}f}"


def write_outputs(rows, group, outdir, args):
    os.makedirs(outdir, exist_ok=True)
    slugs = [s for _, s in VOICES]

    with open(os.path.join(outdir, "voices.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["feature", "family", "direction", "n_premises", "twin_sd",
                    "voice_a_effect", "voice_a_signs_agree", "voice_b_effect",
                    "voice_b_signs_agree", "verdict"])
        for r in rows:
            w.writerow([r["feature"], r["family"], r["direction"], r["n_premises"],
                        f"{r['scale']:.6f}", fmt(r["v_effect"], 3), r["v_agree"],
                        fmt(r["w_effect"], 3), r["w_agree"], r["verdict"]])

    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    order = ("voice-ness", "hand", "one-hand", "inert", "unstable")

    lines = []
    add = lines.append
    add("# Voice sensitivity: this hand or a voice at all?\n")
    add(f"Premises with a twin filed: **{len(group)}** of 3. Voices: "
        f"{', '.join(f'`{s}`' for s in slugs)}. Effect floor: **{args.min_move} SDC** "
        f"(the residual-tell floor), minimum premises per voice: {args.min_premises}.\n")
    add("Every number is *voice minus its own UNASSIGNED twin*, in units of Arm C's robust "
        "SD for that feature. Pipeline, premise and model are constant within a pair, so a "
        "difference is the voice.\n")
    add("## Verdicts\n")
    add("| verdict | features |")
    add("|---|---|")
    for v in order:
        add(f"| {v} | {counts.get(v, 0)} |")
    add("")
    add("- **voice-ness** — both contracts move the feature the same way within 2x. Any "
        "ductus probably does this to this row; it is not a property of either hand.")
    add("- **hand** — opposite directions, or the same direction at more than 2x the size. "
        "The contract content is the lever here, so the wording is worth writing "
        "deliberately.")
    add("- **one-hand** — one contract's idiosyncrasy. Reported as such, never generalised.")
    add("- **inert** — neither reaches it. A useful negative: a voice is not a knob for "
        "every row.")
    add("- **unstable** — a voice's three premises disagree in sign. Three books cannot "
        "decide it; the row needs more premises, not a stronger adjective.\n")

    for family in ("lexical", "syntax", "structure", "names"):
        sub = [r for r in rows if r["family"] == family]
        if not sub:
            continue
        add(f"## {family}\n")
        add("| feature | voice-a (SDC) | voice-b (SDC) | signs | verdict |")
        add("|---|---|---|---|---|")
        for r in sub:
            signs = f"{fmt(r['v_effect'], 1)} / {fmt(r['w_effect'], 1)}"
            add(f"| `{r['feature']}` | {fmt(r['v_effect'])} | {fmt(r['w_effect'])} | "
                f"{signs} | {r['verdict']} |")
        add("")

    add("## Limits\n")
    add(f"- Two contracts on {len(group)} premise(s). This is a contrast, not a "
        "population: it can say whether these two voices agree, never what 'a ductus' does "
        "in general (DECISIONS.md §3).")
    add("- A `voice-ness` verdict is an inference from two samples of a category. Three or "
        "more contracts on the same premises is what would turn it into a distribution.")
    add("- The contracts were authored for *reach*, not merit, and each was written to "
        "differ from the pipeline default on axes this study measures. A large effect is an "
        "upper bound on a typical voice, not a typical voice.")
    add("- Features whose Arm C spread is zero are skipped: an effect size needs a scale, "
        "and dividing by noise you invented is the error the residual rule already guards "
        "against.")
    add("- No reader ever rated these books (DECISIONS.md §5). A movement here is a counted "
        "feature, not a judgement that one voice reads better.")

    path = os.path.join(outdir, "voices.md")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines).rstrip() + "\n")
    return path, counts


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--features", required=True, help="directory of extractor JSON")
    ap.add_argument("--manifest", help="manifest.csv (checks ductus_id against the suffix)")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--min-move", type=float, default=0.5,
                    help="effect floor for 'this voice moves the feature', in Arm C SDs")
    ap.add_argument("--min-premises", type=int, default=2,
                    help="premises a voice needs before its effect is reported (default 2)")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.features):
        print(f"no feature directory {args.features}. Nothing measured, nothing written.")
        return 1
    books = load(args.features)
    group = triplets(books)
    labelled = manifest_ductus(args.manifest)
    for twin, parts in sorted(group.items()):
        for suffix, slug in VOICES:
            rec = parts.get(suffix)
            if not rec:
                continue
            want = labelled.get(rec["book"])
            if want and want != slug:
                print(f"  note: {rec['book']} is filed with ductus_id {want!r} but the "
                      f"suffix {suffix!r} means {slug!r}; the suffix decides here, and the "
                      f"manifest row is what the report should carry.")
    if not group:
        print(f"no voice books under {args.features}: expected twins `B-NN` with `B-NNV` "
              f"and `B-NNW` beside them (DECISIONS.md §3). Nothing to compare, so nothing "
              f"written. Run `python run/dispatch.py --plan` first.")
        return 2
    rows, group = analyse(books, args.manifest, args.min_move, args.min_premises)
    if not rows:
        print("no feature could be scaled: Arm C is missing from this feature tree "
              "(fewer than 3 `C-` books). Extract C-dist into the same tree.")
        return 2
    path, counts = write_outputs(rows, group, args.out, args)
    print(f"premises={len(group)}  features={len(rows)}  " +
          " ".join(f"{k}={counts.get(k, 0)}" for k in
                   ("voice-ness", "hand", "one-hand", "inert", "unstable")))
    print(f"-> {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
