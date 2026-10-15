#!/usr/bin/env python3
"""outcome-ledger.py — the load-bearing wall: predictions before publication, falsified after.

WHY THIS EXISTS
  SELF_IMPROVEMENT.md §7 names the loop's only three external signals: the
  deterministic controls, the frozen corpus, and reader outcomes. Everything else
  the loop does is self-consistency, and "a system with no outcome channel does not
  become a better author over time — it becomes a more confident one."

  COMMONPLACE.md already specifies the shape of this (its `outcome` entry type, with
  `predicted` required verbatim) and the 2026-09-30 Hollow Bridge entry records what
  skipping it costs: "no prediction was recorded ... that is the data the loop most
  needs and cannot recover."

  So this tool makes the channel a thing a run DOES rather than a thing a run
  promises, in three moves:
    predict   an index recorded BEFORE publication, with the basis it rested on
    falsify   the actual afterwards, the error, the lesson, and which records move
    report    outstanding predictions, prediction error, and what the outcome moved

  It is the mirror of errata-store.py: that one indexes what the system learned about
  its own instruments — the measurement channel. This one indexes what it learned
  about the world — outcomes, the taste channel's evidence.

WHAT IT WILL NOT DO
  - It never edits COMMONPLACE.md. It appends a formatted block; the rest of the
    author's ledger is byte-identical afterwards, and the append is asserted to be an
    append (the old file is a byte-prefix of the new one, in the self-test).
  - It never invents a mapping from sales to an index. An actual that is not on the
    index's scale is recorded VERBATIM and reported NOT MAPPABLE, because that mapping
    is the author's open decision (the KDP metric set was deferred 2026-10-15), and a
    guessed mapping would launder itself into the fitness number.
  - It never manufactures a prediction after the fact. `falsify` against a book with
    no open prediction is REFUSED — that is exactly the Hollow Bridge case, and the
    whole point is that it cannot be reconstructed.
  - It never moves a PINNED measurement record. Evidence from one channel may never
    move another (§2): a pinned record is cited by the freeze and moves on a named
    corpus, not on how a book sold. Craft records may be credited or debited; that is
    the channel an outcome is allowed to move.
  - It is not a gate. Make-ready class, same as preflight.sh and errata-store.py: it
    reads records, never prose, and no book is judged by it.

STORAGE
  record/outcomes.jsonl   one row per prediction, closed by its outcome
  COMMONPLACE.md          the author's ledger, appended to, never rewritten
  record/errata.jsonl     read and written ONLY for the craft usage counters, through
                          errata-store.py's own value-of and mutation log

usage:  tools/outcome-ledger.py <command> [options]
  predict --book B --first-impression F --standing-type S [--basis TEXT] [--force]
  falsify --book B --actual TEXT [--first-impression-actual N] [--standing-type-actual N]
          [--error TEXT] [--lesson TEXT] [--record ID=win|loss ...]
  report | list | --self-test

EXIT
  0  ok
  1  refused — a rule held, and the refusal names the rule
  2  could not run (bad usage, unreadable record)
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
from datetime import date, datetime

# The delivery gate for First Impression (PROGRAM_MAP §4). Restated here only to be
# reported against; nothing in this tool enforces it.
FIRST_IMPRESSION_GATE = 7.0

USAGE_KEYS = ("applied", "outcome_win", "outcome_loss", "cited")


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rpath(*parts):
    return os.path.join(*parts).replace(os.sep, "/")


def read_raw(path):
    """Raw bytes-as-text. newline="" so an append cannot silently normalise the file."""
    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        return fh.read()


def write_text(path, text):
    """LF always, on every platform. A CR is the byte grep cannot see (KF-005)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def paths(root):
    return {
        "rows": os.path.join(root, "record", "outcomes.jsonl"),
        "commons": os.path.join(root, "COMMONPLACE.md"),
        "store": os.path.join(root, "record", "errata.jsonl"),
        "store_tool": os.path.join(root, "tools", "errata-store.py"),
    }


def load_rows(root):
    p = paths(root)["rows"]
    if not os.path.isfile(p):
        return []
    rows = []
    with open(p, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def save_rows(root, rows):
    write_text(paths(root)["rows"],
               "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))


def _num(text):
    """The index value, or None when it is not a number or not on the 0-10 scale."""
    try:
        v = float(text)
    except (TypeError, ValueError):
        return None
    return v if 0.0 <= v <= 10.0 else None


def _flag(args, name):
    return args[args.index(name) + 1] if name in args else None


def predict_block(row):
    basis = f"\n- **basis:**     {row['basis']}" if row.get("basis") else ""
    return (
        f"### {row['recorded']} — prediction — {row['book']}\n"
        f"- **book:**      {row['book']}\n"
        f"- **predicted:** First Impression {row['first_impression']} · "
        f"Standing Type {row['standing_type']} — recorded before publication\n"
        f"- **gate:**      First Impression >= {FIRST_IMPRESSION_GATE} at delivery"
        f"{basis}\n"
    )


def outcome_block(row):
    predicted = (f"First Impression {row['first_impression']} · "
                 f"Standing Type {row['standing_type']} — recorded "
                 f"{row['recorded']}, before publication")
    return (
        f"### {row['falsified']} — outcome — {row['book']}\n"
        f"- **predicted:** {predicted}\n"
        f"- **actual:**    {row['actual']}\n"
        f"- **error:**     {row['error']}\n"
        f"- **lesson:**    {row['lesson']}\n"
    )


def append_commons(root, block):
    """Append a block. The rest of the ledger comes back byte-identical, asserted."""
    p = paths(root)["commons"]
    before = read_raw(p) if os.path.isfile(p) else ""
    sep = "" if not before or before.endswith("\n\n") else (
        "\n" if before.endswith("\n") else "\n\n")
    after = before + sep + block
    assert after.startswith(before), "append must not rewrite what is already there"
    write_text(p, after)
    return after


def load_store(root):
    """errata-store.py as a module: one value formula, one mutation log, no drift."""
    p = paths(root)["store_tool"]
    if not os.path.isfile(p):
        return None
    spec = importlib.util.spec_from_file_location("errata_store", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def move_records(root, row, credits):
    """Credit or debit the records this outcome is evidence about.

    Returns (moved, refused). A refusal is a rule, not an error: a pinned measurement
    record is cited by the freeze and moves on a named corpus, never on an outcome.
    """
    moved, refused = [], []
    if not credits:
        return moved, refused
    store = load_store(root)
    if store is None:
        return moved, refused + [("(all)", "errata-store.py not found — nothing to move")]
    records = store.load_records(root)
    by_id = {r["id"]: r for r in records}
    touched = False
    for spec in credits:
        rid, _, verdict = spec.partition("=")
        verdict = verdict.strip().lower()
        if verdict not in ("win", "loss"):
            refused.append((rid, f"unknown verdict {verdict!r} — win or loss"))
            continue
        rec = by_id.get(rid)
        if rec is None:
            refused.append((rid, "no such record in the store"))
            continue
        if rec.get("pin"):
            refused.append((rid, "PINNED measurement record: a reader outcome cannot "
                                 "move a measurement (firewall §2) — a corpus does"))
            continue
        before = dict(rec)
        rec.setdefault("usage", {k: 0 for k in USAGE_KEYS})
        rec["usage"]["outcome_" + verdict] = rec["usage"].get("outcome_" + verdict, 0) + 1
        rec["value"] = store.value_of(rec)
        rec["updated"] = date.today().isoformat()
        store.append_mutation(root, "outcome_" + verdict, before, dict(rec),
                              f"{row['book']} {row['falsified']}")
        moved.append((rid, verdict, before.get("value"), rec["value"]))
        touched = True
    if touched:
        store.save_records(root, records)
    return moved, refused


# --- commands --------------------------------------------------------------

def cmd_predict(root, args):
    book = _flag(args, "--book")
    fi = _num(_flag(args, "--first-impression"))
    st = _num(_flag(args, "--standing-type"))
    if not book:
        print("outcome-ledger: --book is required.")
        return 2
    for label, raw, val in (("--first-impression", _flag(args, "--first-impression"), fi),
                            ("--standing-type", _flag(args, "--standing-type"), st)):
        if raw is None:
            print(f"outcome-ledger: {label} is required. A prediction without the index "
                  "it predicts is not a prediction, and the index is the number an "
                  "outcome is falsified against.")
            return 1
        if val is None:
            print(f"outcome-ledger: {label} {raw!r} is not a number on the 0-10 scale.")
            return 1

    rows = load_rows(root)
    open_rows = [r for r in rows if r["book"] == book and r["status"] == "open"]
    closed = [r for r in rows if r["book"] == book and r["status"] == "closed"]
    if closed and "--force" not in args:
        print(f"outcome-ledger: {book} already carries a falsified prediction "
              f"({closed[0]['falsified']}). A prediction recorded after the outcome was "
              "known is not a prediction. Pass --force only to record a genuinely new "
              "cycle (a second edition), and say so in --basis.")
        return 1
    if open_rows and "--force" not in args:
        print(f"outcome-ledger: {book} already has an open prediction recorded "
              f"{open_rows[0]['recorded']}. Falsify it before recording another, or "
              "pass --force to supersede it.")
        return 1
    if open_rows:
        for r in open_rows:
            r["status"] = "superseded"

    today = date.today().isoformat()
    row = {
        "id": f"P-{today}-{book}",
        "book": book,
        "recorded": today,
        "first_impression": fi,
        "standing_type": st,
        "basis": _flag(args, "--basis"),
        "status": "open",
        "actual": None,
        "first_impression_actual": None,
        "standing_type_actual": None,
        "error": None,
        "lesson": None,
        "falsified": None,
        "moved": [],
    }
    body = append_commons(root, predict_block(row))
    rows.append(row)
    save_rows(root, rows)
    print(f"outcome-ledger: prediction recorded for {book}: First Impression {fi}, "
          f"Standing Type {st} — before publication.")
    print(f"  appended to COMMONPLACE.md ({len(body)} bytes on disk). "
          "Falsify it after the outcome lands.")
    return 0


def cmd_falsify(root, args):
    book = _flag(args, "--book")
    actual = _flag(args, "--actual")
    if not book or actual is None:
        print("outcome-ledger: --book and --actual are both required. The actual is "
              "entered verbatim — paraphrase is how evidence becomes flattering.")
        return 2
    rows = load_rows(root)
    open_rows = [r for r in rows if r["book"] == book and r["status"] == "open"]
    if not open_rows:
        known = [r for r in rows if r["book"] == book]
        if known:
            print(f"outcome-ledger: {book}'s prediction was already falsified on "
                  f"{known[0]['falsified']}. This tool does not manufacture a second one.")
        else:
            print(f"outcome-ledger: no prediction was recorded for {book} before "
                  "publication, so there is nothing to falsify. That is the Hollow "
                  "Bridge case (COMMONPLACE.md 2026-09-30): the error cannot be "
                  "recovered after the fact, and inventing one now would be a flattering "
                  "number wearing the name of evidence. Record the next book before "
                  "publication instead.")
        return 1
    row = open_rows[0]

    fa = _flag(args, "--first-impression-actual")
    sa = _flag(args, "--standing-type-actual")
    if fa is None or sa is None:
        error = _flag(args, "--error")
        if error is None:
            error = ("NOT MAPPABLE — the actual is not on the index scale, and the "
                     "metric mapping from sales to the index is the author's open "
                     "decision (deferred 2026-10-15). Recorded verbatim above; no "
                     "error is computed rather than guessed.")
        comparable = False
    else:
        fv, sv = _num(fa), _num(sa)
        if fv is None or sv is None:
            print("outcome-ledger: --first-impression-actual / --standing-type-actual "
                  "must be numbers on the 0-10 scale to compute an error.")
            return 1
        comparable = True
        ef, es = fv - row["first_impression"], sv - row["standing_type"]
        row["first_impression_actual"], row["standing_type_actual"] = fv, sv
        error = _flag(args, "--error") or (
            f"First Impression {row['first_impression']} predicted, {fv} actual "
            f"({ef:+.2f}); Standing Type {row['standing_type']} predicted, {sv} actual "
            f"({es:+.2f}); mean |error| {round((abs(ef) + abs(es)) / 2, 2)}")
    row["comparable"] = comparable
    row["error"] = error
    row["actual"] = actual
    row["lesson"] = _flag(args, "--lesson") or "none yet"
    row["falsified"] = date.today().isoformat()
    row["status"] = "closed"

    moved, refused = move_records(root, row, [a for a in args if "=" in a and not a.startswith("--")])
    row["moved"] = [{"id": i, "verdict": v, "value_before": b, "value_after": a}
                    for i, v, b, a in moved]

    append_commons(root, outcome_block(row))
    save_rows(root, rows)

    print(f"outcome-ledger: outcome recorded for {book}.")
    print(f"  error: {error}")
    for rid, verdict, before_v, after_v in moved:
        print(f"  moved {rid}: {verdict}, value {before_v} -> {after_v}")
    for rid, why in refused:
        print(f"  refused {rid}: {why}")
    if not comparable:
        print("  this outcome does not move the fitness signal: no comparable actual. "
              "Name the mapping in --error once the metric set is decided.")
    return 0


def cmd_list(root, args):
    rows = load_rows(root)
    if not rows:
        print("outcome-ledger: no predictions recorded. A book that ships without one "
              "is the 2026-09-30 entry repeating.")
        return 0
    for r in rows:
        if r["status"] == "open":
            print(f"  OPEN      {r['book']:24} FI {r['first_impression']} · ST "
                  f"{r['standing_type']}  recorded {r['recorded']}")
        elif r["status"] == "closed":
            print(f"  closed    {r['book']:24} falsified {r['falsified']}"
                  f"  mappable={r.get('comparable')}")
        else:
            print(f"  {r['status']:9} {r['book']:24} superseded by a later prediction")
    return 0


def cmd_report(root, args):
    rows = load_rows(root)
    open_rows = [r for r in rows if r["status"] == "open"]
    closed = [r for r in rows if r["status"] == "closed"]
    mappable = [r for r in closed if r.get("comparable")]
    print("outcome-ledger — prediction error is the fitness signal")
    print(f"  predictions recorded: {len(rows)}  (open {len(open_rows)}, "
          f"closed {len(closed)}, superseded "
          f"{len([r for r in rows if r['status'] == 'superseded'])})")
    for r in open_rows:
        try:
            age = (date.today() - datetime.strptime(r["recorded"], "%Y-%m-%d").date()).days
        except ValueError:
            age = 0
        print(f"    open {age:4}d  {r['book']:24} FI {r['first_impression']} · "
              f"ST {r['standing_type']}")
    if closed:
        print(f"  falsified: {len(closed)}  mappable: {len(mappable)}  "
              f"not mappable: {len(closed) - len(mappable)}")
    if mappable:
        errs = []
        for r in mappable:
            errs.append(abs(r["first_impression_actual"] - r["first_impression"]))
            errs.append(abs(r["standing_type_actual"] - r["standing_type"]))
        print(f"  mean |error| across {len(errs)} index claims: "
              f"{round(sum(errs) / len(errs), 2)}")
    else:
        print("  mean |error|: NOT COMPUTED — no falsified prediction carries an actual "
              "on the index scale yet.")
    moved = [(m, r["book"]) for r in rows for m in r.get("moved") or []]
    if moved:
        print(f"  records moved by an outcome: {len(moved)}")
        for m, book in moved:
            print(f"    {m['id']} {m['verdict']} ({book}) "
                  f"value {m['value_before']} -> {m['value_after']}")
    else:
        print("  records moved by an outcome: 0 — the store's usage counters are still "
              "at zero, which is why its confidence bands are labelled a prototype.")
    print("  A loop whose predictions get sharper is learning about the world; a loop "
          "whose scores get higher is learning about itself.")
    return 0


# --- self-test -------------------------------------------------------------

def selftest():
    checks = []

    def ok(cond, label):
        checks.append((bool(cond), label))

    tmp = tempfile.mkdtemp(prefix="outcome-ledger-")
    try:
        os.makedirs(os.path.join(tmp, "record"))
        os.makedirs(os.path.join(tmp, "tools"))
        shutil.copy(os.path.join(repo_root(), "tools", "errata-store.py"),
                    os.path.join(tmp, "tools", "errata-store.py"))
        write_text(paths(tmp)["commons"],
                   "# COMMONPLACE — the taste ledger\n\n## Seeded from the record so far\n\n"
                   "### 2026-09-30 — outcome — Hollow Bridge: no prediction was recorded\n"
                   "- **predicted:** none.\n")
        store = {"id": "E-2026-01-01-001", "created": "2026-01-01", "updated": "2026-01-01",
                 "class": "craft", "target": "quoin (process)", "title": "a craft note",
                 "body": "b", "source": {"file": "ERRATA.md", "line": 1, "commit": "T"},
                 "state": "observed", "n": 1, "evidence": "e", "motive": "aesthetic",
                 "usage": {k: 0 for k in USAGE_KEYS}, "status": "active", "pin": [],
                 "expiry": None, "merged_from": [], "superseded_by": None,
                 "tombstone": None, "confidence": 0.35, "value": 0.35}
        pinned = dict(store, id="E-2026-01-02-001", class_="measurement",
                      target="U4", pin=["measurement-ledger"], title="a pinned measurement")
        write_text(paths(tmp)["store"],
                   "".join(json.dumps(r, sort_keys=True) + "\n" for r in (store, pinned)))

        # 1-2. a prediction must carry the indices it will be falsified against
        ok(cmd_predict(tmp, ["--book", "x"]) == 1, "predict: an index-less prediction is refused")
        ok(cmd_predict(tmp, ["--book", "x", "--first-impression", "eleven",
                             "--standing-type", "5"]) == 1,
           "predict: an index off the 0-10 scale is refused")

        # 3. a real prediction appends and the old file stays a byte-prefix
        before = read_raw(paths(tmp)["commons"])
        rc = cmd_predict(tmp, ["--book", "grand-standing", "--first-impression", "7.4",
                               "--standing-type", "5.1", "--basis", "two blind readers"])
        after = read_raw(paths(tmp)["commons"])
        ok(rc == 0, "predict: a well-formed prediction is recorded")
        ok(after.startswith(before) and after.count("\n### ") > before.count("\n### "),
           "predict: COMMONPLACE.md gains a block and keeps every byte it had")
        ok("\r" not in after, "predict: nothing written carries a CR (KF-005)")
        ok("First Impression 7.4" in after and "Standing Type 5.1" in after,
           "predict: the prediction is verbatim in the ledger")

        # 4. a second open prediction for the same book is refused, then superseded
        ok(cmd_predict(tmp, ["--book", "grand-standing", "--first-impression", "9",
                             "--standing-type", "9"]) == 1,
           "predict: a second open prediction for one book is refused")
        ok(cmd_predict(tmp, ["--book", "grand-standing", "--first-impression", "8.0",
                             "--standing-type", "5.5", "--force", "--basis", "superseding"]) == 0,
           "predict: --force records a revised prediction")
        superseded = [r for r in load_rows(tmp) if r["status"] == "superseded"]
        ok(len(superseded) == 1, "predict: the superseded prediction is kept, not dropped")

        # 5. falsifying a book with no prediction is refused (Hollow Bridge)
        ok(cmd_falsify(tmp, ["--book", "hollow-bridge", "--actual", "12 copies"]) == 1,
           "falsify: a book with no prior prediction is refused, not back-filled")

        # 6. an uncomparable actual is recorded verbatim and NOT MAPPABLE
        rc = cmd_falsify(tmp, ["--book", "grand-standing", "--actual",
                               "sold 340 in year one; one 1-star review, verbatim: 'thin'",
                               "--lesson", "the premise read as hollow"])
        rows = load_rows(tmp)
        row = [r for r in rows if r["status"] == "closed"][0]
        ok(rc == 0 and row["actual"].startswith("sold 340") and row["comparable"] is False,
           "falsify: an off-scale actual is kept verbatim and marked not mappable")
        ok("NOT MAPPABLE" in row["error"],
           "falsify: no error is invented when the actual is off the index scale")

        # 7-8. the outcome moves craft records and is refused on pinned ones
        write_text(paths(tmp)["store"],
                   "".join(json.dumps(r, sort_keys=True) + "\n" for r in (store, pinned)))
        ok(cmd_predict(tmp, ["--book", "second-book", "--first-impression", "7.1",
                             "--standing-type", "5.0"]) == 0, "predict: a second book records")
        ok(cmd_falsify(tmp, ["--book", "second-book", "--actual", "actual verbatim",
                             "--first-impression-actual", "6.2",
                             "--standing-type-actual", "5.4",
                             "E-2026-01-01-001=win", "E-2026-01-02-001=loss"]) == 0,
           "falsify: a mappable outcome is recorded")
        row2 = [r for r in load_rows(tmp) if r["book"] == "second-book"][0]
        ok("mean |error| 0.65" in row2["error"],
           f"falsify: the error is computed against both indices ({row2['error'][-24:]})")
        ok([m["id"] for m in row2["moved"]] == ["E-2026-01-01-001"],
           "falsify: only the craft record moved")
        store_now = {json.loads(l)["id"]: json.loads(l)
                     for l in read_raw(paths(tmp)["store"]).splitlines() if l.strip()}
        ok(store_now["E-2026-01-01-001"]["usage"]["outcome_win"] == 1
           and store_now["E-2026-01-01-001"]["value"] > 0.35,
           "falsify: outcome_win raises the craft record's value")
        ok(store_now["E-2026-01-02-001"]["usage"]["outcome_loss"] == 0,
           "falsify: a PINNED measurement record is not moved by an outcome (firewall §2)")

        ok(cmd_report(tmp, []) == 0, "report: runs and exits 0")
        ok(cmd_list(tmp, []) == 0, "list: runs and exits 0")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [label for good, label in checks if not good]
    for good, label in checks:
        print(("  ok    " if good else "  FAIL  ") + label)
    print("-" * 67)
    if failed:
        print(f"SELF-TEST FAILURE — {len(failed)} of {len(checks)} assertions failed.")
        return 1
    print(f"SELF-TEST PASS — {len(checks)} assertions (predict, supersede, falsify-verbatim, "
          "error, firewall, append-only, report).")
    return 0


# --- main ------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    root = repo_root()
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1]
        del args[i:i + 2]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2
    cmd, rest = args[0], args[1:]
    if cmd in ("selftest", "--self-test"):
        return selftest()
    table = {"predict": cmd_predict, "falsify": cmd_falsify,
             "report": cmd_report, "list": cmd_list}
    if cmd not in table:
        print(f"outcome-ledger: unknown command {cmd}")
        return 2
    return table[cmd](root, rest)


if __name__ == "__main__":
    sys.exit(main())
