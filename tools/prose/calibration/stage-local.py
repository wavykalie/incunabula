#!/usr/bin/env python3
"""stage-local.py - cut the literary-horror lane out of copies the author owns.

These eight books are in copyright. They arrive as `local-copy` documents under
SOURCE_POLICY.md s3: lawfully owned, analysed locally, never committed, never redistributed.
Nothing here fetches. It reads `corpus/literary-horror/_source/<stem>.<ext>`, writes one
plain-text document per story or chapter into the lane, and prints what it staged.

WHY A SCRIPT RATHER THAN A ONE-OFF RUN
  Every cap in deslop-check.sh is a per-document rate, so where a document is cut IS the
  measurement. A collection pooled into one 100k-word blob reads a smoother tail than the
  same prose cut at its stories, and nothing in the output would say which had been done.
  The splitter is therefore part of the record, beside fetch-ghost.py.

SPLITTERS
  spine   the epub package already separates the documents; keep them, drop front matter
  titles  one text stream, cut at the collection's own story titles (used for the forms
          that pool: a single-HTML epub, an azw3, a calibre HTML export)
  fb2     FictionBook sections, one per story, minus the back matter

THE TWO `.lit` FILES. Microsoft Reader compresses its text with LZX, and every open-source
reader for it needs a toolchain this machine does not have: convertlit is C, calibre's own
lit reader needs its compiled `calibre_extensions.lzx`, cabriolet is Ruby, eruditio is Rust.
Calibre's `ebook-convert` is the one that runs here, so each .lit is converted ONCE, by
hand, and the epub it produces is what is staged:

    ebook-convert "The Twisted Ones.lit" kingfisher-twisted-ones.epub

Both epubs are in `_source/` beside the .lit. The conversion is not repeated by this script:
re-running it would need calibre present, and the epub is already the record of that step.

usage:  python stage-local.py <lane-dir> [--source DIR] [--limit N]
"""

import html as htmlmod
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXTRACT = load("extract")

# `titles` is the collection's own contents page, in order: the same list that decides what
# counts as a story decides where the document breaks. `labels` is used only where the split
# comes from the package (spine) and the documents arrive without names.
WORKS = [
    dict(stem="barker-books-of-blood-1", ext="epub", split="spine", min_words=1000,
         labels=["The Book of Blood", "The Midnight Meat Train", "The Yattering and Jack",
                 "Pig Blood Blues", "Star Shine", "The Cities"]),
    dict(stem="jackson-haunting-of-hill-house", ext="epub", split="spine"),
    dict(stem="ligotti-teatro-grottesco", ext="epub", split="titles", titles=[
        "Purity", "The Town Manager", "Sideshow, and Other Stories", "The Clown Puppet",
        "The Red Tower", "My Case for Retributive Action", "Our Temporary Supervisor",
        "In a Foreign Town, in a Foreign Land", "Teatro Grottesco", "Gas Station Carnivals",
        "The Bungalow House", "Severini", "The Shadow, the Darkness"]),
    # Fifteen stories, taken from the book's own contents page. The first pass used eight:
    # the copy's front contents list was cut short and six headings were folded into their
    # neighbours, which inflated Best New Horror to 15.5k words and Pop Art to 23.6k. The
    # full list is what the body actually prints, one heading line per story.
    dict(stem="hill-20th-century-ghosts", ext="azw3", split="titles", titles=[
        "Best New Horror", "20th Century Ghost", "Pop Art",
        "You Will Hear the Locust Sing", "Abraham's Boys", "Better Than Home",
        "The Black Phone", "In the Rundown", "The Cape", "Last Breath", "Dead-Wood",
        "The Widow's Breakfast", "Bobby Conroy Comes Back from the Dead",
        "My Father's Mask", "Voluntary Committal"]),
    dict(stem="barron-imago-sequence", ext="html", split="titles", titles=[
        "Old Virginia", "Shiva, Open Your Eye", "Procession of the Black Sloth", "Bulldozer",
        "Proboscis", "Hallucigenia", "They Who Dwell in the Cracks", "Parallax",
        "The Royal Zoo Is Closed"]),
    dict(stem="link-get-in-trouble", ext="fb2", split="fb2",
         drop=["Acknowledgments", "ABOUT THE AUTHOR"]),
    # Converted from .lit by calibre: a novel, so the package's own chapter documents are
    # the unit. The 1,500-word floor drops the author's note and the copyright page.
    dict(stem="kingfisher-twisted-ones", ext="epub", split="spine", min_words=1500),
    # Converted from .lit by calibre: an eight-story collection delivered as six blobs, so
    # its stories are cut out by their own contents page.
    dict(stem="machado-her-body-and-other-parties", ext="epub", split="titles", titles=[
        "The Husband Stitch", "Inventory", "Mothers", "Especially Heinous",
        "Real Women Have Bodies", "Eight Bites", "The Resident", "Difficult at Parties"],
         stop_at=["Acknowledgments", "Document Outline"]),
]

FLOOR = 400          # a story shorter than this is a split that went wrong, not a story


CONTENTS_TAIL = re.compile(r"(?im)^\s*(?:table of contents|contents)\s*$")


def norm(line):
    """Case, quotes, spacing and punctuation are typesetting; the words are the heading."""
    return re.sub(r"[^a-z0-9]", "", line.casefold())


def trim_contents_tail(text):
    """Cut a contents list reprinted at the END of the file.

    A converted azw3 and a calibre HTML export both append the table of contents as a run
    of title lines after the last story. Left in, it is counted as the last story's prose,
    and it also drags in whatever markup the conversion failed to close. Only a marker past
    the halfway point is a tail: a contents page at the FRONT is the splitter's problem,
    and cutting there would delete the book.
    """
    cut = None
    for found in CONTENTS_TAIL.finditer(text):
        if found.start() > len(text) * 0.5:
            # The FIRST marker past the halfway point, not the last: these files print the
            # heading twice ("Table of Contents" and again before the list), and cutting at
            # the second one leaves the first heading and its block in the last story.
            cut = found.start()
            break
    return text if cut is None else text[:cut].rstrip()


def trim_back_matter(text, markers):
    """Cut at a back-matter heading that follows the last story.

    A converted collection ends with acknowledgements and a document outline; left on,
    they are counted as the final story's prose. Line-exact and past the halfway point,
    for the same reason as trim_contents_tail: a heading at the front is the book.
    """
    if not markers:
        return text
    wanted = {norm(m) for m in markers}
    lines = text.split("\n")
    offsets, at = [], 0
    for line in lines:
        offsets.append(at)
        at += len(line) + 1
    for i, line in enumerate(lines):
        if offsets[i] > len(text) * 0.5 and norm(line) in wanted:
            return text[:offsets[i]].rstrip()
    return text


def split_titles(text, titles):
    """[(title, body)] cut at each title used as a heading.

    A collection prints its contents twice - once as a list, once as the headings - and the
    list can sit at either end of the file. So every occurrence of the first title is tried
    as a start, and the chain is kept only if EVERY part is a plausible document. A chain
    that begins in the contents list fails immediately, because its first part is a few
    words long. This replaced "take the last one", which was right for a contents page at
    the front and wrong for the calibre export whose contents page is at the back.
    """
    lines = text.split("\n")
    keys = [norm(t) for t in titles]
    found = {k: [] for k in keys}
    for i, line in enumerate(lines):
        key = norm(line)
        if key in found:
            found[key].append(i)
    missing = [t for t, k in zip(titles, keys) if not found[k]]
    if missing:
        raise SystemExit("  ! headings not found as whole lines: %s" % "; ".join(missing))

    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line) + 1)

    for candidate in found[keys[0]]:
        chain = [candidate]
        for key in keys[1:]:
            later = [i for i in found[key] if i > chain[-1]]
            if not later:
                chain = None
                break
            chain.append(later[0])
        if chain is None:
            continue
        offsets = [starts[i] for i in chain] + [len(text)]
        parts = [text[offsets[n]:offsets[n + 1]].strip() for n in range(len(chain))]
        if all(len(p.split()) >= FLOOR for p in parts):
            return list(zip(titles, parts))
    raise SystemExit("  ! no chain of those headings produces %d whole stories"
                     % len(titles))


def fb2_sections(path, drop):
    """[(title, body)] from a FictionBook, minus the back matter by name."""
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    body = re.search(r"<body>(.*)</body>", raw, re.S)
    if not body:
        raise SystemExit("  ! no <body> in the fb2")
    out = []
    for section in re.findall(r"<section[^>]*>(.*?)</section>", body.group(1), re.S):
        title = re.search(r"<title>(.*?)</title>", section, re.S)
        name = " ".join(re.sub(r"<[^>]+>", " ", title.group(1)).split()) if title else ""
        if not name or name in drop:
            continue
        text = re.sub(r"(?i)</p>", "\n\n", section)
        text = re.sub(r"<[^>]+>", "", text)
        text = htmlmod.unescape(text)
        text = "\n".join(line.strip() for line in text.split("\n"))
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        out.append((name, text))
    return out


def documents(work, path):
    """[(label, text)] - the book cut at its own boundaries."""
    if work["split"] == "spine":
        docs = EXTRACT.epub_docs(path)
        if not docs:
            raise SystemExit("  ! the epub resolved to zero documents")
        floor = work.get("min_words", FLOOR)
        kept = [(label, trim_contents_tail(text)) for label, text in docs
                if len(text.split()) >= floor]
        if "labels" in work:
            if len(kept) != len(work["labels"]):
                raise SystemExit("  ! %d documents over %d words, expected %d named stories"
                                 % (len(kept), floor, len(work["labels"])))
            return list(zip(work["labels"], [t for _l, t in kept]))
        return [(label.split("__")[-1] if label else "doc", text) for label, text in kept]
    if work["split"] == "titles":
        if work["ext"] == "epub":
            text = "\n\n".join(t for _l, t in EXTRACT.epub_docs(path))
        elif work["ext"] in ("azw3", "mobi"):
            text = "\n\n".join(t for _l, t in EXTRACT.mobi_docs(path))
        else:
            text = EXTRACT.to_text(open(path, "rb").read())
        text = trim_back_matter(trim_contents_tail(text), work.get("stop_at", []))
        return split_titles(text, work["titles"])
    if work["split"] == "fb2":
        return fb2_sections(path, work.get("drop", []))
    raise SystemExit("  ! unknown splitter %r" % work["split"])


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.casefold()).strip("-")[:40] or "part"


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    lane = sys.argv[1]
    source = os.path.join(lane, "_source")
    if "--source" in sys.argv:
        source = sys.argv[sys.argv.index("--source") + 1]
    works = WORKS
    if "--limit" in sys.argv:
        works = works[:int(sys.argv[sys.argv.index("--limit") + 1])]

    staged, total = 0, 0
    for work in works:
        path = os.path.join(source, "%s.%s" % (work["stem"], work["ext"]))
        if not os.path.exists(path):
            print("%s\n  - not on disk at %s" % (work["stem"], path))
            continue
        print(work["stem"])
        for stale in sorted(os.listdir(lane)):
            if stale.startswith(work["stem"] + "__"):
                os.remove(os.path.join(lane, stale))
        parts = documents(work, path)
        work_words = 0
        for i, (label, text) in enumerate(parts, start=1):
            words = len(text.split())
            if words < 100:
                raise SystemExit("  ! part %d (%s) is %d words" % (i, label, words))
            name = "%s__%02d__%s.txt" % (work["stem"], i, slug(label))
            with open(os.path.join(lane, name), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            work_words += words
            print("  %02d  %6d words  %s" % (i, words, name))
        total += work_words
        staged += 1
        print("  -- %d words, %d document(s)" % (work_words, len(parts)))

    print("\nstaged %d work(s), %d words" % (staged, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
