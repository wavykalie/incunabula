#!/usr/bin/env python3
"""chunk-pd-corpus.py - split published novels into chapter-sized chunks.

`audit-slack.py` compares a cap against the worst rate in a whole published DOCUMENT.
The scanner, though, applies every cap to a CHAPTER, and a chapter is the smaller
unit: the same density in fewer words is fewer hits, so a document-level maximum is
not a chapter-level one. That gap is why 24 of 26 audited rows read TIGHTER than
their derivation - the comparison is conservative, which is the safe direction, but
it means the audit cannot answer the question that actually matters:

    does a cap fail a real published CHAPTER?

This answers it directly. It slices each novel into fixed word-count chunks, which
approximates a chapter without needing the book's own structure, and writes them as
separate files so `deslop-check.sh` can be pointed at them as a directory.

A fixed slice is deliberately *harsher* than a real chapter in one respect: real
chapters vary in length, and the scanner's cap is proportional to words, so a short
chapter is checked just as hard per word as a long one. It is fairer in another: a
slice can cut a sentence in half at both ends, which a real chapter boundary does
not. Neither favours the caps, which is the point.

usage:  python chunk-pd-corpus.py <corpus-dir> <out-dir> [--words N]
"""

import os
import re
import shutil
import sys

PROSE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chapter lengths from CALIBRATION.md: published chapters average 3,557 words, this
# project's own books run ~2,150. The default is the smaller of the two - the tighter
# test, since fewer words means fewer permitted hits for the same density.
DEFAULT_WORDS = 2150

WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if len(args) < 2:
        print(__doc__.strip())
        return 2
    corpus, out = args[0], args[1]
    words = DEFAULT_WORDS
    for f in flags:
        if f.startswith("--words"):
            words = int(f.split("=", 1)[1]) if "=" in f else int(sys.argv[sys.argv.index(f) + 1])

    if not os.path.isdir(corpus):
        print(f"no corpus at {corpus}")
        return 2
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    nfiles = 0
    for name in sorted(os.listdir(corpus)):
        path = os.path.join(corpus, name)
        if not os.path.isfile(path) or not name.lower().endswith(".txt"):
            continue
        with open(path, encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        # Split on sentence-ish boundaries so a chunk does not end mid-word.
        pieces = re.split(r"(?<=[.!?])\s+", text)
        chunks, cur, count = [], [], 0
        for piece in pieces:
            cur.append(piece)
            count += len(WORD.findall(piece))
            if count >= words:
                chunks.append(" ".join(cur))
                cur, count = [], 0
        if cur and count >= words // 2:
            chunks.append(" ".join(cur))
        for i, chunk in enumerate(chunks, 1):
            with open(os.path.join(out, f"{name[:-4]}-ch{i:03d}.txt"), "w",
                      encoding="utf-8") as fh:
                fh.write(chunk)
        nfiles += len(chunks)

    print(f"wrote {nfiles} chunks of ~{words} words from "
          f"{len(os.listdir(corpus))} source files into {out}")
    print()
    print("A cap that fails any of these is failing published human prose.")
    print("Point the scanner at it:")
    print(f"    bash {os.path.join(PROSE, 'deslop-check.sh')} {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
