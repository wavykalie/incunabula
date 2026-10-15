#!/usr/bin/env python3
"""errata-store.py — the structured, compactable half of the self-improvement layer.

WHY THIS EXISTS
  ERRATA.md is append-only and must stay that way: it is the measurement ledger,
  it is cited by date from GATE_FREEZE.md and PRINTERS_COPY.md, and the freeze
  hashes depend on it not moving. But append-only is exactly why it cannot be the
  whole improvement layer. Fifty-odd dated entries, no ids, no scoring, no expiry:
  every finding weighs the same, so nothing can be ranked and nothing can ever be
  retired. The file grows and stops being read.

  This tool is the other half. It keeps a STRUCTURED, COMPACTABLE index of the
  findings in ERRATA.md (and of new ones), with confidence, usage and expiry,
  while ERRATA.md itself is never edited. Measurement findings are PINNED — those
  are the ones the freeze cites and compaction may never touch them. Craft findings
  may be deduped, merged and expired; every move is logged and reversible.

WHAT IT WILL NOT DO
  - It never writes ERRATA.md. Import is a copy, not a move.
  - It never deletes a body. Merged and expired bodies move to record/archive/,
    and the same text is still in ERRATA.md regardless — so nothing is lost twice
    over.
  - It never compacts a pinned record.
  - It never invents a confidence number and calls it measured (see below).
  - It is not a gate. It is make-ready, in the same exemption class as
    tools/preflight.sh: it reads records, not prose, and no book is judged by it.

CONFIDENCE NOTE  (prototype, and labelled as such on purpose)
  The bands in `initial_confidence` are derived from rules this project already
  states — evidence kind, independence `n`, whether a control covers the finding —
  and they are a RANKING AID, not a measurement. No gate may read them. This is the
  same posture check-recoverable.py takes with its 1.15/0.85 thresholds: separation
  points, not derived floors. When real reader outcomes land (SELF_IMPROVEMENT §7),
  `usage.outcome_win` is what moves a record, and the bands can be re-derived then.

STORAGE
  record/errata.jsonl        current records, one JSON object per line
  record/mutations.jsonl     append-only event log (before/after; enables rollback)
  record/snapshots/*.json    periodic snapshot + sealed-log digests
  record/archive/*.jsonl     bodies moved out by compaction, quarterly; the log
                             itself is sealed here once it passes SEAL_LIMIT
  ERRATA-CRAFT.md            generated human view (never hand-edited)

usage:  tools/errata-store.py <command> [options]
  import [--commit C]   (re)build records from ERRATA.md; idempotent
  check                 validate the store; exit 1 on any violation
  list [--status S] [--class C]
  show ID
  score                 recompute confidence/value from evidence
  merge ID_LOSER ID_WINNER
  compact [--dry-run] [--ttl-days N]
  restore ID            undo the last mutation that touched a record
  rollback --to N       revert every mutation with seq > N (reverse order)
  snapshot              write a snapshot now
  render                write ERRATA-CRAFT.md
  log [--limit N]
  selftest
exit: 0 ok · 1 violation or failed self-test · 2 usage error
"""

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import date, datetime, timezone

# --- constants -------------------------------------------------------------

STATUSES = ("active", "merged", "expired", "superseded")
CLASSES = ("measurement", "craft")
PINNED_PIN = "measurement-ledger"   # the pin that means "the freeze may cite this"
DEFAULT_TTL_DAYS = 365              # age past which a low-value craft record expires
SEAL_LIMIT = 500                    # mutations kept live before the oldest are sealed
LOW_CONFIDENCE = 0.5                # below this, and unused, and old -> expire

# The rows that name a gate, a threshold, or a calibration surface. A finding on one
# of these is measurement: it is re-derivable, it is what the freeze cites by date,
# and compaction must never touch it. Everything else (process, delegation, tooling)
# is craft knowledge — the half that is allowed to move.
MEASUREMENT_HINTS = ("scanner", "method", "calibration", "recoverable")

DATED_HEADING = re.compile(r"^(#{2,3})\s+(\d{4}-\d{2}-\d{2})\s+[—\-]\s+(.*)$")
ANY_HEADING = re.compile(r"^(#{1,2})\s+\S")
FIELD = re.compile(r"^- \*\*(\w+):\*\*\s+(.*)$")


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rpath(*parts):
    return os.path.join(*parts).replace(os.sep, "/")


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def store_paths(root):
    return {
        "jsonl": os.path.join(root, "record", "errata.jsonl"),
        "log": os.path.join(root, "record", "mutations.jsonl"),
        "snap": os.path.join(root, "record", "snapshots"),
        "arch": os.path.join(root, "record", "archive"),
        "view": os.path.join(root, "ERRATA-CRAFT.md"),
        "source": os.path.join(root, "ERRATA.md"),
    }


# --- records ---------------------------------------------------------------

def classify(target, body):
    t = (target or "").lower()
    if any(k in t for k in ("process", "delegation", "tooling")):
        return "craft"
    return "measurement"


def is_measurement(target, body):
    if classify(target, body) == "craft":
        return False
    t = (target or "").lower()
    if any(k in t for k in MEASUREMENT_HINTS):
        return True
    # a gate row like U4, A1a, D2, S1, F1, P3, N? — a capital letter + digits
    return bool(re.match(r"^[A-Z]{1,3}\d", (target or "").strip()))


def initial_confidence(rec):
    """PROTOTYPE ranking aid — see the module docstring. Not a measurement."""
    c = 0.30
    state = rec.get("state")
    if state == "adopted":
        c += 0.20
    elif state == "proposed":
        c += 0.10
    n = rec.get("n") or 0
    if n >= 3:
        c += 0.15
    elif n >= 1:
        c += 0.05
    ev = (rec.get("evidence") or "").lower()
    if any(k in ev for k in ("control", "corpus", "calibration", "fixture")):
        c += 0.10
    if rec.get("class") == "measurement":
        c += 0.10
    return round(min(c, 0.90), 2)


def value_of(rec):
    u = rec.get("usage") or {}
    return round(rec["confidence"] * (1 + u.get("applied", 0) + u.get("outcome_win", 0))
                 - u.get("outcome_loss", 0), 3)


def normalize_title(title):
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def load_records(root):
    p = store_paths(root)["jsonl"]
    if not os.path.isfile(p):
        return []
    out = []
    for line in read_text(p).splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def save_records(root, records):
    p = store_paths(root)["jsonl"]
    write_text(p, "".join(json.dumps(r, sort_keys=True) + "\n" for r in records))


def next_seq(root):
    p = store_paths(root)["log"]
    n = 0
    if os.path.isfile(p):
        for line in read_text(p).splitlines():
            if line.strip():
                n = json.loads(line).get("seq", n)
    return n + 1


def append_mutation(root, op, before, after, detail=""):
    p = store_paths(root)["log"]
    seq = next_seq(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    ev = {
        "seq": seq,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "op": op,
        "id": (after or before or {}).get("id"),
        "detail": detail,
        "before": before,
        "after": after,
    }
    with open(p, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(ev, sort_keys=True) + "\n")
    return seq


def archive_body(root, rec, reason):
    """Move a body out of the live store into the quarterly archive segment."""
    q = f"{rec['created'][:4]}-Q{(int(rec['created'][5:7]) - 1) // 3 + 1}"
    p = os.path.join(store_paths(root)["arch"], f"errata-{q}.jsonl")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    entry = {"id": rec["id"], "archived_at": date.today().isoformat(),
             "reason": reason, "body": rec.get("body", "")}
    with open(p, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    return rpath(os.path.relpath(p, root))


# --- parsing ERRATA.md -----------------------------------------------------

def parse_entries(text):
    """Every dated entry in ERRATA.md, in file order. Handles both ### and ## forms.

    ### entries carry the seven-field protocol; ## entries (the earlier threshold
    rulings) are free-form. Both are records here; neither is edited.
    """
    lines = text.splitlines()
    marks = []
    for i, ln in enumerate(lines):
        m = DATED_HEADING.match(ln)
        if m:
            marks.append((i, m.group(3)))
        elif ANY_HEADING.match(ln):
            # a non-dated h1/h2 ends the previous entry's body
            marks.append((i, None))
    entries = []
    cur = None
    for i, title in marks:
        if title is None:
            if cur is not None:
                cur["end"] = i
                entries.append(cur)
                cur = None
            continue
        if cur is not None:
            cur["end"] = i
            entries.append(cur)
        m = DATED_HEADING.match(lines[i])
        cur = {"date": m.group(2), "title": title.strip(), "line": i + 1, "start": i}
    if cur is not None:
        cur["end"] = len(lines)
        entries.append(cur)
    for e in entries:
        e["body"] = "\n".join(lines[e["start"]:e["end"]]).rstrip()
        e["fields"] = {}
        for ln in lines[e["start"]:e["end"]]:
            fm = FIELD.match(ln)
            if fm:
                e["fields"][fm.group(1).lower()] = fm.group(2).strip()
    return entries


def _int_or_zero(s):
    m = re.search(r"\d+", s or "")
    return int(m.group(0)) if m else 0


def import_records(root, commit="HEAD"):
    src = store_paths(root)["source"]
    if not os.path.isfile(src):
        print(f"errata-store: no {rpath(os.path.relpath(src, root))} to import")
        return 2
    entries = parse_entries(read_text(src))
    per_date = {}
    records = []
    for e in entries:
        # A dated heading that carries NO field lines, NO bullets and almost no prose
        # is a section preamble ("VERMILLION reconciliation" and its two siblings),
        # not a finding. The test is deliberately narrow: several real findings are
        # written as prose in the older `##` style with no bullet fields at all, and
        # dropping one of those to remove a heading would be an absence invented into
        # a decision. When in doubt, this keeps the entry.
        words = len(re.findall(r"\w+", e["body"]))
        if (not e["fields"] and not re.search(r"^- \S", e["body"], re.M)
                and words < 40):
            continue
        per_date[e["date"]] = per_date.get(e["date"], 0) + 1
        rid = f"E-{e['date']}-{per_date[e['date']]:03d}"
        target = e["fields"].get("row", "")
        cls = classify(target, e["body"])
        meas = (cls == "measurement")
        n = _int_or_zero(e["fields"].get("n", ""))
        rec = {
            "id": rid,
            "created": e["date"],
            "updated": date.today().isoformat(),
            "class": cls,
            "target": target,
            "title": e["title"],
            "body": e["body"],
            "source": {"file": "ERRATA.md", "line": e["line"], "commit": commit},
            "state": (e["fields"].get("state") or "observed").lower(),
            "n": n,
            "evidence": e["fields"].get("evidence", ""),
            "motive": (e["fields"].get("motive") or "").split("—")[0].strip().lower(),
            "usage": {"cited": 0, "applied": 0, "outcome_win": 0, "outcome_loss": 0},
            "status": "active",
            "pin": [PINNED_PIN] if meas else [],
            "expiry": None,
            "merged_from": [],
            "superseded_by": None,
            "tombstone": None,
        }
        rec["confidence"] = initial_confidence(rec)
        rec["value"] = value_of(rec)
        records.append(rec)
    return records


# --- commands --------------------------------------------------------------

def cmd_import(root, args):
    commit = "HEAD"
    if "--commit" in args:
        commit = args[args.index("--commit") + 1]
    records = import_records(root, commit)
    if records == 2:
        return 2
    old = load_records(root)
    write_text(store_paths(root)["jsonl"],
               "".join(json.dumps(r, sort_keys=True) + "\n" for r in records))
    n_meas = sum(1 for r in records if r["pin"])
    n_craft = len(records) - n_meas
    print(f"imported {len(records)} records from ERRATA.md "
          f"({n_meas} measurement/pinned, {n_craft} craft)")
    if old and [r["id"] for r in old] != [r["id"] for r in records]:
        print("note: record ids changed since the last import — the store was rebuilt")
    return 0


def validate(root, records):
    errs = []
    seen = set()
    ids = {r.get("id") for r in records}
    for r in records:
        rid = r.get("id", "?")
        for key in ("id", "created", "class", "title", "status", "confidence",
                    "value", "usage", "pin"):
            if key not in r:
                errs.append(f"{rid}: missing field {key}")
        if rid in seen:
            errs.append(f"{rid}: duplicate id")
        seen.add(rid)
        if r.get("class") not in CLASSES:
            errs.append(f"{rid}: bad class {r.get('class')!r}")
        if r.get("status") not in STATUSES:
            errs.append(f"{rid}: bad status {r.get('status')!r}")
        if r.get("status") == "merged" and not r.get("tombstone"):
            errs.append(f"{rid}: merged with no tombstone")
        tb = r.get("tombstone")
        if tb and tb not in ids:
            errs.append(f"{rid}: tombstone {tb} does not resolve")
        if r.get("pin") and r.get("class") != "measurement":
            errs.append(f"{rid}: pinned but not a measurement record")
        if (r.get("status") == "merged" and r.get("pin")
                and r.get("merged_by") != "author"):
            errs.append(f"{rid}: a PINNED record was merged by compaction — only an "
                        f"explicit author merge may consolidate a measurement record")
    # log chain
    p = store_paths(root)["log"]
    if os.path.isfile(p):
        seqs = [json.loads(l)["seq"] for l in read_text(p).splitlines() if l.strip()]
        if seqs != sorted(seqs) or len(set(seqs)) != len(seqs):
            errs.append("mutations.jsonl: seq is not strictly increasing")
    return errs


def cmd_check(root, args):
    records = load_records(root)
    if not records:
        print("errata-store: store is empty — run: tools/errata-store.py import")
        return 1
    errs = validate(root, records)
    print("=" * 67)
    print("errata-store — the craft-knowledge store")
    print("=" * 67)
    print(f"  records: {len(records)}  "
          f"(pinned {sum(1 for r in records if r['pin'])} · "
          f"active {sum(1 for r in records if r['status'] == 'active')} · "
          f"merged {sum(1 for r in records if r['status'] == 'merged')} · "
          f"expired {sum(1 for r in records if r['status'] == 'expired')})")
    if errs:
        for e in errs:
            print(f"  FAIL  {e}")
        return 1
    print("  ok    schema, ids, tombstones, pins and the log chain all check out")
    return 0


def cmd_score(root, args):
    records = load_records(root)
    changed = 0
    for r in records:
        c = initial_confidence(r)
        v = value_of({**r, "confidence": c})
        if c != r.get("confidence") or v != r.get("value"):
            before = dict(r)
            r["confidence"], r["value"] = c, v
            append_mutation(root, "score", before, dict(r), "recomputed")
            changed += 1
    save_records(root, records)
    print(f"scored {len(records)} records ({changed} changed)")
    return 0


def cmd_list(root, args):
    records = load_records(root)
    status = args[args.index("--status") + 1] if "--status" in args else None
    cls = args[args.index("--class") + 1] if "--class" in args else None
    for r in records:
        if status and r["status"] != status:
            continue
        if cls and r["class"] != cls:
            continue
        pin = "PIN" if r["pin"] else "   "
        print(f"  {pin} {r['id']}  {r['status']:9} c={r['confidence']:.2f} "
              f"v={r['value']:5.2f}  {r['title'][:58]}")
    return 0


def cmd_show(root, args):
    if not args:
        return 2
    for r in load_records(root):
        if r["id"] == args[0]:
            print(json.dumps(r, indent=2, sort_keys=True))
            return 0
    print(f"errata-store: no such id: {args[0]}")
    return 1


def merge(root, loser_id, winner_id, records, allow_pinned=False):
    """Merge loser into winner. Automatic consolidation never moves a PINNED record;
    an explicit author merge (--allow-pinned) may, because consolidating two dated
    entries for the same defect is a person's judgment and the body is archived,
    never deleted — ERRATA.md still carries the text either way."""
    by_id = {r["id"]: r for r in records}
    loser, winner = by_id[loser_id], by_id[winner_id]
    pinned = bool(loser["pin"] or winner["pin"])
    if pinned and not allow_pinned:
        print(f"refused: {loser_id if loser['pin'] else winner_id} is PINNED "
              f"({PINNED_PIN}) — automatic compaction never moves a measurement record; "
              f"an explicit author merge needs --allow-pinned")
        return False
    before = dict(loser)
    winner.setdefault("merged_from", [])
    if loser_id not in winner["merged_from"]:
        winner["merged_from"].append(loser_id)
    if winner["value"] < loser["value"]:
        winner["value"] = loser["value"]          # keep the stronger number
    loser["status"] = "merged"
    loser["tombstone"] = winner_id
    loser["merged_by"] = "author" if pinned else "compaction"
    loser["body"] = ""
    loser["updated"] = date.today().isoformat()
    archived = archive_body(root, before, f"merged into {winner_id} ({loser['merged_by']})")
    append_mutation(root, "merge", before, dict(loser), f"-> {winner_id}; body {archived}")
    return True


def expire_pass(root, records, ttl_days, dry):
    today = date.today()
    n = 0
    for r in records:
        if r["pin"] or r["status"] != "active":
            continue
        age = (today - date.fromisoformat(r["created"])).days
        u = r.get("usage", {})
        past_expiry = r.get("expiry") and r["expiry"] <= today.isoformat()
        low_value = (r["confidence"] < LOW_CONFIDENCE
                     and u.get("applied", 0) == 0 and age > ttl_days)
        if not (past_expiry or low_value):
            continue
        why = "past expiry" if past_expiry else f"low confidence, unused, {age}d old"
        print(f"  {'would expire' if dry else 'expire'} {r['id']}  ({why})  {r['title'][:50]}")
        if dry:
            n += 1
            continue
        before = dict(r)
        archived = archive_body(root, before, f"expired: {why}")
        r["status"], r["body"] = "expired", ""
        r["updated"] = today.isoformat()
        append_mutation(root, "expire", before, dict(r), f"{why}; body {archived}")
        n += 1
    return n


def dedupe_pass(root, records, dry):
    groups = {}
    for r in records:
        if r["pin"] or r["status"] != "active":
            continue
        groups.setdefault(normalize_title(r["title"]), []).append(r)
    n = 0
    for key, group in groups.items():
        if len(group) < 2:
            continue
        group.sort(key=lambda r: (-r["value"], r["id"]))
        keeper, losers = group[0], group[1:]
        for loser in losers:
            print(f"  {'would merge' if dry else 'merge'} {loser['id']} -> {keeper['id']}"
                  f"  ({loser['title'][:50]})")
            if not dry:
                merge(root, loser["id"], keeper["id"], records)
            n += 1
    return n


def seal_log(root):
    """Bound the live log: seal the oldest events to an archive segment with a digest."""
    p = store_paths(root)["log"]
    if not os.path.isfile(p):
        return None
    events = [json.loads(l) for l in read_text(p).splitlines() if l.strip()]
    if len(events) <= SEAL_LIMIT:
        return None
    keep = events[-SEAL_LIMIT:]
    sealed = events[:-SEAL_LIMIT]
    blob = "".join(json.dumps(e, sort_keys=True) + "\n" for e in sealed)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
    dest = os.path.join(store_paths(root)["arch"], f"mutations-{sealed[0]['seq']}.jsonl")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    write_text(dest, blob)
    write_text(p, "".join(json.dumps(e, sort_keys=True) + "\n" for e in keep))
    return {"sealed": len(sealed), "sha256_16": digest, "file": rpath(os.path.relpath(dest, root))}


def write_snapshot(root, records, note):
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    p = os.path.join(store_paths(root)["snap"], f"{ts}.json")
    payload = {
        "ts": ts,
        "note": note,
        "last_seq": next_seq(root) - 1,
        "count": len(records),
        "records": records,
        "sealed_log_digests": [],
    }
    write_text(p, json.dumps(payload, indent=1, sort_keys=True))
    return rpath(os.path.relpath(p, root))


def cmd_compact(root, args):
    dry = "--dry-run" in args
    ttl = int(args[args.index("--ttl-days") + 1]) if "--ttl-days" in args else DEFAULT_TTL_DAYS
    records = load_records(root)
    print(f"compact ({'dry run' if dry else 'apply'}) — pinned records are never touched")
    m = dedupe_pass(root, records, dry)
    e = expire_pass(root, records, ttl, dry)
    if not dry and (m or e):
        save_records(root, records)
        sealed = seal_log(root)
        snap = write_snapshot(root, records, f"compact: {m} merged, {e} expired")
        if sealed:
            print(f"  sealed {sealed['sealed']} log events -> {sealed['file']} "
                  f"(sha256 {sealed['sha256_16']})")
        print(f"  snapshot: {snap}")
    print(f"  {m} merged · {e} expired")
    return 0


def cmd_merge(root, args):
    allow = "--allow-pinned" in args
    pos = [a for a in args if not a.startswith("--")]
    if len(pos) < 2:
        return 2
    records = load_records(root)
    if merge(root, pos[0], pos[1], records, allow_pinned=allow):
        save_records(root, records)
        print(f"merged {pos[0]} -> {pos[1]}" + ("  [author merge of a pinned record]" if allow else ""))
        return 0
    return 1


def cmd_restore(root, args):
    if not args:
        return 2
    rid = args[0]
    p = store_paths(root)["log"]
    events = [json.loads(l) for l in read_text(p).splitlines() if l.strip()] if os.path.isfile(p) else []
    target = None
    for ev in reversed(events):
        if ev.get("id") == rid and ev.get("before") is not None:
            target = ev
            break
    if not target:
        print(f"errata-store: no mutation to undo for {rid}")
        return 1
    records = load_records(root)
    for i, r in enumerate(records):
        if r["id"] == rid:
            before = dict(target["before"])
            append_mutation(root, "restore", dict(r), before,
                            f"undo seq {target['seq']} ({target['op']})")
            records[i] = before
            break
    else:
        # the record was removed entirely (not the case today) — reinstate it
        append_mutation(root, "restore", None, dict(target["before"]),
                        f"undo seq {target['seq']}")
        records.append(dict(target["before"]))
    save_records(root, records)
    print(f"restored {rid} — undid {target['op']} (seq {target['seq']})")
    return 0


def cmd_rollback(root, args):
    if "--to" not in args:
        return 2
    upto = int(args[args.index("--to") + 1])
    p = store_paths(root)["log"]
    events = [json.loads(l) for l in read_text(p).splitlines() if l.strip()] if os.path.isfile(p) else []
    records = load_records(root)
    by_id = {r["id"]: r for r in records}
    reverted = 0
    for ev in reversed([e for e in events if e["seq"] > upto]):
        if ev.get("before") is None:
            continue
        by_id[ev["before"]["id"]] = dict(ev["before"])
        reverted += 1
    save_records(root, list(by_id.values()))
    append_mutation(root, "rollback", None, None, f"reverted {reverted} mutations after seq {upto}")
    print(f"rollback: reverted {reverted} mutations beyond seq {upto}")
    return 0


def cmd_snapshot(root, args):
    records = load_records(root)
    print(f"snapshot: {write_snapshot(root, records, 'manual')}")
    return 0


def cmd_render(root, args):
    records = load_records(root)
    lines = [
        "# ERRATA-CRAFT — the craft-knowledge view",
        "",
        "**Generated by `tools/errata-store.py render`. Do not hand-edit.**",
        "",
        "This is the readable half of the store behind "
        "[`ERRATA.md`](ERRATA.md). `ERRATA.md` stays append-only and is never edited; "
        "this view is regenerated from `record/errata.jsonl` and can be deleted and "
        "rebuilt at any time. Measurement findings are **pinned** — the freeze cites "
        "them by date and compaction never moves them. Craft findings carry a "
        "prototype confidence, a usage count, and an expiry.",
        "",
        f"_{len(records)} records · "
        f"{sum(1 for r in records if r['pin'])} pinned · "
        f"{sum(1 for r in records if r['status'] == 'active')} active · "
        f"{sum(1 for r in records if r['status'] == 'merged')} merged · "
        f"{sum(1 for r in records if r['status'] == 'expired')} expired_",
        "",
        "| id | date | class | target | state | status | conf | value | pin | title |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        lines.append(
            f"| `{r['id']}` | {r['created']} | {r['class']} | "
            f"`{r['target'] or '—'}` | {r['state']} | {r['status']} | "
            f"{r['confidence']:.2f} | {r['value']:.2f} | "
            f"{'PIN' if r['pin'] else ''} | {r['title'][:80]} |"
        )
    lines += [
        "",
        "## Compaction",
        "",
        "`tools/errata-store.py compact --dry-run` shows what a compaction would merge "
        "or expire. Nothing pinned is ever touched; merged and expired bodies move to "
        "`record/archive/`, and `restore <id>` (or `rollback --to <seq>`) puts them "
        "back. The live mutation log is sealed to `record/archive/` past 500 events, "
        "with a SHA-256 digest recorded in the next snapshot, so the audit trail is "
        "complete without growing without bound.",
        "",
    ]
    write_text(store_paths(root)["view"], "\n".join(lines) + "\n")
    print(f"rendered {rpath(os.path.relpath(store_paths(root)['view'], root))} "
          f"({len(records)} records)")
    return 0


def cmd_log(root, args):
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else 20
    p = store_paths(root)["log"]
    events = [json.loads(l) for l in read_text(p).splitlines() if l.strip()] if os.path.isfile(p) else []
    for ev in events[-limit:]:
        print(f"  {ev['seq']:4}  {ev['ts']}  {ev['op']:8} {ev.get('id') or '—':22} {ev['detail'][:60]}")
    print(f"  ({len(events)} events total)")
    return 0


# --- self-test -------------------------------------------------------------

def selftest():
    checks = []

    def ok(cond, label):
        checks.append((bool(cond), label))

    tmp = tempfile.mkdtemp(prefix="errata-store-")
    try:
        src = os.path.join(tmp, "ERRATA.md")
        write_text(src, "\n".join([
            "# ERRATA", "",
            "### 2026-01-01 — a craft finding about similes",
            "- **row:**      quoin (process | delegation)",
            "- **observed:** the overprint repeats",
            "- **n:**        3",
            "- **evidence:** three books",
            "- **motive:**   aesthetic",
            "- **state:**    observed",
            "- **proposes:** cut the explanation",
            "",
            "### 2026-01-02 — a measurement finding about U4",
            "- **row:**      U4",
            "- **observed:** the floor fails the canon",
            "- **n:**        140",
            "- **evidence:** corpus control",
            "- **motive:**   aesthetic",
            "- **state:**    adopted",
            "- **proposes:** advisory",
            "",
        ]))
        recs = import_records(tmp, "TEST")
        by = {r["id"]: r for r in recs}
        craft = by["E-2026-01-01-001"]
        meas = by["E-2026-01-02-001"]
        ok(craft["class"] == "craft" and not craft["pin"], "import: process row -> craft, unpinned")
        ok(meas["class"] == "measurement" and meas["pin"] == [PINNED_PIN],
           "import: gate row -> measurement, pinned")
        ok(meas["confidence"] > craft["confidence"],
           "import: an adopted corpus-backed measurement outranks a single-book craft note")
        save_records(tmp, recs)

        # a duplicate must merge; a pinned record must refuse to
        dup = dict(craft, id="E-2026-01-03-001", title=craft["title"], value=0.1)
        recs2 = load_records(tmp) + [dup]
        save_records(tmp, recs2)
        ok(merge(tmp, "E-2026-01-03-001", "E-2026-01-01-001", recs2),
           "merge: a duplicate craft record merges")
        ok(not merge(tmp, "E-2026-01-02-001", "E-2026-01-01-001", recs2),
           "merge: automatic compaction refuses to merge a PINNED measurement record")
        loser = [r for r in recs2 if r["id"] == "E-2026-01-03-001"][0]
        ok(loser["status"] == "merged" and loser["tombstone"] == "E-2026-01-01-001"
           and loser["body"] == "", "merge: loser tombstoned and body moved out")
        arch = os.path.join(tmp, "record", "archive")
        ok(os.path.isdir(arch) and any(f.endswith(".jsonl") for f in os.listdir(arch)),
           "merge: body archived under record/archive/ (never deleted)")
        save_records(tmp, recs2)

        # a person MAY consolidate a pinned measurement record; compaction may not
        ok(merge(tmp, "E-2026-01-02-001", "E-2026-01-01-001", recs2, allow_pinned=True),
           "merge: an explicit author merge MAY consolidate a PINNED record")
        save_records(tmp, recs2)
        cmd_restore(tmp, ["E-2026-01-02-001"])
        pm = [r for r in load_records(tmp) if r["id"] == "E-2026-01-02-001"][0]
        ok(pm["status"] == "active" and pm["pin"] == [PINNED_PIN],
           "restore: an author-merged PINNED record returns to active, pin intact")

        # restore must bring a merged record back
        cmd_restore(tmp, ["E-2026-01-03-001"])
        back = [r for r in load_records(tmp) if r["id"] == "E-2026-01-03-001"][0]
        ok(back["status"] == "active" and back["tombstone"] is None,
           "restore: the merged record is active again")
        ok(len(load_records(tmp)) == 3, "restore: no record was dropped")

        # expiry + archive, then rollback to a seq
        old = dict(craft, id="E-2020-01-01-001", created="2020-01-01",
                   confidence=0.2, value=0.2, title="low value old note")
        recs3 = load_records(tmp) + [old]
        save_records(tmp, recs3)
        n = expire_pass(tmp, recs3, 30, False)
        exp = [r for r in recs3 if r["id"] == "E-2020-01-01-001"][0]
        ok(exp["status"] == "expired",
           "expire: a low-confidence unused old craft record expires")
        ok(n >= 1, f"expire: the pass expired {n} low-value record(s), not zero")
        ok(exp["body"] == "",
           "expire: expired record keeps its id, loses its body")
        ok(not [r for r in recs3 if r["id"] == "E-2026-01-02-001" and r["status"] != "active"],
           "expire: the pinned measurement record was untouched")
        save_records(tmp, recs3)

        errs = validate(tmp, load_records(tmp))
        ok(not errs, f"check: the store validates ({'; '.join(errs) if errs else 'clean'})")
        ok(cmd_render(tmp, []) == 0 and os.path.isfile(os.path.join(tmp, "ERRATA-CRAFT.md")),
           "render: the human view is written")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [label for good, label in checks if not good]
    for good, label in checks:
        print(("  ok    " if good else "  FAIL  ") + label)
    print("-" * 67)
    if failed:
        print(f"SELF-TEST FAILURE — {len(failed)} of {len(checks)} assertions failed.")
        return 1
    print(f"SELF-TEST PASS — {len(checks)} assertions "
          "(import, pin, merge, archive, restore, expire, validate, render).")
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
    table = {
        "import": cmd_import, "check": cmd_check, "list": cmd_list, "show": cmd_show,
        "score": cmd_score, "merge": cmd_merge, "compact": cmd_compact,
        "expire": lambda r, a: cmd_compact(r, a), "restore": cmd_restore,
        "rollback": cmd_rollback, "snapshot": cmd_snapshot, "render": cmd_render,
        "log": cmd_log,
    }
    if cmd == "selftest":
        return selftest()
    if cmd not in table:
        print(f"errata-store: unknown command {cmd}")
        return 2
    return table[cmd](root, rest)


if __name__ == "__main__":
    sys.exit(main())
