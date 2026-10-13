#!/usr/bin/env python3
"""fetch-multivolume.py - build the multi-volume corpus the controls need.

`validate-controls.sh` controls 4-7 have never run. They want a corpus staged as
`<stem>-v01__chapter-NN.txt`: several VOLUMES, each already split into chapter files,
because `check-uniformity.py` and `check-drift.py` compare chapters *inside* a book and a
single pooled directory would measure variance across books instead of within one.

The three published volumes those gates were originally calibrated on are not shipped -
they are commercial prose. This fetches a substitute from Project Gutenberg: published
English fiction, multiple authors, 1813-1925, which is the oldest corpus the law makes
freely available. It is NOT a replacement for the original calibration, and `PRINTERS_COPY.md`
already records that a 19th-century sample measures the century as much as the prose. What
it buys is that four controls stop being permanently unrunnable.

The copyright wall is real and this does not climb it: nothing published recently is
freely available, so a *current* commercial corpus remains a procurement problem. What is
achievable is format and breadth, and that is what this does.

usage:  python fetch-multivolume.py <out-dir> [--set fiction|nonfiction|prescriptive] [--limit N]
"""

import os
import re
import sys
import urllib.request

# Published English fiction, spread of authors and of the nineteenth century. Chosen for
# being unambiguously commercial narrative rather than a treatise, and for covering
# several authors so the corpus is not one voice measured repeatedly.
BOOKS = [
    (1342, "austen-pride", "Austen, Pride and Prejudice, 1813"),
    (1260, "bronte-jane-eyre", "Bronte, Jane Eyre, 1847"),
    (768, "bronte-wuthering", "Bronte, Wuthering Heights, 1847"),
    (145, "eliot-middlemarch", "Eliot, Middlemarch, 1871"),
    (110, "hardy-tess", "Hardy, Tess of the d'Urbervilles, 1891"),
    # 209 is Dracula; 120 is Treasure Island; 345 is Great Expectations; 4300 is Ulysses.
    (209, "stoker-dracula", "Stoker, Dracula, 1897"),
    (120, "stevenson-treasure", "Stevenson, Treasure Island, 1883"),
    (1400, "dickens-great-expectations", "Dickens, Great Expectations, 1861"),
    (345, "dickens-oliver-twist", "Dickens, Oliver Twist, 1838"),
    (1661, "shelley-frankenstein", "Shelley, Frankenstein, 1818"),
    (98, "twain-tom-sawyer", "Twain, The Adventures of Tom Sawyer, 1876"),
    (74, "twain-huckleberry", "Twain, Adventures of Huckleberry Finn, 1884"),
    (25447, "doyle-hound", "Doyle, The Hound of the Baskervilles, 1902"),
    (2852, "wells-time-machine", "Wells, The Time Machine, 1894"),
    (35, "twain-adam", "Twain, The Adventures of Adam, 1902"),
]

# Published ENGLISH NON-FICTION with real chapter structure, chosen so the paragraph and
# chapter geometry is recoverable. This set exists to answer one question: which of the
# gates, all of which were calibrated on nineteenth-century FICTION, survive contact with
# argumentative prose?
#
# Argumentative chapters have no reason to vary in length the way a scene does - a chapter
# on 'Of the Origin of Species' runs as long as its argument does. If `U1` (chapter-length
# variance) fails here, that is a real limit of a fiction-calibrated gate, and finding it
# costs one download rather than one 28,000-word book.
NONFICTION = [
    (3704, "darwin-beagle", "Darwin, Journal of Researches, 1839"),
    (23, "douglass-narrative", "Douglass, Narrative of a Life, 1845"),
    (1228, "darwin-origin", "Darwin, On the Origin of Species, 1859"),
    (2300, "darwin-descent", "Darwin, The Descent of Man, 1871"),
    (2055, "dana-two-years", "Dana, Two Years Before the Mast, 1832"),
    (3300, "smith-wealth", "Smith, The Wealth of Nations, 1776"),
    (23962, "muir-mountains", "Muir, The Mountains of California, 1894"),
    (3086, "ruskin-unto-this-last", "Ruskin, Unto This Last, 1862"),
]

# Published English PRESCRIPTIVE prose - self-help, parenting, pedagogy - the register
# of the two demo genres. The set above is NARRATIVE nonfiction: travel, memoir, science
# written as argument. This set is the register that tells the reader what to DO, and it
# is the honest test of rows calibrated on nineteenth-century fiction: an advice book
# enumerates, exhorts, and closes chapters on counsel, and a row that accuses it for that
# is a row that needs the convention mechanism - not a book that needs rewriting.
#
# All seven are US-public-domain (published 1762-1912), which is the copyright wall and
# also the caveat: the modern self-help register (Carnegie and after) is not in this set
# and cannot be until it ages into the public domain. A row that misfires here misfires
# on modern advice prose too; a row that passes here is NOT proven clean on a 2020s
# parenting book. CALIBRATION.md section 20 states both directions.
#
# Chavasse does not chapter into this corpus's unit - it is a Q&A handbook whose sections
# are topic headings and whose numbered questions would each fall under the 600-word
# floor - so it stages whole as __flat.txt and is measured at whole-book granularity.
# Named rather than dropped: it is the parenting volume, and a register sweep for the
# parenting demo genres that quietly omits parenting is not a sweep.
PRESCRIPTIVE = [
    (935, "smiles-selfhelp", "Smiles, Self-Help, 1859"),
    (21291, "marden-pushing", "Marden, Pushing to the Front, 1894"),
    (16287, "james-talks", "James, Talks to Teachers, 1899"),
    (2274, "bennett-24-hours", "Bennett, How to Live on 24 Hours a Day, 1908"),
    (39863, "montessori-method", "Montessori, The Montessori Method, 1912"),
    (6595, "chavasse-mother", "Chavasse, Advice to a Mother, 1878"),
    (5427, "rousseau-emile", "Rousseau, Emile, 1762"),
]

SETS = {"fiction": BOOKS, "nonfiction": NONFICTION, "prescriptive": PRESCRIPTIVE}

# Gutenberg's own header/footer, stripped so it is not counted as prose.
PG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.S)
PG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.S)

# Chapter headings. Deliberately several shapes: no single pattern covers English
# chapter headings across two centuries of publishing, and a book split at the wrong
# places produces a corpus that is not a corpus.
CHAPTER_HEADS = [
    re.compile(r"(?m)^\s*(CHAPTER|Chapter)\s+([IVXLCDM]+|\d+)[^\n]{0,60}$"),
    re.compile(r"(?m)^\s*([IVXLCDM]+)\s*$"),
    # Dotted numerals: Victorian scientific prose marks sections "I." and "II." rather
    # than "CHAPTER I", and Ruskin's Unto This Last is entirely built from them.
    re.compile(r"(?m)^\s*([IVXLCDM]{1,7})\.\s*$"),
    re.compile(r"(?m)^\s*(\d{1,2})\.\s*$"),
]

# Heading shapes for the PRESCRIPTIVE set only. Not shared: every attempt to fold these
# into CHAPTER_HEADS changed how the fiction and nonfiction sets stage (a wrapped prose
# initial - Darwin's "C. C. Sprengel has shown" - is flush-left roman + period + capital,
# and one draft of this pattern split Wealth of Nations into 41 chapters and Sherlock
# Holmes into 15). The sets are curated lists already; a curated heading shape per set is
# the same kind of curation, and it leaves fiction and nonfiction byte-identical BY
# CONSTRUCTION rather than by verification.
#
# "I. PSYCHOLOGY AND THE TEACHING ART" (James, Talks to Teachers): roman numeral, period,
# same-line ALL-CAPS title. Four restraints, each one earned:
#   - flush-left (no leading whitespace): TOC lines and legal sub-enumerations indent.
#   - [ \t] not \s after the period: \s reaches across a newline and re-matches the
#     bare-numeral shape in CHAPTER_HEADS.
#   - ALL-CAPS title body: a wrapped sentence starting "C. C. Sprengel has shown" is
#     mixed-case and cannot match; a talk heading is set in caps and cannot miss.
#   - no digit requirement: the numerals are the shape the books actually use.
PRESCRIPTIVE_HEADS = [
    re.compile(r"(?m)^([IVXLCDM]{1,7})\.[ \t]+[A-Z][A-Z ,'-]+$"),
]

MIN_CHAPTER_WORDS = 600


def fetch(gut_id):
    url = f"https://www.gutenberg.org/cache/epub/{gut_id}/pg{gut_id}.txt"
    with urllib.request.urlopen(url, timeout=60) as fh:
        raw = fh.read()
    # Decode WITHOUT universal newlines, and normalise the line endings by hand.
    #
    # Some Project Gutenberg files carry stray carriage returns, so a line ends "\r\r\n".
    # Opened in text mode, Python's universal-newline translation turns that "\r" into an
    # extra "\n" - a BLANK LINE between every hard-wrapped display line. Every wrapped
    # line then becomes its own paragraph, paragraph count triples, and the paragraph-length
    # CV this corpus exists to measure collapses from ~110% to ~32%. It looks like a
    # finding about English prose and is really a bug about file handles.
    text = raw.decode("utf-8", "replace")
    text = text.replace("\r\r\n", "\n").replace("\r\n", "\n").replace("\r", "\n")
    if "\r" in text:
        raise AssertionError("a carriage return survived normalisation")
    return text


def strip_gutenberg(text):
    text = PG_START.sub("", text, count=1)
    text = PG_END.sub("", text, count=1)
    return text


def split_chapters(text, minimum=MIN_CHAPTER_WORDS, extra_heads=()):
    """Split on chapter headings, merging runs that are too short to be a chapter.

    A heading followed by a paragraph of two lines would otherwise become a 'chapter'
    and every cross-chapter statistic would be measuring that artefact.
    """
    marks = []
    for rx in tuple(CHAPTER_HEADS) + tuple(extra_heads):
        for m in rx.finditer(text):
            marks.append(m.start())
    if not marks:
        return None
    marks = sorted(set(marks))
    # Drop a leading mark before any real body text.
    if marks[0] < 2000:
        marks = marks[1:]
    if len(marks) < 2:
        return None
    out = []
    for i, start in enumerate(marks):
        end = marks[i + 1] if i + 1 < len(marks) else len(text)
        body = text[start:end].strip()
        if len(body.split()) >= minimum:
            out.append(body)
    if len(out) < 3:
        return None
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    out = sys.argv[1]
    which = "fiction"
    if "--set" in sys.argv:
        which = sys.argv[sys.argv.index("--set") + 1]
    if which not in SETS:
        print(f"unknown set {which!r}; choose from {', '.join(SETS)}")
        return 2
    books = SETS[which]
    limit = len(books)
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    os.makedirs(out, exist_ok=True)
    staged, skipped = 0, []

    print(f"set: {which}")
    for vol, (gid, stem, title) in enumerate(books[:limit], start=1):
        vol_tag = f"v{vol:02d}"
        try:
            raw = fetch(gid)
        except Exception as exc:                      # noqa: BLE001
            skipped.append(f"{stem}: fetch failed ({exc})")
            continue
        text = strip_gutenberg(raw)
        chapters = split_chapters(text, extra_heads=(
            PRESCRIPTIVE_HEADS if which == "prescriptive" else ()))
        if not chapters:
            words = len(text.split())
            skipped.append(f"{stem}: no usable chapter headings "
                           f"({words} words kept for reference)")
            with open(os.path.join(out, f"{stem}-{vol_tag}__flat.txt"), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            continue
        for i, chapter in enumerate(chapters, 1):
            # newline="" so the line endings written are the ones decided above, and a
            # reader opening these files in text mode sees exactly this.
            with open(os.path.join(out, f"{stem}-{vol_tag}__chapter-{i:02d}.txt"),
                      "w", encoding="utf-8", newline="\n") as fh:
                fh.write(chapter)
        staged += 1
        print(f"  {vol_tag}  {title:<45} {len(chapters):>3} chapters")

    files = len(os.listdir(out))
    print()
    print(f"staged {staged} volumes as {files} files in {out}")
    if skipped:
        print()
        print("not usable as chaptered volumes (kept whole where possible):")
        for s in skipped:
            print("  -", s)
    print()
    print("Point the controls at it:")
    print(f'    HUMAN_CORPUS=<abs path to> bash validate-controls.sh')
    return 0


if __name__ == "__main__":
    sys.exit(main())
