#!/usr/bin/env python3
"""fetch-document-layers.py - a corpus of DOCUMENT-SIZED published prose.

Why this exists. `P1` and `A25` are *rate* rules, so the size of the document they are
applied to decides the verdict before the prose is read. At 2,000 words one instance is
0.50/1k against a cap of 3; at 612 words it is 2.00/1k against a cap of 1.63. Ashgrove's
612-word annotation layer failed `A25` on one real antithesis and the arithmetic said any
layer under 667 words would fail on its first. Two rows now show the same shape, and the
question neither the chapters nor the layers could answer is: **do published human
documents of that size actually stay under these caps?**

A chapter corpus cannot answer it, because a chapter is 3,000-6,000 words. The published
form whose unit IS the document is the book of letters, and their documents are the size
Ashgrove's layers are. This stages them at their own boundaries - not by chopping chapters,
which would manufacture opener repetition at every cut.

Everything here is public domain (Project Gutenberg), 1768-1892. That is the usual
copyright wall and the usual caveat: a rule that passes here is not thereby proven clean on
a 2020s novel. It IS proven or disproven on documents of this size, which is the only
question this corpus was built to ask.

usage:  python fetch-document-layers.py <out-dir> [--limit N] [--min N] [--max N]
"""

import os
import re
import sys
import urllib.request

# Each entry is (gutenberg id, stem, title, head regex). The regex is the book's OWN
# document marker: a book of letters numbers its letters, and a diary dates its entries.
# Nothing is split on a guess about where a document "should" end.
# Every entry carries the Title: string the id MUST resolve to. Gutenberg ids are not
# memorable and a wrong one fails silently: 1661 is a Sherlock Holmes collection and
# 10214 is a Plato treatise, and an earlier draft of this file staged both as "letters"
# without noticing. The fetcher now refuses an id whose Gutenberg title does not contain
# `expect`, so a mis-numbered source can never enter the corpus as anonymous prose.
#    # Lady Susan (946) is correct but its edition sets no letter headings, so its 41 letters
    # cannot be recovered by this method; named here rather than dropped, because "the book
    # that would not split" is information about the corpus, not a gap. The Diary of a Nobody
    # (21517) also would not serve: its Project Gutenberg edition has no plain-text cache file.
SOURCES = [
    (6053, "burney-evelina", "Burney, Evelina, 1778 (letters, 41 documents)",
     re.compile(r"(?im)^[ \t]*LETTER[ \t]+([IVXLCDM]{1,7}|\d+)[.:]?[ \t]*$"),
     "Evelina"),
    (84, "shelley-frankenstein", "Shelley, Frankenstein, 1818 (the Walton letters)",
     re.compile(r"(?im)^[ \t]*LETTER[ \t]+([IVXLCDM]{1,7}|\d+)[.:]?[ \t]*$"),
     "Frankenstein"),
    # Widened 2026-11-07: four more epistolary novels, because 44 documents (two books,
    # 41 of them one book) is too thin a base rate to settle a floor on. These add 18th-
    # century letters of the same document size, in English, all public domain. Each
    # book's own heading is used; none is split on a guess.
    (2160, "smollett-humphry-clinker", "Smollett, Humphry Clinker, 1771 (letters)",
     re.compile(r"(?im)^[ \t]*To[ \t]+(?:Mr|Mrs|Miss|Dr|Sir|Madam|Captain|Colonel|Lady|Rev)\b[^\n]{0,90}$"),
     "Humphry Clinker"),
    (6124, "richardson-pamela", "Richardson, Pamela, 1740 (letters)",
     re.compile(r"(?im)^[ \t]*LETTER[ \t]+([IVXLCDM]{1,7}|\d+)[.:]?[ \t]*$"),
     "Pamela"),
    # Clarissa's headings carry the correspondents on the same line ("LETTER I. Miss Howe
    # to ..."), so this pattern cannot anchor at end of line the way Evelina's does.
    (9296, "richardson-clarissa-v1", "Richardson, Clarissa vol. 1, 1748 (letters)",
     re.compile(r"(?im)^[ \t]*LETTER[ \t]+[IVXLCDM]{1,7}\b.*$"),
     "Clarissa Harlowe"),
    (12431, "foster-coquette", "Foster, The Coquette, 1797 (letters)",
     re.compile(r"(?im)^[ \t]*LETTER[ \t]+([IVXLCDM]{1,7}|\d+)[.:]?[ \t]*$"),
     "Coquette"),
    (16300, "brooke-emily-montague", "Brooke, Emily Montague, 1769 (letters)",
     re.compile(r"(?im)^[ \t]*LETTER[ \t]+([IVXLCDM]{1,7}|\d+)[.:]?[ \t]*$"),
     "Emily Montague"),
]

PG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.S)
PG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.S)


def fetch(gut_id):
    url = f"https://www.gutenberg.org/cache/epub/{gut_id}/pg{gut_id}.txt"
    with urllib.request.urlopen(url, timeout=90) as fh:
        raw = fh.read()
    text = raw.decode("utf-8", "replace")
    # Same normalisation as fetch-multivolume.py: a stray "\r\r\n" opened in text mode
    # becomes a blank line between every wrapped line, which turns hard wrapping into
    # paragraphs and changes every paragraph statistic this corpus might later feed.
    text = text.replace("\r\r\n", "\n").replace("\r\n", "\n").replace("\r", "\n")
    return text


def strip_gutenberg(text):
    return PG_END.sub("", PG_START.sub("", text, count=1), count=1)


def split_documents(text, head, minimum):
    marks = sorted({m.start() for m in head.finditer(text)})
    if not marks:
        return []
    # Front matter: a table of contents lists every letter before the first one is read,
    # so the first N marks are headings with a few words under each. Filtering those on
    # word count is not enough - the LAST TOC mark's segment runs into the real first
    # document and survives. A segment that contains two or more further headings is a
    # contents list, and the document is what follows its final heading.
    out = []
    seen = set()
    for i, start in enumerate(marks):
        end = marks[i + 1] if i + 1 < len(marks) else len(text)
        body = text[start:end].strip()
        inner = [m.start() for m in head.finditer(body)]
        if len(inner) >= 2:
            body = body[inner[-1]:].strip()
        if len(body.split()) < minimum:
            continue
        # A table of contents is one segment that ends at the second real document, so
        # taking the text after its last heading can reproduce the first document. Both
        # copies end at the same boundary; key on the tail rather than the head, which
        # differs by the contents heading.
        key = re.sub(r"[^a-z0-9]", "", body[-400:].lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(body)
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    out = sys.argv[1]
    limit = len(SOURCES)
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    minimum = 80
    if "--min" in sys.argv:
        minimum = int(sys.argv[sys.argv.index("--min") + 1])
    maximum = 1500
    if "--max" in sys.argv:
        maximum = int(sys.argv[sys.argv.index("--max") + 1])

    os.makedirs(out, exist_ok=True)
    total, staged, skipped = 0, [], []

    for gid, stem, title, head, expect in SOURCES[:limit]:
        try:
            raw = fetch(gid)
        except Exception as exc:                                    # noqa: BLE001
            skipped.append(f"{stem}: fetch failed ({exc})")
            continue
        found = re.search(r"(?im)^Title:\s*(.+)$", raw)
        found_title = found.group(1).strip() if found else ""
        if expect.lower() not in found_title.lower():
            skipped.append(f"{stem}: gutenberg {gid} is {found_title!r}, not {expect!r} - REFUSED")
            continue
        text = strip_gutenberg(raw)
        docs = [d for d in split_documents(text, head, minimum)
                if len(d.split()) <= maximum]
        if len(docs) < 3:
            skipped.append(f"{stem}: {len(docs)} usable documents - not staged")
            continue
        for i, doc in enumerate(docs, 1):
            with open(os.path.join(out, f"{stem}__doc-{i:03d}.txt"), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write(doc)
        total += len(docs)
        staged.append((title, len(docs)))
        print(f"  {title:<52} {len(docs):>3} documents")

    print()
    print(f"staged {total} documents in {out}")
    print("size bands: " + " ".join(
        f"{lo}-{hi}w={sum(1 for f in os.listdir(out) if lo <= len(open(os.path.join(out, f), encoding='utf-8').read().split()) < hi)}"
        for lo, hi in ((0, 167), (167, 400), (400, 667), (667, 1500))))
    if skipped:
        print()
        for s in skipped:
            print("  not staged:", s)
    print()
    print("Measure it:")
    print(f"    bash tools/prose/deslop-check.sh {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
