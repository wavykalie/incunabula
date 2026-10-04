#!/usr/bin/env python3
"""check-narrative.py - does the book pay what it promised?

WHY THIS EXISTS
  Every gate in this directory measures the SURFACE of prose. None measures the SHAPE of
  story. A book can pass deslop per chapter, hold one voice across the manuscript, vary
  its chapter lengths and still contain: a wound introduced in chapter one and never
  mentioned again, a secondary character who delivers the plot and exits in a log entry,
  four chapters running the same emotional circuit, and extended scenes that all serve
  the same function. Those are the failures an external reader finds and no scanner sees.

  This tool reads NO PROSE. It reads one declared file - NARRATIVE_LEDGER.yaml at the
  book root, beside CANON_LEDGER.yaml - and checks the book against its own declared
  narrative obligations. The declarations are written by the skills (case-keeper records
  debt in extraction pass 6; proof-panel declares the per-chapter beat arc and each
  extended scene's function at Phase 4). This tool only verifies them, mechanically.

WHY IT MAY GATE WITHOUT A CORPUS (read this before trusting the exit code)
  The directory's rule is that a threshold needs a measured corpus, and this row gates
  with no corpus at all. That is legitimate for exactly one class of row, and the class
  already exists: `check-length.py` (L1). Quoting its reasoning, which applies here
  unchanged:

      "This row needs no corpus. There is no population it can false-fail, because
       it is not measuring a population. A book either delivered its declared
       length or it did not."

  N1 compares a book to the narrative obligations THAT BOOK DECLARED FOR ITSELF. There
  is no published prose to calibrate against because no published prose is being
  measured. A book with a debt ledger either closed its entries or it did not. The
  prose-reading companions in this class (`check-figurative.py`, `check-dialogue-tags.py`,
  `check-quantities.py`) DO measure prose, and every one of them is therefore
  report-only until a corpus exists. The line is the same line the directory has always
  drawn.

  The principle N1 enforces is the structural analogue of "not-run is never pass":
  **an unexamined setup is a failure, not a loose end.** An entry the book introduced
  with emphasis and never resolved must end the pipeline as OPEN (a failure at
  delivery) or DEFERRED with a recorded reason (a legitimate decision - series do this).
  It may never end as silence.

THE ROWS
  N1  narrative debt       GATES   every obligation RESOLVED or DEFERRED-with-reason
  N2  beat repetition      reports declared per-chapter emotional arcs that repeat
  N3  scene function       reports declared scene functions that duplicate
  N4  ledger conformance   GATES   schema validity, status discipline, staleness

  N2 and N3 are REPORT-ONLY and cannot fail anything. They print counts and pairs; the
  numbers in them (the near-duplicate similarity line, the pure-texture share) are
  observations, not thresholds. This project does not set a threshold from an unmeasured
  number, and there is no corpus of published beat maps from which one could be derived.
  A repeated arc is a fact about this book, and the author judges it - which is the
  correct division of labour, because a repeated circuit is sometimes deliberate.

EXIT CODES (mirroring check-length.py, because the same absences mean the same things)
    0  the ledger covers the book, conforms, and owes nothing at delivery
    1  N1 FAIL (open debt at delivery) or N4 FAIL (non-conformant or stale at delivery)
    2  the ledger declares nothing and tracks no chapter - NOT RUN, never means pass
    3  no NARRATIVE_LEDGER.yaml at the book root - UNGOVERNED, not a pass, not a fail
    4  the book declares status: in_progress - recorded, never a delivery failure
       (N4 schema conformance is still enforced mid-draft: a malformed ledger is
        broken input, not unfinished work. Staleness mid-draft is expected and only
        recorded - chapters drafted since the last case-keeper UPDATE are normal.)

WHAT THIS TOOL CANNOT DO, AND IT IS THE WHOLE LIMIT
  It cannot see a setup that nobody recorded. It reads no prose, so a wound the
  manuscript introduces and the ledger never captures passes this gate perfectly. The
  extraction is case-keeper's job and the audit is collator's; this tool is the third
  layer, the one that makes the ledger's own claims checkable. A book with a clean
  ledger and a careless extraction is exactly as invisible here as it is everywhere
  else - which is why the Phase 6 checklist requires collator's full pass BEFORE this
  row is consulted, and why the sweep order is written into the skill, not into this
  file. A ledger validator cannot validate a ledger nobody wrote.

  It also cannot tell a deliberate open thread (a series hook, an intentional ambiguity)
  from an abandoned one. That is what DEFERRED-with-reason exists for. The tool checks
  that the reason was written down; it does not check that the reason is good.

usage:  tools/prose/check-narrative.py [BOOK_DIR ...]
        (no argument = every */manuscript/chapters under the project root)
"""

import glob
import os
import re
import sys

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)
LEDGER = "NARRATIVE_LEDGER.yaml"

# Closed vocabularies. A declaration outside these lists is a conformance failure,
# because a closed list is what makes N3's comparison mechanical: "theme payoff" must
# mean the same thing in every row or the duplicate check compares nothing.
DEBT_KINDS = {"mystery", "trauma", "character", "clock", "promise", "threat",
              "object", "skill"}
DEBT_STATUS = {"OPEN", "RESOLVED", "DEFERRED"}
SCENE_FUNCTIONS = {"relationship shift", "theme payoff", "plot turn",
                   "character revelation", "pure texture"}

SIMILARITY_LINE = 0.6   # printed, not enforced. No corpus of published beat maps exists.


# --------------------------------------------------------------- strict mini-YAML
# The project ships no dependencies, so PyYAML is not available. This parser accepts
# EXACTLY the subset the narrative-ledger-schema.md specifies - top-level sections,
# `key: value` maps, and lists of one-line flow maps (`- {id: D-001, ...}`) or scalars -
# and raises LedgerError with a line number on anything else. It never guesses. A ledger
# that will not parse is a FAIL (exit 1), not a skip: the maintenance gate's standing
# rule is "read it with a real parser, not an eyeball", and the failure mode this
# replaces is a ledger whose rows are silently dropped - which hides the very debts the
# ledger exists to show.

class LedgerError(Exception):
    pass


def _scalar(text, line_no):
    t = text.strip()
    if t == "" or t.lower() in ("null", "~"):
        return None
    if t.lower() == "true":
        return True
    if t.lower() == "false":
        return False
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if (t.startswith('"') and t.endswith('"') and len(t) >= 2) or \
       (t.startswith("'") and t.endswith("'") and len(t) >= 2):
        return t[1:-1]
    if t.startswith("[") and t.endswith("]"):
        inner = t[1:-1].strip()
        if not inner:
            return []
        return [_scalar(p, line_no) for p in _split_flow(inner, line_no)]
    if t.startswith("{"):
        raise LedgerError(f"line {line_no}: nested flow map not supported")
    return t


def _split_flow(inner, line_no):
    """Split a flow sequence/map body on commas that are not inside quotes."""
    parts, cur, quote = [], "", None
    for ch in inner:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            cur += ch
        elif ch == ",":
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if quote:
        raise LedgerError(f"line {line_no}: unterminated quote")
    if cur.strip():
        parts.append(cur)
    return parts


def _flow_map(inner, line_no):
    out = {}
    for part in _split_flow(inner, line_no):
        if ":" not in part:
            raise LedgerError(f"line {line_no}: flow entry without ':' : {part.strip()!r}")
        k, v = part.split(":", 1)
        key = k.strip()
        if not key:
            raise LedgerError(f"line {line_no}: empty key in flow map")
        out[key] = _scalar(v, line_no)
    return out


def parse_ledger(text):
    """Strict subset parser. Returns {section: [ ... ]} with `meta` as a map."""
    data = {}
    section = None
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("\t"):
            raise LedgerError(f"line {n}: tabs are not allowed (YAML indentation is spaces)")
        indent = len(line) - len(line.lstrip())
        body = line.strip()

        if indent == 0:
            if ":" not in body:
                raise LedgerError(f"line {n}: top-level line without ':'")
            key, rest = body.split(":", 1)
            section = key.strip()
            if not section:
                raise LedgerError(f"line {n}: empty top-level key")
            if section in data:
                raise LedgerError(f"line {n}: duplicate top-level section {section!r}")
            data[section] = {} if rest.strip() == "" else _scalar(rest, n)
            continue

        if section is None:
            raise LedgerError(f"line {n}: indented line before any section")

        if body.startswith("- "):
            item = body[2:].strip()
            if item.startswith("{") and item.endswith("}"):
                value = _flow_map(item[1:-1], n)
            else:
                value = _scalar(item, n)
            if not isinstance(data[section], list):
                if isinstance(data[section], dict) and not data[section]:
                    data[section] = []
                else:
                    raise LedgerError(f"line {n}: list item under non-list section {section!r}")
            data[section].append(value)
        else:
            if ":" not in body:
                raise LedgerError(f"line {n}: map line without ':'")
            if not isinstance(data[section], dict):
                raise LedgerError(f"line {n}: map line under list section {section!r}")
            k, v = body.split(":", 1)
            data[section][k.strip()] = _scalar(v, n)
    return data


# ------------------------------------------------------------------ the checks

def book_status(book_root):
    """The book's own first `status:` value, or None. Same rule as check-length.py:
    only the literal `in_progress` reclassifies anything. PROJECT_STATE.yaml first,
    then STATE.yaml - the project layout allows either name, and treating the second
    as absent would re-create check-length's documented ungoverned confusion."""
    for name in ("PROJECT_STATE.yaml", "STATE.yaml"):
        path = os.path.join(book_root, name)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    head = fh.read(8000)
            except OSError:
                continue
            m = re.search(r"^\s*status\s*:\s*[\"']?([A-Za-z_. -]+)", head, re.I | re.M)
            if m and m.group(1).strip().lower() == "in_progress":
                return "in_progress"
            return None
    return None


def conformance(ledger):
    """N4, schema half. Returns a list of defect strings (empty = conformant)."""
    defects = []
    meta = ledger.get("meta")
    if not isinstance(meta, dict):
        defects.append("meta: section missing or not a map")
        meta = {}
    tracked = meta.get("chapters_tracked")
    if not isinstance(tracked, list) or not all(isinstance(c, int) for c in tracked):
        defects.append("meta.chapters_tracked: must be a list of chapter numbers")
        tracked = []

    beats = ledger.get("beats") or []
    scenes = ledger.get("scenes") or []
    debt = ledger.get("debt") or []
    for name, rows in (("beats", beats), ("scenes", scenes), ("debt", debt)):
        if not isinstance(rows, list):
            defects.append(f"{name}: must be a list of one-line flow maps")
    beats = beats if isinstance(beats, list) else []
    scenes = scenes if isinstance(scenes, list) else []
    debt = debt if isinstance(debt, list) else []

    seen_arcs = set()
    for i, row in enumerate(beats, 1):
        where = f"beats[{i}]"
        if not isinstance(row, dict):
            defects.append(f"{where}: not a flow map")
            continue
        ch, arc = row.get("chapter"), row.get("arc")
        if not isinstance(ch, int):
            defects.append(f"{where}: chapter must be a number")
        if not arc or not isinstance(arc, str):
            defects.append(f"{where}: arc must be a non-empty string")
        if isinstance(ch, int):
            if ch in seen_arcs:
                defects.append(f"{where}: chapter {ch} has more than one declared arc")
            seen_arcs.add(ch)
            if tracked and ch not in tracked:
                defects.append(f"{where}: chapter {ch} is not in meta.chapters_tracked")

    for i, row in enumerate(scenes, 1):
        where = f"scenes[{i}]"
        if not isinstance(row, dict):
            defects.append(f"{where}: not a flow map")
            continue
        ch, fn = row.get("chapter"), row.get("function")
        if not isinstance(ch, int):
            defects.append(f"{where}: chapter must be a number")
        if fn not in SCENE_FUNCTIONS:
            defects.append(f"{where}: function {fn!r} is not one of "
                           f"{sorted(SCENE_FUNCTIONS)}")
        if not row.get("scene"):
            defects.append(f"{where}: scene must be a non-empty string")
        if isinstance(ch, int) and tracked and ch not in tracked:
            defects.append(f"{where}: chapter {ch} is not in meta.chapters_tracked")

    seen_ids = set()
    for i, row in enumerate(debt, 1):
        where = f"debt[{i}]"
        if not isinstance(row, dict):
            defects.append(f"{where}: not a flow map")
            continue
        did = row.get("id")
        if not did:
            defects.append(f"{where}: id is required")
        elif did in seen_ids:
            defects.append(f"{where}: duplicate id {did!r}")
        else:
            seen_ids.add(did)
        if row.get("kind") not in DEBT_KINDS:
            defects.append(f"{where}: kind {row.get('kind')!r} is not one of "
                           f"{sorted(DEBT_KINDS)}")
        if not row.get("description"):
            defects.append(f"{where}: description is required")
        if not row.get("opened"):
            defects.append(f"{where}: opened (source ref) is required")
        status = row.get("status")
        if status not in DEBT_STATUS:
            defects.append(f"{where}: status {status!r} is not one of "
                           f"{sorted(DEBT_STATUS)}")
        elif status == "RESOLVED":
            if not row.get("resolution"):
                defects.append(f"{where}: RESOLVED without a resolution")
            if not row.get("resolved_at"):
                defects.append(f"{where}: RESOLVED without resolved_at")
        elif status == "DEFERRED" and not row.get("deferred_reason"):
            defects.append(f"{where}: DEFERRED without a deferred_reason - "
                           f"deferral is a decision and the reason is the decision")
    return defects


def _tokens(arc):
    stop = {"the", "and", "with", "into", "onto", "from", "that", "this", "then",
            "when", "than", "back", "out", "away", "down", "her", "his", "she",
            "him", "they", "them", "its", "for", "but", "not", "gets", "get"}
    return {w for w in re.findall(r"[a-z']+", str(arc).lower()) if w not in stop and len(w) > 2}


def _norm_arc(arc):
    s = str(arc).lower().replace("→", "->").replace("\u2192", "->")
    return re.sub(r"\s+", " ", s).strip()


def beats_rows(beats):
    """N2, report-only. Exact duplicates, near-duplicate pairs, consecutive runs."""
    rows = [b for b in beats if isinstance(b, dict)
            and isinstance(b.get("chapter"), int) and b.get("arc")]
    rows.sort(key=lambda b: b["chapter"])
    lines = []
    exact, runs = {}, []
    for b in rows:
        exact.setdefault(_norm_arc(b["arc"]), []).append(b["chapter"])
    for arc, chs in exact.items():
        if len(chs) > 1:
            lines.append(f"   --   N2  identical arc in chapters {chs}:  \"{arc}\"")
    prev_key = prev_ch = None
    run = []
    for b in rows:
        key = _norm_arc(b["arc"])
        if key == prev_key and b["chapter"] == prev_ch + 1:
            run.append(b["chapter"])
        else:
            if len(run) > 1:
                runs.append(list(run))
            run = [b["chapter"]]
        prev_key, prev_ch = key, b["chapter"]
    if len(run) > 1:
        runs.append(list(run))
    for r in runs:
        lines.append(f"   --   N2  consecutive chapters {r} share one arc shape")
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = _tokens(rows[i]["arc"]), _tokens(rows[j]["arc"])
            if not a or not b:
                continue
            sim = len(a & b) / min(len(a), len(b))
            if sim >= SIMILARITY_LINE and _norm_arc(rows[i]["arc"]) != _norm_arc(rows[j]["arc"]):
                lines.append(f"   --   N2  near-identical arcs ch {rows[i]['chapter']} "
                             f"and ch {rows[j]['chapter']} (overlap {sim:.2f}):")
                lines.append(f"          {rows[i]['arc']!r}")
                lines.append(f"          {rows[j]['arc']!r}")
    return lines, rows


def scenes_rows(scenes):
    """N3, report-only. Function duplication and the pure-texture share."""
    rows = [s for s in scenes if isinstance(s, dict)]
    by_fn = {}
    for s in rows:
        by_fn.setdefault(s.get("function"), []).append(s)
    lines = []
    for fn in sorted(by_fn, key=lambda f: (f is None, str(f))):
        chs = [s.get("chapter") for s in by_fn[fn]]
        if len(chs) > 1 and fn != "pure texture":
            lines.append(f"   --   N3  function {fn!r} declared by {len(chs)} scenes "
                         f"(chapters {chs})")
    texture = by_fn.get("pure texture", [])
    if rows:
        tw = sum(int(s.get("words") or 0) for s in texture)
        total = sum(int(s.get("words") or 0) for s in rows)
        share = f"{100.0 * tw / total:.0f}% of declared scene words" if total else \
                f"{len(texture)} of {len(rows)} scenes (no word counts declared)"
        lines.append(f"   --   N3  pure texture: {share}. No cap is set - this directory")
        lines.append("          sets no threshold from an unmeasured number. A texture")
        lines.append("          budget is a decision the author makes and records.")
    return lines, rows


def check(label, book_root, chapters_on_disk, tracked_hint):
    path = os.path.join(book_root, LEDGER)
    print("=" * 67)
    print(f"## {label}   {chapters_on_disk} chapter file(s) on disk")
    print("=" * 67)

    with open(path, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    try:
        ledger = parse_ledger(text)
    except LedgerError as exc:
        print(f"   FAIL N4  ledger will not parse: {exc}")
        print("          A state file that will not parse is a FAIL, not a skip. The")
        print("          parser accepts only the narrative-ledger-schema.md subset;")
        print("          anything else is refused loudly rather than half-read.")
        return 1

    defects = conformance(ledger)
    meta = ledger.get("meta") if isinstance(ledger.get("meta"), dict) else {}
    tracked = meta.get("chapters_tracked") or []
    debt = ledger.get("debt") if isinstance(ledger.get("debt"), list) else []
    beats = ledger.get("beats") if isinstance(ledger.get("beats"), list) else []
    scenes = ledger.get("scenes") if isinstance(ledger.get("scenes"), list) else []

    stale = sorted(set(tracked_hint) - set(tracked)) if tracked_hint else []
    declared_empty = not (beats or scenes or debt or tracked)
    in_progress = book_status(book_root) == "in_progress"

    print(f"declared: {len(debt)} debt entr{'y' if len(debt) == 1 else 'ies'}, "
          f"{len(beats)} beat arc(s), {len(scenes)} extended scene(s); "
          f"chapters_tracked {tracked if tracked else 'EMPTY'}")
    print()

    # ---- N1: the debt row. The only one that gates on content.
    open_debt = [d for d in debt if isinstance(d, dict) and d.get("status") == "OPEN"]
    deferred = [d for d in debt if isinstance(d, dict) and d.get("status") == "DEFERRED"]
    resolved = [d for d in debt if isinstance(d, dict) and d.get("status") == "RESOLVED"]
    for d in open_debt:
        print(f"   --   N1  OPEN   {d.get('id')}  [{d.get('kind')}] "
              f"{d.get('description')}  (opened {d.get('opened')})")
    for d in deferred:
        print(f"   --   N1  DEFERRED {d.get('id')}  {d.get('deferred_reason')}")
    n1_status = "FAIL" if open_debt else "ok"
    if not debt:
        n1_status = "--"
        print("   --   N1  no debt entries declared. This passes only if extraction")
        print("          pass 6 actually ran; the tool cannot see an unrecorded setup.")
    else:
        print(f"   {n1_status:<5} N1  narrative debt       {len(resolved)} resolved, "
              f"{len(deferred)} deferred, {len(open_debt)} OPEN")
    print()

    # ---- N2 / N3: report-only, and they say so.
    b_lines, b_rows = beats_rows(beats)
    s_lines, s_rows = scenes_rows(scenes)
    for line in b_lines + s_lines:
        print(line)
    if not b_rows:
        print("   --   N2  no beat arcs declared - nothing to compare")
    if not s_rows:
        print("   --   N3  no extended scenes declared - nothing to compare")
    print()

    # ---- N4: conformance + staleness.
    if defects:
        for d in defects:
            print(f"   {'FAIL':<5} N4  {d}")
    if stale:
        print(f"   {'note' if in_progress else 'FAIL':<5} N4  STALE: chapters "
              f"{stale} exist on disk but are not in meta.chapters_tracked. A chapter")
        print("          the ledger has never seen cannot be shown to owe nothing.")
    if not defects and not stale:
        print("   ok    N4  ledger conforms to the schema and covers every chapter file")
    print()

    # ---- verdict assembly, precedence: conformance failure > in-progress > not-run.
    if defects:
        print("The ledger does not conform. Fix the ledger; the tool never edits it.")
        return 1
    if stale and not in_progress:
        print("The ledger is stale at delivery. Run case-keeper UPDATE over the")
        print("missing chapters, then re-run. Stale is not-run, and not-run is never pass.")
        return 1
    if declared_empty:
        print("NOT RUN: the ledger declares nothing and tracks no chapter.")
        print("Exit 2 never means pass.")
        return 2
    if in_progress:
        print("IN PROGRESS: N1 is recorded, not judged. A drafting book legitimately")
        print("owes open setups; the contract enforces the moment status: in_progress")
        print("is gone from PROJECT_STATE.yaml / STATE.yaml.")
        return 4
    if open_debt:
        print("NARRATIVE DEBT OPEN at delivery. Every entry must be RESOLVED (with the")
        print("resolution recorded) or DEFERRED (with the reason recorded). An open")
        print("setup is an unexamined setup, and an unexamined setup is a failure.")
        return 1
    print("NARRATIVE OK - the book paid what the ledger says it promised.")
    return 0


def resolve(arg):
    for candidate in (arg,
                      os.path.join(arg, "manuscript"),
                      os.path.join(arg, "manuscript", "chapters")):
        if os.path.isdir(candidate) and any(CHAPTER.search(n) for n in os.listdir(candidate)):
            return candidate
    return None


def main():
    args = sys.argv[1:]
    targets = []
    if args:
        for arg in args:
            directory = resolve(arg)
            if not directory:
                print(f"check-narrative: no chapters found under {arg}")
                return 3
            targets.append((arg, directory))
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for directory in sorted(glob.glob(os.path.join(root, "*", "manuscript", "chapters"))):
            targets.append((os.path.basename(os.path.dirname(os.path.dirname(directory))),
                            directory))

    checked = failures = ungoverned = skipped = in_progress = 0
    for label, directory in targets:
        book_root = os.path.dirname(os.path.dirname(os.path.abspath(directory)))
        path = os.path.join(book_root, LEDGER)
        chapter_nums = sorted(int(m.group(1)) for n in os.listdir(directory)
                              for m in [CHAPTER.search(n)] if m)
        if not os.path.isfile(path):
            print(f"check-narrative: {label} has NO {LEDGER} at its root ({book_root}) "
                  f"- UNGOVERNED by this row.")
            print("          This is not the same as declaring no narrative debt. It")
            print("          means nothing can say what this book owes. Exit 3 is not a")
            print("          pass and not a fail. Create the ledger (see")
            print("          incunabula-codex/references/narrative-ledger-schema.md),")
            print("          or say explicitly that the book carries no obligations.")
            print()
            ungoverned += 1
            continue
        rc = check(label, book_root, len(chapter_nums), chapter_nums)
        print()
        if rc == 2:
            skipped += 1
        elif rc == 1:
            failures += 1
        elif rc == 4:
            # The in-progress reclassification must survive the book loop and reach
            # the exit code. It did not before control 15 caught it: check() returned
            # 4, this loop counted it as checked, and the process exited 0 with a row
            # on screen saying the book was not judged. The row was honest and the
            # exit code lied - the same defect class as KF-004, one layer down.
            in_progress += 1
        else:
            checked += 1

    print("=" * 67)
    if failures:
        print(f"NARRATIVE FAILURE - {failures} book(s) owe something the ledger can name.")
        print("Fix the debt, or defer it with a reason. Silence is not a resolution.")
        return 1
    if ungoverned:
        print(f"NARRATIVE UNGOVERNED - {ungoverned} book(s) have no {LEDGER}. Exit 3.")
        return 3
    if in_progress:
        print(f"NARRATIVE IN PROGRESS - {in_progress} book(s) are still being drafted and "
              f"were recorded, not judged. Exit 4.")
        print("A drafting book legitimately owes open setups; the N1 contract enforces")
        print("again the moment status: in_progress is gone from the state file.")
        if checked:
            print(f"({checked} other book(s) were judged normally in the same run.)")
        return 4
    if skipped:
        print(f"NARRATIVE NOT RUN - {skipped} book(s) declare nothing. Exit 2, never pass.")
        return 2
    print(f"NARRATIVE OK - {checked} book(s) closed their declared obligations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
