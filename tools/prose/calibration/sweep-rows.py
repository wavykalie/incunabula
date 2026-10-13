#!/usr/bin/env python3
"""sweep-rows.py - the genre sweep: measure the FROZEN rule table across corpus subsets.

The question (CALIBRATION.md section 20): the deslop rows were calibrated on
nineteenth-century narrative prose. Which of them accuse a published PRESCRIPTIVE
book - self-help, parenting, pedagogy, the register of the demo genres - purely for
being the register it is? Section 18 ran this sweep against narrative nonfiction and
found U1. This runs the same sweep, same method, against the advice register.

It holds NO rule of its own. Every regex is read out of tools/prose/deslop-check.sh at
runtime through lint-chapter's own loader, and the closing-coda position rule (F1) reads
CODA_RE out of the same file. Where this tool and the scanner disagree, the scanner is
right - this is a measurement aid and the scanner is the instrument.

Read path mirrors the scanner: stray CRs are stripped and Project Gutenberg boilerplate
removed before anything is measured. Per-file application mirrors the gate: a row
"accuses" a file exactly when deslop-check.sh would fail that file (HARD and WARN_ONLY on
any hit, density tiers on the scanner's integer cap arithmetic n*aw > an*words). Corpus
rates are reported alongside for the comparison table in CALIBRATION.md.

Measurement tool, not a gate: it reads published prose and passes no verdict on any
manuscript. Same class as measure.py and fetch-multivolume.py, absent from
GATE_FREEZE.md's manifest by design.

usage: python sweep-rows.py CORPUS_DIR [CORPUS_DIR ...]

Exit codes:
    0  sweep printed
    2  no corpus files found - an empty sweep must never read as a clean one
"""

import glob
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCANNER = os.path.join(HERE, "..", "deslop-check.sh")
LINT = os.path.join(HERE, "..", "..", "lint-chapter.py")

PG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.S)
PG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.S)


def load_rules():
    """The rule table via lint-chapter's loader. Never a copy: measure.py kept its own
    mirror and drifted from the scanner until the mirror was stale. One loader, one table."""
    spec = importlib.util.spec_from_file_location("lint_chapter", LINT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rules, err = mod.load_rules()
    if err:
        raise SystemExit(f"sweep-rows: {err}")
    return rules


def load_coda_re():
    with open(SCANNER, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    m = re.search(r"^CODA_RE='([^']*)'", text, re.M)
    if not m:
        raise SystemExit("sweep-rows: CODA_RE did not parse out of the scanner")
    return re.compile(m.group(1), re.I)


def read_body(path):
    """Mirror of the scanner's read path: normalise, then strip Gutenberg boilerplate."""
    with open(path, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    text = text.replace("\r", "")
    text = PG_START.sub("", text, count=1)
    text = PG_END.sub("", text, count=1)
    return text


def tail_para(text):
    """The closing paragraph, the same one F1 judges: last blank-line-separated block."""
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    return re.sub(r"\n", " ", paras[-1]) if paras else ""


def sweep_dir(path, rules, coda_rx):
    all_files = sorted(glob.glob(os.path.join(path, "*.txt")))
    if not all_files:
        print(f"== {os.path.basename(path)}: no .txt files - nothing measured")
        return False

    # __flat volumes are whole books the fetcher could not chapter. They are a
    # different unit and get their own block: a 255,000-word treatise in the same
    # denominator as 3,000-word chapters would move the rates without changing
    # anything about the register.
    flat = [f for f in all_files if "__flat" in os.path.basename(f)]
    ok = False
    for label, files in (("chapters", [f for f in all_files if f not in flat]),
                         ("flat volumes", flat)):
        if files and sweep_block(path, label, files, rules, coda_rx):
            ok = True
    return ok


def sweep_block(path, label, files, rules, coda_rx):
    compiled = []
    for tier, rid, name, an, aw, wn, ww, rx, flags in rules:
        compiled.append((tier, rid, name, an, aw, re.compile(rx, flags)))

    totals = {}   # rid -> [hits, files_hit, files_accused]
    words_total, nfiles, coda_closes = 0, 0, 0

    for fpath in files:
        text = read_body(fpath)
        words = len(text.split())
        if words == 0:
            continue
        nfiles += 1
        words_total += words
        for tier, rid, name, an, aw, rx in compiled:
            n = sum(1 for _ in rx.finditer(text))
            acc = n > 0 if tier in ("HARD", "WARN_ONLY") else (n * aw) > (an * words)
            row = totals.setdefault(rid, [0, 0, 0])
            row[0] += n
            if n:
                row[1] += 1
            if acc:
                row[2] += 1
        if coda_rx.search(tail_para(text)):
            coda_closes += 1

    subset = os.path.basename(os.path.normpath(path))
    print(f"== {subset} / {label}   {nfiles} files   {words_total} words")
    print(f"{'id':<6} {'tier':<8} {'name':<24} {'hits':>6} {'per1k':>7} "
          f"{'cap/1k':>7} {'files accused':>14}")
    seen = set()
    for tier, rid, name, an, aw, _rx in compiled:
        if rid in seen:
            continue
        seen.add(rid)
        hits, with_hits, accused = totals.get(rid, [0, 0, 0])
        per1k = hits * 1000.0 / max(1, words_total)
        if tier in ("HARD", "WARN_ONLY"):
            capstr, note = "0", f"{with_hits}/{nfiles} w/ hits"
        else:
            capstr = f"{an * 1000.0 / aw:.2f}"
            note = f"{accused}/{nfiles}"
        print(f"{rid:<6} {tier:<8} {name:<24} {hits:>6} {per1k:>7.2f} "
              f"{capstr:>7} {note:>14}")
    print(f"{'F1':<6} {'POSITION':<8} {'closing coda':<24} {'':>6} {'':>7} {'0':>7} "
          f"{str(coda_closes) + '/' + str(nfiles) + ' close on coda':>14}")
    print()
    return True


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    rules = load_rules()
    coda_rx = load_coda_re()
    any_files = False
    for path in argv[1:]:
        any_files = sweep_dir(path, rules, coda_rx) or any_files
    if not any_files:
        print("sweep-rows: nothing measured - an empty sweep is never a clean sweep")
        return 2
    print('"files accused" counts files the row would fail the way deslop-check.sh gates')
    print("them (HARD/WARN_ONLY on any hit, density tiers on the cap arithmetic).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
