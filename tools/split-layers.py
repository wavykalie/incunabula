#!/usr/bin/env python3
"""split-layers.py — per-layer gate evidence for a `structure: layered` book.

WHY THIS EXISTS
  A layered book's gates are scoped per layer: a footnote layer and a main-text
  layer have nothing to measure against each other. Rewriting the frozen
  instruments to understand layers would mean editing the instrument, which the
  freeze forbids, and forking it would mean two versions of a checker.

  So the unit moves instead of the tool. A layered book's chapter files fence
  each document run:

      <!-- layer:01-survey -->
      ...prose...
      <!-- /layer -->

  and this script extracts every layer's runs into artifacts/layers/<id>/<chapter>,
  one file per layer per chapter. `deslop-check.sh` is then pointed at one layer
  directory at a time, unmodified, and the result is attributable to the same
  frozen instrument as every other book's.

WHAT IT REFUSES
  An unfenced chapter (prose with no layer identity), an unclosed fence, or a
  nested fence. Each of those makes "which layer is this sentence in?" a question
  the book cannot answer, and a per-layer gate run over such a file would be
  measuring a guess. A book whose text is only partly fenced is not a layered
  book; it is a conventional book with comments in it.

  A markdown heading or blank line before the first fence is allowed: the chapter
  title is not a document layer.

USAGE
    python tools/split-layers.py <book-root> [--dry-run]

EXIT
    0  every chapter split, artifacts written
    1  a fence defect - nothing written for the offending chapter
    2  no chapters found (not-run is never a pass)
"""

import os
import re
import sys

START = re.compile(r"^\s*<!--\s*layer:\s*([A-Za-z0-9._-]+)\s*-->\s*$")
END = re.compile(r"^\s*<!--\s*/layer\s*-->\s*$")
SAFE = re.compile(r"^[A-Za-z0-9._-]+$")


def split(text):
    """-> ({layer: [blocks]}, prose_before_first_fence, errors)"""
    blocks, errors = {}, []
    before = []
    layer, buf, seen_fence = None, [], False
    for n, line in enumerate(text.splitlines(), 1):
        m = START.match(line)
        if m:
            if layer is not None:
                errors.append(f"line {n}: fence opened inside layer {layer!r}")
                continue
            name = m.group(1)
            if not SAFE.match(name):
                errors.append(f"line {n}: layer id {name!r} is not a safe directory name")
            layer, buf, seen_fence = name, [], True
            continue
        if END.match(line):
            if layer is None:
                errors.append(f"line {n}: closing fence with no open layer")
                continue
            blocks.setdefault(layer, []).append("\n".join(buf).strip())
            layer = None
            continue
        if layer is None:
            before.append((n, line))
        else:
            buf.append(line)
    if layer is not None:
        errors.append(f"unclosed fence for layer {layer!r} at end of file")

    trail = [(n, ln) for n, ln in before
             if ln.strip() and not ln.lstrip().startswith("#")]
    if trail:
        errors.append(f"{len(trail)} line(s) of prose outside any layer fence, "
                      f"first at line {trail[0][0]}: {trail[0][1].strip()[:60]!r}")
    return blocks, trail, errors


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in argv
    if len(args) != 1:
        print(__doc__)
        return 2
    root = args[0]
    chdir = os.path.join(root, "manuscript", "chapters")
    if not os.path.isdir(chdir):
        print(f"split-layers: no manuscript/chapters under {root} - nothing to split.")
        return 2
    names = sorted(n for n in os.listdir(chdir)
                   if n.endswith((".md", ".txt")) and re.search(r"chapter[-_ ]?\d+", n, re.I))
    if not names:
        print(f"split-layers: no chapter files under {chdir} - not-run is never a pass.")
        return 2

    out_root = os.path.join(root, "artifacts", "layers")
    failed = 0
    totals = {}
    for name in names:
        path = os.path.join(chdir, name)
        with open(path, encoding="utf-8", errors="ignore") as fh:
            blocks, _, errors = split(fh.read())
        if errors:
            failed += 1
            print(f"split-layers: {name}")
            for e in errors:
                print(f"  - {e}")
            continue
        if not blocks:
            failed += 1
            print(f"split-layers: {name} has no layer fences - the book declares "
                  f"`structure: layered` and this chapter has no layer identity.")
            continue
        for layer in sorted(blocks):
            joined = "\n\n".join(b for b in blocks[layer] if b) + "\n"
            words = len(joined.split())
            totals.setdefault(layer, 0)
            totals[layer] += words
            if dry:
                continue
            d = os.path.join(out_root, layer)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, name), "w", encoding="utf-8", newline="") as fh:
                fh.write(joined)

    if failed:
        print(f"split-layers: {failed} chapter(s) refused. A layer the book cannot "
              f"name is a layer no gate can measure.")
        return 1

    print(f"split-layers: {len(names)} chapter(s) split into {len(totals)} layer(s)"
          + (" (dry run, nothing written)" if dry else f" under {out_root}"))
    for layer in sorted(totals):
        print(f"  {layer:<16} {totals[layer]:>6} words")
    print("  point the frozen scanner at one layer at a time, e.g.")
    print(f"    bash tools/prose/deslop-check.sh {out_root}/<layer>")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
