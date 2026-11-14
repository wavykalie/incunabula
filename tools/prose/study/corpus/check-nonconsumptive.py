#!/usr/bin/env python3
"""check-nonconsumptive.py - keep local-copy prose out of committed artifacts.

WHY THIS EXISTS
  The case for analysing a modern in-copyright text you lawfully hold rests on the use being
  non-consumptive: features are counted, the text is not republished. That holds only if no
  committed file carries a verbatim run from the book. One pasted sentence in a report breaks
  it, and nobody would notice by reading the report.

  So: every `local-copy` row in the registry, every committed text artifact, every 8-word
  shingle. A match is a leak.

  Eight words is the threshold because shorter runs survive ordinary quotation, titles and
  idiomatic phrasing; at eight, a match is the book's own sentences, not a coincidence.

usage:
    python corpus/check-nonconsumptive.py [--registry R] [--books DIR] [--artifact PATH ...]

    With no --artifact, the scan covers every git-tracked text file under the study dir,
    excluding books/ (the texts themselves are not artifacts).

exit
    0  no committed artifact reproduces a local-copy text
    1  at least one artifact contains a run from a local-copy work
    2  no local-copy rows to check, or no text found for them - NOT RUN, never a pass
"""

import argparse
import csv
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))
DEFAULT_REGISTRY = os.path.join(HERE, "sources-v2.tsv")
NGRAM = 8
WORD = re.compile(r"[a-z0-9']+")
TEXT_EXT = (".md", ".txt", ".csv", ".json", ".tsv", ".jsonl", ".yaml", ".yml")


def words(text):
    return WORD.findall(text.lower())


def shingles(seq, n=NGRAM):
    return {" ".join(seq[i:i + n]) for i in range(len(seq) - n + 1)}


def local_rows(registry):
    if not os.path.exists(registry):
        return [], "no registry"
    with open(registry, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    return [r for r in rows
            if (r.get("license") or "").strip().lower() == "local-copy"], ""


def read_tree(root):
    parts = []
    if os.path.isfile(root):
        with open(root, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    for base, _, names in os.walk(root):
        for name in sorted(names):
            if name.lower().endswith(TEXT_EXT):
                with open(os.path.join(base, name), encoding="utf-8",
                          errors="replace") as fh:
                    parts.append(fh.read())
    return "\n\n".join(parts)


def tracked_artifacts(study):
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=study, check=True,
                             capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        out = ""
    if not out:
        found = []
        for base, dirs, names in os.walk(study):
            dirs[:] = [d for d in dirs if d not in ("books", "__pycache__", ".git")]
            for name in names:
                if name.lower().endswith(TEXT_EXT):
                    found.append(os.path.join(base, name))
        return found
    files = []
    for rel in out.split("\0"):
        if not rel or rel.startswith("books/"):
            continue
        if rel.lower().endswith(TEXT_EXT):
            files.append(os.path.join(study, rel))
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    ap.add_argument("--books", default=os.path.join(STUDY, "books"),
                    help="tree holding the local-copy texts (default: study/books)")
    ap.add_argument("--artifact", action="append", default=None,
                    help="artifact file or directory to scan (repeatable)")
    args = ap.parse_args(argv)

    rows, why = local_rows(args.registry)
    if not rows:
        print(f"check-nonconsumptive: no local-copy rows ({why or 'registry has none'}). "
              f"Nothing to check is NOT RUN, never a pass.")
        return 2

    corpus, misses = {}, []
    for r in rows:
        slot = (r.get("slots") or "").strip()
        path = os.path.join(args.books, slot)
        if not os.path.isdir(path):
            misses.append(slot)
            continue
        corpus[slot] = shingles(words(read_tree(path)))
    if not corpus:
        print(f"check-nonconsumptive: no text found for {len(rows)} local-copy row(s) "
              f"under {args.books}. Nothing to check is NOT RUN, never a pass.")
        return 2
    for slot in misses:
        print(f"  note: {slot} has no text under {args.books} - not scanned")

    artifacts = []
    for a in args.artifact or [None]:
        if a is None:
            artifacts.extend(tracked_artifacts(STUDY))
        elif os.path.isdir(a):
            artifacts.extend(os.path.join(b, n) for b in [a] for n in os.listdir(a))
        else:
            artifacts.append(a)

    leaks = 0
    for path in sorted(set(artifacts)):
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        seq = words(text)
        for i in range(len(seq) - NGRAM + 1):
            span = " ".join(seq[i:i + NGRAM])
            for slot, sh in corpus.items():
                if span in sh:
                    leaks += 1
                    print(f"  LEAK  {os.path.relpath(path, STUDY)} "
                          f"reproduces {NGRAM} words of {slot}: \"{span[:60]}...\"")
                    break

    print(f"check-nonconsumptive: {len(corpus)} local-copy work(s), "
          f"{len(set(artifacts))} artifact(s) scanned, {leaks} leak(s)")
    if leaks:
        print("FAIL - a committed artifact reproduces prose from a local-copy work. "
              "Paraphrase the finding, cite counts and ids, or move the file out of git.")
        return 1
    print("OK - no committed artifact carries an 8-word run from a local-copy work.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
