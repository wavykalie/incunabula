#!/usr/bin/env python3
"""preflight.py - the study's make-ready check: one command before each session.

Three things have to still be true when a session starts, and none of them is visible by
looking at the directory listing:

  frozen premises   the twenty (and the three long-form) still match their .sha256
                    sidecars, each frozen `text` is still the render of its five fields,
                    and the pool digest recorded inside the frozen file still matches the
                    pool on disk. A premise edited after the freeze turns every pair in
                    this run into a comparison of two different inputs (design §6).
  the plan          RUNPLAN.csv, the payload files and the dispatch cards agree with each
                    other, and every payload is a byte-for-byte reproduction of a frozen
                    premise: the §3 wrapper around it for Arm A, the bare text for Arm B.
                    The plan IS the prompt record, so a payload that drifted means the
                    log would describe something that was never sent.
  the probe record  run/harness.json is filled from A-01's first call, so every row can
                    say which model actually wrote and what sampling was actually applied.

WHY THE ROWS CARRY DIFFERENT STATES
  A check that has never been seen to fail is not yet known to work, so PASS, FAIL,
  NOT MEASURED and SKIP are reported as different things and none stands in for another.
  An unfilled probe record is NOT MEASURED: dispatch can continue, no row can be filed,
  and the exit code says so instead of reporting a pass over an unmeasured route.

  The frozen-file and payload rows are the ones that must be seen to fail, and they can:
  flip one byte in a payload and row `payloads` FAILs naming the book; flip one byte in a
  frozen premise and its sidecar row FAILs. Both are exercised in the negative test.

WHAT IT DOES NOT DO
  It calls no model, touches no prose, and does not run selftest.py - that is the slower
  proof that the harness works; this is the fast proof that its inputs are the ones the
  run will claim. It writes nothing, so it is safe before every session.

usage:
    python preflight.py [--out run/out] [--frozen premises/frozen] [--harness PATH]

exit:
    0  READY         every row PASS
    1  FAIL          a frozen input, the plan or a payload disagrees with the record
    2  NOT READY     nothing is broken, but something is not a measurement yet
    3  COULD NOT RUN the premises are missing, so there is nothing to verify against
"""

import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "run")
ROWS = []


# ------------------------------------------------------------------ helpers
def rel(path):
    try:
        return os.path.relpath(path, HERE).replace("\\", "/")
    except ValueError:
        return path


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def load_tool(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def row(name, status, detail=""):
    ROWS.append((name, status, detail))
    print(f"  {name:<26} {status:<13} {detail}")


# ------------------------------------------------------------------ frozen premises
def frozen_block(path, label, premise_mod):
    """One frozen file: sidecar, per-premise render, and the pool it came from."""
    side = path + ".sha256"
    if not os.path.exists(path) or not os.path.exists(side):
        row(label, "FAIL", f"missing {rel(path)} or its .sha256 - nothing to verify")
        return None
    with open(side, encoding="utf-8") as fh:
        want = fh.read().split()[0]
    got = sha256_file(path)
    if got != want:
        row(label, "FAIL", f"MISMATCH: recorded {want[:16]}... actual {got[:16]}... "
                           f"- a changed premise is a protocol deviation, not an edit")
        return None
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    premises = doc.get("premises") or []
    bad = []
    for p in premises:
        if premise_mod.render(p) != p.get("text"):
            bad.append(f"{p.get('id')}: text is not the render of its fields")
        elif premise_mod.words(p["text"]) != p.get("words"):
            bad.append(f"{p.get('id')}: recorded {p.get('words')}w, text is "
                       f"{premise_mod.words(p['text'])}w")
    pool = os.path.join(HERE, "premises", "candidates.json")
    if os.path.exists(pool) and doc.get("pool_sha256"):
        if sha256_file(pool) != doc["pool_sha256"]:
            bad.append("the pool changed after this freeze (pool_sha256 no longer matches)")
    if bad:
        row(label, "FAIL", f"sha256 ok but {len(bad)} internal problem(s): " + "; ".join(bad[:3]))
        return doc
    row(label, "PASS", f"{len(premises)} premises, sha256 {got[:16]}...")
    return doc


def pool_row(v1_path, doc2):
    """v2 is drawn from what v1 did not take: check that claim, not just its hash."""
    if not doc2:
        row("long-form linkage", "SKIP", "no long-form file, so there is no linkage to check")
        return
    want = doc2.get("excluded_by_sha256")
    if not want:
        row("long-form linkage", "FAIL", "premises-v2 records no excluded_by_sha256; the "
                                         "stratum's no-overlap claim is unverifiable")
        return
    got = sha256_file(v1_path)
    if got != want:
        row("long-form linkage", "FAIL", f"v2 was drawn against {want[:16]}..., but v1 is "
                                         f"{got[:16]}... - the long stratum may now share "
                                         f"premises with the primary twenty")
        return
    row("long-form linkage", "PASS", "v2 excluded the twenty that v1 took")


# ------------------------------------------------------------------ the plan
def plan_block(out, frozen_map, want_counts, dispatch):
    csvp = os.path.join(out, "RUNPLAN.csv")
    if not os.path.exists(csvp):
        row("RUNPLAN.csv", "NOT MEASURED",
            f"no plan at {rel(csvp)}; run `python run/dispatch.py --plan`")
        return []
    with open(csvp, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        row("RUNPLAN.csv", "FAIL", "the plan exists but holds no rows")
        return []
    counts = dict(Counter(r.get("stratum", "") for r in rows))
    if counts != want_counts:
        row("RUNPLAN.csv", "FAIL", f"{len(rows)} rows with strata {counts}; the frozen "
                                   f"premises imply {want_counts}")
    else:
        total = sum(int(r["target_words"]) for r in rows)
        comp = "  ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        row("RUNPLAN.csv", "PASS", f"{len(rows)} books ({comp}), {total:,} target words")

    bad, no_card = [], []
    for r in rows:
        bid = r.get("book_id") or "?"
        p = os.path.join(out, r.get("payload_path") or "")
        if not r.get("payload_path") or not os.path.exists(p):
            bad.append(f"{bid}: payload file missing")
            continue
        with open(p, "rb") as fh:
            blob = fh.read()
        if hashlib.sha256(blob).hexdigest() != r.get("payload_sha256", ""):
            bad.append(f"{bid}: digest differs from RUNPLAN.csv")
            continue
        prem = frozen_map.get(r.get("premise_id", ""))
        if prem is None:
            bad.append(f"{bid}: premise {r.get('premise_id')!r} is in no frozen file")
            continue
        want = (dispatch.WRAPPER.format(words=int(r["target_words"]), text=prem["text"])
                if r.get("arm") == "A" else prem["text"])
        try:
            got = blob.decode("utf-8")
        except UnicodeDecodeError:
            bad.append(f"{bid}: payload is not UTF-8")
            continue
        if got != want:
            bad.append(f"{bid}: payload is not the frozen premise text")
        if not os.path.exists(os.path.join(out, "briefs", f"{bid}.md")):
            no_card.append(bid)

    if bad:
        row("payloads", "FAIL", f"{len(bad)} of {len(rows)} disagree: " + "; ".join(bad[:4]))
    else:
        row("payloads", "PASS", f"{len(rows)}/{len(rows)} digests match and reproduce the "
                                f"frozen premise text")
    if no_card:
        row("cards", "FAIL", f"{len(no_card)} missing: {', '.join(no_card[:5])}")
    else:
        extra = []
        briefs = os.path.join(out, "briefs")
        if os.path.isdir(briefs):
            have = {n for n in os.listdir(briefs) if n.endswith(".md")}
            extra = sorted(have - {f"{r['book_id']}.md" for r in rows})
        row("cards", "PASS", f"{len(rows)} dispatch cards" +
            (f" (plus {len(extra)} stale: {', '.join(extra[:3])})" if extra else ""))
    return rows


# ------------------------------------------------------------------ the probe record
def probe_block(path, harness):
    if not os.path.exists(path):
        row("probe record", "NOT MEASURED",
            f"no record at {rel(path)}; run `python run/harness.py --init` on A-01's "
            f"first call")
        return
    with open(path, encoding="utf-8") as fh:
        rec = json.load(fh)
    errs = harness.errors(rec)
    if errs:
        row("probe record", "NOT MEASURED",
            f"{len(errs)} blank(s), so no row can be filed: " + "; ".join(errs[:2]) +
            ("; ..." if len(errs) > 2 else ""))
        return
    bits = []
    for key, label in harness.SAMPLING:
        blk = rec.get(key) or {}
        bits.append(f"{label}={'set' if blk.get('settable') else str(blk.get('applied'))}")
    row("probe record", "PASS",
        f"{rec.get('model_returned')} from {rec.get('version_source')}; " + ", ".join(bits))


# ------------------------------------------------------------------ main
def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=os.path.join(RUN, "out"),
                    help="run directory: RUNPLAN.csv, briefs/, payloads/")
    ap.add_argument("--frozen", default=os.path.join(HERE, "premises", "frozen"))
    ap.add_argument("--harness", default=os.environ.get("STUDY_HARNESS")
                    or os.path.join(RUN, "harness.json"),
                    help="probe record (default run/harness.json, or $STUDY_HARNESS)")
    args = ap.parse_args(argv)

    v1_path = os.path.join(args.frozen, "premises-v1.json")
    v2_path = os.path.join(args.frozen, "premises-v2.json")
    if not os.path.exists(v1_path):
        print(f"no frozen premises at {rel(v1_path)} - there is nothing to verify "
              f"against. Exit 3.")
        return 3

    try:
        premise_mod = load_tool("premise", os.path.join(HERE, "premises", "premise.py"))
        dispatch = load_tool("dispatch", os.path.join(RUN, "dispatch.py"))
        harness = load_tool("harness", os.path.join(RUN, "harness.py"))
    except Exception as exc:                      # noqa: BLE001 - any import failure is fatal
        print(f"could not load the study's own tools: {exc}. Exit 3.")
        return 3

    print("preflight - the study's frozen inputs, plan and probe record")
    print(f"study: {HERE}")
    print()

    print("1. frozen premises")
    doc1 = frozen_block(v1_path, "premises-v1", premise_mod)
    doc2 = frozen_block(v2_path, "premises-v2", premise_mod) if os.path.exists(v2_path) \
        else None
    if doc2 is None:
        row("premises-v2", "SKIP", "not frozen; the long-form stratum is not planned either")
    pool_row(v1_path, doc2)

    frozen_map = {}
    if doc1:
        frozen_map.update({p["id"]: p for p in doc1["premises"]})
    if doc2:
        frozen_map.update({p["id"]: p for p in doc2["premises"]})

    print()
    print("2. the plan")
    want = {}
    if doc1:
        want["primary"] = 2 * len(doc1["premises"])
        want["voice"] = len(dispatch.VOICE_PREMISES) * len(dispatch.VOICES)
    if doc2:
        want["long"] = 2 * len(doc2["premises"])
    plan_block(args.out, frozen_map, want, dispatch)

    print()
    print("3. the probe record")
    probe_block(args.harness, harness)

    fails = [r for r in ROWS if r[1] == "FAIL"]
    unmeasured = [r for r in ROWS if r[1] == "NOT MEASURED"]
    skipped = [r for r in ROWS if r[1] == "SKIP"]
    print()
    if fails:
        print(f"VERDICT: FAIL - {len(fails)} row(s) disagree with the record. Do not "
              f"dispatch: the plan or a frozen input is not what the run would claim.")
        return 1
    if unmeasured:
        names = ", ".join(r[0] for r in unmeasured)
        print(f"VERDICT: NOT READY - nothing is broken, but not measured yet: {names}. "
              f"Dispatch can continue; no row can be filed until that record is filled.")
        return 2
    tail = f" ({len(skipped)} row(s) SKIPPED, named above)" if skipped else ""
    print(f"VERDICT: READY - frozen inputs, plan digests and probe record are all what "
          f"the run will claim{tail}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
