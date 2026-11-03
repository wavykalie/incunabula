#!/usr/bin/env python3
"""drive.py - run Arm A books end to end through the route the probe recorded.

One book is one naive conversation: the planned payload once, then §3's continuation
sentence, resumed in the same conversation, until the accepted band is reached or the
model stalls. Every response is saved verbatim, every call is filed through
`run/dispatch.py` (so the prompt digest, the opening/passage collision checks and the
manifest row are all dispatch's, not this script's), and the model id filed for a call is
the one that call's own log resolved - not the one we asked for.

WHY THE RESOLVER LINE IS PARSED PER CALL
  `DECISIONS.md` (2026-11-02) records that this route does not return an API modelVersion
  and that the CLI's resolver log is the evidence of what ran. Reading it per call, rather
  than trusting the probe record once, is what makes a mid-run swap visible: a call that
  resolves to a different id files nothing, because dispatch refuses a model that disagrees
  with `run/harness.json` unless the change is recorded as a sub-cohort.

WHAT THIS DOES NOT DO
  It cannot run Arm B. The pipeline books need the Incunabula phases at a frozen commit,
  with an operator counting gate interventions; that is a different route and a different
  contract (design §4, RUNBOOK §9). This script refuses an Arm B row rather than pretending.

usage:
    python run/drive.py --dry-run A-02 A-03 ...     # validate plan rows and payloads
    python run/drive.py A-02 A-03 ...               # draft, file, finalize
"""

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, STUDY)
sys.path.insert(0, HERE)
import dispatch                                                  # noqa: E402

RESOLVER = re.compile(r'model alias "([^"]+)" resolved to "([^"]+)"')

# Why this exists: on 2026-11-02 A-20's opening came back as a 36-word filter notice and was
# filed as chapter one of a book that then continued from it (DECISIONS.md). A refusal is not
# prose, so it stops the book here instead of becoming text nobody can attribute.
BLOCK = re.compile(r"blocked by Gemini's filters", re.I)

def refused(text):
    return bool(BLOCK.search(text))


def sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


def write(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


class Stop(Exception):
    """A refusal or a stall. The book is reported, not rescued."""


class Skip(Exception):
    """Already in the manifest. Not a failure, and not a re-roll."""


def conversation_of(work):
    """The conversation to resume. Recorded at the opening call, recovered from it if not.

    A book interrupted after its first call must continue ITS OWN conversation: a fresh
    opening would be a re-roll, which design §7 files as a deviation, not a retry.
    """
    p = os.path.join(work, "conversation.txt")
    if os.path.exists(p) and read(p).strip():
        return read(p).strip()
    p = os.path.join(work, "01.json")
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8-sig")).get("conversation_id") or ""
        except Exception:
            pass
    raise Stop("cannot resume: no conversation id was recorded for this book")


def plan_rows(out):
    path = os.path.join(out, "RUNPLAN.csv")
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return {r["book_id"]: r for r in csv.DictReader(fh)}


def probe_model(path):
    if not os.path.exists(path):
        raise Stop(f"no probe record at {path}; run `python run/harness.py --check`")
    return json.load(open(path, encoding="utf-8")).get("model_returned")


def resolved_model(log_path, fallback):
    """The id this call's own resolver line names, or the probe's value as a fallback."""
    if os.path.exists(log_path):
        found = RESOLVER.findall(read(log_path))
        if found:
            return found[-1][1], f'resolver log: alias {found[-1][0]!r} resolved'
    return fallback, "probe record (no resolver line in this call's log)"


def call(prompt, work, tag, conversation, model):
    log_path = os.path.join(work, tag + ".log")
    cmd = ["agy", "--print=" + prompt, "--model", model, "--output-format", "json",
           "--dangerously-skip-permissions", "--log-file", log_path]
    if conversation:
        cmd += ["--conversation", conversation]
    proc = subprocess.run(cmd, cwd=work, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    write(os.path.join(work, tag + ".json"), proc.stdout or "")
    write(os.path.join(work, tag + ".err"), proc.stderr or "")
    try:
        doc = json.loads(proc.stdout)
    except Exception:
        raise Stop(f"{tag}: unreadable JSON (rc {proc.returncode}); "
                   f"stderr: {(proc.stderr or '').strip()[:200]}")
    return doc, log_path


def ingest(args, cmd):
    proc = subprocess.run([sys.executable, os.path.join(HERE, "dispatch.py"), *cmd],
                          cwd=STUDY, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise Stop(f"dispatch refused: {proc.stdout.strip()[-400:]}")
    return proc.stdout


def locked_ingest(args, cmd):
    """Finalize under a lock file.

    Parallel streams append to one `books/manifest.csv`; a finalize that read the file
    while another wrote it would be checking duplicates against a half-written table.
    """
    lock = os.path.join(STUDY, "books", ".manifest.lock")
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    deadline = time.time() + 300
    fd = None
    while time.time() < deadline:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            time.sleep(2)
    if fd is None:
        raise Stop("could not take the manifest lock within five minutes")
    try:
        return ingest(args, cmd)
    finally:
        os.close(fd)
        try:
            os.remove(lock)
        except OSError:
            pass


def book(bid, row, args, probe, counters, filed):
    if bid in filed:
        raise Skip(f"{bid} is already in the manifest")
    if row["arm"] != "A":
        raise Stop(f"{bid} is Arm {row['arm']}; this driver only runs Arm A (design §4 "
                   f"needs the pipeline, RUNBOOK §9)")
    payload_path = os.path.join(args.out, row["payload_path"])
    payload = read(payload_path)
    if sha_text(payload) != row["payload_sha256"]:
        raise Stop(f"{bid}: payload digest does not match RUNPLAN.csv")
    book_dir = os.path.join(STUDY, row["book_dir"])
    log_file = os.path.join(book_dir, "logs", "prompts.jsonl")
    man = os.path.join(book_dir, "manuscript", "naive-text.md")
    band_lo = int(row["band_lo"])
    entries = []
    if os.path.exists(log_file):
        for line in read(log_file).splitlines():
            if not line.strip():
                continue
            try:
                entries.append(json.loads(line))
            except ValueError:
                continue          # a half-written last line from an interrupted call

    work = os.path.join(args.out, "agy", bid)
    responses = os.path.join(args.out, "responses", bid)
    os.makedirs(responses, exist_ok=True)
    if entries:
        conversation = conversation_of(work)
        calls = len(entries)
        have = len(read(man).split()) if os.path.exists(man) else 0
        print(f"    resuming: {calls} call(s) already filed, {have:,} words", flush=True)
    else:
        if os.path.isdir(work):
            shutil.move(work, work + "-prev")
        os.makedirs(work)
        write(os.path.join(work, "prompt-sent.txt"), payload)
        doc, log_path = call(payload, work, "01", None, dispatch.MODEL)
        model_id, source = resolved_model(log_path, probe)
        text = doc.get("response") or ""
        if not text.strip():
            raise Stop(f"{bid}: opening returned no text "
                       f"(denied: {doc.get('denied_actions')})")
        if refused(text):
            raise Stop(f"{bid}: the opening was refused by the model's filter, not written "
                       f"({len(text.split())} words of notice). Nothing was filed.")
        write(os.path.join(responses, "01.txt"), text)
        conversation = doc.get("conversation_id") or ""
        write(os.path.join(work, "conversation.txt"), conversation)
        ingest(args, ["--ingest", bid, "--response", os.path.join(responses, "01.txt"),
                      "--model-returned", model_id])
        print(f"    opening: {len(text.split()):,} words, model {model_id} ({source})",
              flush=True)
        calls = 1

    stall = ""
    while True:
        words = len(read(man).split()) if os.path.exists(man) else 0
        if words >= band_lo:
            break
        if calls > args.max_continuations:
            stall = f"stopped at {words:,} words after {calls - 1} continuation(s)"
            break
        calls += 1
        tag = f"{calls:02d}"
        doc, log_path = call(dispatch.CONTINUATION, work, tag, conversation,
                             dispatch.MODEL)
        model_id, source = resolved_model(log_path, probe)
        text = doc.get("response") or ""
        if not text.strip():
            stall = (f"stalled at {words:,} words: continuation {tag} returned no text "
                     f"(denied: {doc.get('denied_actions')})")
            calls -= 1
            break
        if refused(text):
            stall = (f"stalled at {words:,} words: continuation {tag} returned a filter "
                     f"notice instead of prose")
            calls -= 1
            break
        write(os.path.join(responses, tag + ".txt"), text)
        ingest(args, ["--ingest", bid, "--response", os.path.join(responses, tag + ".txt"),
                      "--model-returned", model_id, "--continuation"])
        print(f"    continuation {tag}: {len(text.split()):,} words "
              f"({source}) -> {len(read(man).split()):,}", flush=True)

    if not os.path.exists(log_file):
        raise Stop(f"{bid}: no prompt log was written; nothing to file")
    cmd = ["--finalize-only", bid, "--out", args.out]
    notes = [n for n in (stall, args.deviation) if n]
    if notes:
        cmd += ["--deviation", "; ".join(notes)]
    if stall:
        counters["stalls"] += 1
    locked_ingest(args, cmd)
    words = len(read(man).split())
    print(f"    filed: {words:,} words, {calls} call(s)"
          + (f" | NOTE {stall}" if stall else ""), flush=True)
    counters["filed"] += 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("books", nargs="+", help="Arm A book ids, in dispatch order")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--harness", default=os.environ.get("STUDY_HARNESS")
                    or os.path.join(HERE, "harness.json"))
    ap.add_argument("--max-continuations", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true",
                    help="validate plan rows and payload digests, call nothing")
    ap.add_argument("--deviation", default="",
                    help="a protocol note recorded on every row this run files")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    rows = plan_rows(args.out)
    probe = probe_model(args.harness) if not args.dry_run else None
    filed = set()
    manifest = os.path.join(STUDY, "books", "manifest.csv")
    if os.path.exists(manifest):
        with open(manifest, encoding="utf-8-sig", newline="") as fh:
            filed = {r["book_id"] for r in csv.DictReader(fh)}
    counters = {"filed": 0, "failed": 0, "stalls": 0}
    print(f"drive: {len(args.books)} book(s), model sent {dispatch.MODEL}, "
          f"continuation {dispatch.CONTINUATION!r}", flush=True)

    for bid in args.books:
        row = rows.get(bid)
        print(f"\n== {bid}", flush=True)
        if not row:
            print("    FAIL not in the plan", flush=True)
            counters["failed"] += 1
            continue
        try:
            if args.dry_run:
                payload = read(os.path.join(args.out, row["payload_path"]))
                ok = sha_text(payload) == row["payload_sha256"] and row["arm"] == "A"
                filed = os.path.exists(os.path.join(STUDY, row["book_dir"], "logs",
                                                    "prompts.jsonl"))
                print(f"    {'would run' if ok and not filed else 'skip'}: arm {row['arm']}, "
                      f"{int(row['target_words']):,} words target, payload "
                      f"{'matches' if ok else 'MISMATCH'}"
                      + (", already filed" if filed else ""), flush=True)
                continue
            book(bid, row, args, probe, counters, filed)
        except Skip as exc:
            print(f"    SKIP {exc}", flush=True)
        except Stop as exc:
            print(f"    STOP {exc}", flush=True)
            counters["failed"] += 1
        except KeyboardInterrupt:
            print("    interrupted; the books filed so far stand", flush=True)
            break

    print(f"\ndrive: {counters['filed']} filed, {counters['failed']} stopped, "
          f"{counters['stalls']} stall note(s)", flush=True)
    return 0 if counters["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
