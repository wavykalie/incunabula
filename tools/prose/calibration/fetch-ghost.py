#!/usr/bin/env python3
"""fetch-ghost.py - stage the ghost-story corpus the new horror book reads against.

The borrow list for that book names eleven works. Three are public domain and are fetched
here; the other eight (Jackson 1959, Barker 1984, Hill 2005, Ligotti 2006, Barron 2007,
Link 2015, Machado 2017, Kingfisher 2019) are in copyright and cannot be fetched by anyone.
They arrive only as `local-copy` documents under SOURCE_POLICY.md s3, and the `literary-horror`
row in LANES.tsv records them as NOT INSTALLED until they do.

What this stages is therefore the pre-1930 stratum: James's two collections and Dickens.
It is one end of the register, not the register - a book written now cannot take its
thresholds from 1843 and 1904 - and LANES.tsv says so on the row.

Two James volumes break the one-work-per-author rule the other lanes hold to. Recorded
rather than dropped: the pair is the canon of the English antiquarian ghost story, and
dropping the second would leave the lane with one author and one book.

Documents are staged as `<stem>__<NN>__<story>.txt`, one per story or stave, because every
cap in deslop-check.sh is a per-document rate and a pooled collection measures a register
nobody reads a book in.

usage:  python fetch-ghost.py <out-dir> [--limit N]
"""

import os
import re
import sys
import urllib.request

# One entry per work. `titles` is the collection's own table of contents, in order, and is
# used as the splitter: a heading is a line that normalises to one of these. `pattern` is
# used instead when the book marks its own divisions in a shape no title list describes.
WORKS = [
    dict(
        gid=8486,
        stem="james-antiquary",
        title="James, Ghost Stories of an Antiquary, 1904",
        titles=[
            "Canon Alberic's Scrap-book",
            "Lost Hearts",
            "The Mezzotint",
            "The Ash-tree",
            "Number 13",
            "Count Magnus",
            "\"Oh, Whistle, and I'll Come to You, My Lad\"",
            "The Treasure of Abbot Thomas",
        ],
    ),
    dict(
        gid=9629,
        stem="james-more-ghost-stories",
        title="James, More Ghost Stories of an Antiquary, 1911",
        titles=[
            "A School Story",
            "The Rose Garden",
            "The Tractate Middoth",
            "Casting the Runes",
            "The Stalls of Barchester Cathedral",
            "Martin's Close",
            "Mr Humphreys and His Inheritance",
        ],
    ),
    dict(
        gid=46,
        stem="dickens-christmas-carol",
        title="Dickens, A Christmas Carol, 1843",
        # The contents list sets the staves in title case ("Stave   I: Marley's Ghost") and
        # the body sets them in caps, so a case-sensitive pattern splits the body and
        # leaves the contents alone. Verified below: five staves or nothing.
        pattern=r"(?m)^STAVE[ \t]+[IVX]+[ \t]*:",
        chapters=5,
    ),
]

# Project Gutenberg's text host has answered 503 for every text file on some days, so the
# mirrors are tried in order rather than treated as a fallback nobody expects to need.
MIRRORS = (
    "https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt",
    "https://www.gutenberg.org/files/{gid}/{gid}-0.txt",
    "https://mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/{dir}/{gid}-0.txt",
    "https://mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/{dir}/{gid}.txt",
    "https://mirror.csclub.uwaterloo.ca/gutenberg/{dir}/{gid}-0.txt",
    "https://mirror.csclub.uwaterloo.ca/gutenberg/{dir}/{gid}.txt",
)


def gutenberg_dir(gid):
    """PG's directory shape: 46 -> 4/46, 8486 -> 8/4/8/8486, 9629 -> 9/6/2/9629."""
    digits = str(gid)
    return "/".join(list(digits[:-1]) + [digits])


PG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.S)

# Where the book stops. Matched as positions rather than as one lazy pattern, because a
# single `.*` under re.S runs to the end of the file: the old-style footer line sits AFTER
# the licence, so a regex that matched it would cut at the wrong end and leave the licence
# in the corpus. Every marker is tried and the earliest wins; the licence markers are there
# for files that carry no END line at all.
END_MARKERS = (
    re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG"),
    re.compile(r"(?im)^\*END\*[ .]?THE SMALL PRINT"),
    re.compile(r"(?im)^End of (?:the )?Project Gutenberg"),
    re.compile(r"\*\*\*\s*START:?\s*FULL LICENSE"),
    re.compile(r"(?im)^Section\s+1\.\s+General Terms of Use"),
)


def fetch(gid):
    """The raw text, from the first mirror that answers with a book rather than an error page."""
    seen = []
    tried = set()
    for template in MIRRORS:
        candidate = template.format(gid=gid, dir=gutenberg_dir(gid))
        if candidate in tried:
            continue
        tried.add(candidate)
        try:
            with urllib.request.urlopen(candidate, timeout=60) as fh:
                raw = fh.read()
        except Exception as exc:                          # noqa: BLE001
            seen.append("%s: %s" % (candidate, exc))
            continue
        text = decode(raw)
        # 9629 predates the `-0` suffix and is held as the bare `<gid>.txt`; the trailing
        # templates cover it. A page that answers but is not a book is a 404 dressed up as
        # a 200, so the marker is what decides.
        if "PROJECT GUTENBERG" in text.upper():
            return text, candidate
        seen.append("%s: answered, but not with a Gutenberg text" % candidate)
    raise SystemExit("fetch-ghost: no mirror served %d\n  %s" % (gid, "\n  ".join(seen)))


def decode(raw):
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def normalise_newlines(text):
    # Same reason as fetch-multivolume.py: a stray "\\r\\r\\n" becomes a blank line under
    # universal-newline translation, and every wrapped display line then counts as a
    # paragraph. Paragraph CV collapses and it reads as a finding about prose.
    text = text.replace("\r\r\n", "\n").replace("\r\n", "\n").replace("\r", "\n")
    if "\r" in text:
        raise AssertionError("a carriage return survived normalisation")
    return text


def strip_gutenberg(text):
    start = PG_START.search(text)
    if start:
        text = text[start.end():]
    cut = len(text)
    for marker in END_MARKERS:
        found = marker.search(text)
        if found:
            cut = min(cut, found.start())
    body = text[:cut]
    if "PROJECT GUTENBERG" in body.upper() or "gutenberg-tm" in body.lower():
        raise SystemExit("fetch-ghost: the boilerplate strip left Gutenberg text in the body")
    return body.strip()


def norm(line):
    """Case, quotes, spacing and punctuation are typesetting; the words are the heading."""
    return re.sub(r"[^a-z0-9]", "", line.casefold())


def split_titles(text, titles):
    """[(title, body)] cut at each title used as a heading.

    The contents list holds the same strings as the headings, in the same order, so the
    first chain of matches is discarded and the chain that starts latest is taken: the
    contents entry for the first story is followed by every other contents entry, which
    leaves no room for the rest of the chain, and the body heading does.
    """
    lines = text.split("\n")
    found = {}
    for i, line in enumerate(lines):
        key = norm(line)
        if not key:
            continue
        for title in titles:
            if key == norm(title):
                found.setdefault(title, []).append(i)
    missing = [t for t in titles if t not in found]
    if missing:
        return None, "headings not found as whole lines: %s" % "; ".join(missing)

    offsets, at = [], 0
    line_start = [0]
    for line in lines:
        at += len(line) + 1
        line_start.append(at)

    chosen = None
    for start in reversed(found[titles[0]]):
        chain, ok = [start], True
        for title in titles[1:]:
            later = [i for i in found[title] if i > chain[-1]]
            if not later:
                ok = False
                break
            chain.append(later[0])
        if ok:
            chosen = chain
            break
    if chosen is None:
        return None, "the headings appear, but not in contents order"

    offsets = [line_start[i] for i in chosen]
    out = []
    for i, start in enumerate(offsets):
        end = offsets[i + 1] if i + 1 < len(offsets) else len(text)
        out.append((titles[i], text[start:end].strip()))
    return out, None


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")
    return s[:40]


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    out = sys.argv[1]
    works = WORKS
    if "--limit" in sys.argv:
        works = works[:int(sys.argv[sys.argv.index("--limit") + 1])]

    os.makedirs(out, exist_ok=True)
    total_words, staged = 0, 0
    for work in works:
        raw, url = fetch(work["gid"])
        text = strip_gutenberg(normalise_newlines(raw))
        if len(text.split()) < 20_000:
            raise SystemExit("fetch-ghost: %s stripped to %d words - the header or footer "
                             "regex cut the book" % (work["title"], len(text.split())))
        if "pattern" in work:
            hits = list(re.finditer(work["pattern"], text))
            if len(hits) != work["chapters"]:
                raise SystemExit("fetch-ghost: %s split into %d parts, expected %d - the "
                                 "pattern is not the splitter this book uses"
                                 % (work["title"], len(hits), work["chapters"]))
            bounds = [m.start() for m in hits] + [len(text)]
            # The heading is what differs between staves; the stem is not.
            labels = [slug(m.group(0)) for m in hits]
            parts = [(labels[i], text[bounds[i]:bounds[i + 1]].strip())
                     for i in range(len(hits))]
        else:
            parts, problem = split_titles(text, work["titles"])
            if problem:
                raise SystemExit("fetch-ghost: %s: %s" % (work["title"], problem))

        # A re-run must not leave a previous staging beside this one: a renamed story would
        # be measured twice and the lane's document count would be a leftover, not a corpus.
        for stale in sorted(os.listdir(out)):
            if stale.startswith(work["stem"] + "__"):
                os.remove(os.path.join(out, stale))

        print("%s\n  %s" % (work["title"], url))
        work_words = 0
        for i, (label, body) in enumerate(parts, start=1):
            words = len(body.split())
            if words < 400:
                raise SystemExit("fetch-ghost: %s part %d (%s) is %d words - the split cut "
                                 "inside the book" % (work["title"], i, label, words))
            name = "%s__%02d__%s.txt" % (work["stem"], i, slug(label))
            with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)
            work_words += words
            print("  %02d  %6d words  %s" % (i, words, name))
        total_words += work_words
        staged += 1
        print("  -- %d words" % work_words)

    print("\nstaged %d work(s), %d words, %d file(s) in %s"
          % (staged, total_words, len(os.listdir(out)), out))
    print("\nThe rest of the borrow list is in copyright and cannot be fetched (SOURCE_POLICY.md"
          "\ns3): Jackson, Barker, Hill, Ligotti, Barron, Link, Machado, Kingfisher arrive as"
          "\nlocal copies or not at all. LANES.tsv carries the lane as NOT INSTALLED until then.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
