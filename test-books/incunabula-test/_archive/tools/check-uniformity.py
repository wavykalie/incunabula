#!/usr/bin/env python3
"""check-uniformity.py - the cross-chapter monotony gate.

WHY THIS EXISTS
  Every other prose check in this directory scans ONE chapter at a time and compares
  its rates to per-1k caps. That structure cannot see the failure that matters most
  in machine-assisted writing: not that any single chapter is wrong, but that all of
  them are the SAME. A book can pass every per-chapter cap and still read as robotic,
  because uniformity lives in the comparison between chapters, and no per-chapter
  check is capable of making one.

  This was measured, not theorised. Two finished books in this project - different
  genres, different lengths, written months apart - were built by the same pipeline
  and came out uniform to a degree published prose never is:

      book                    chapters   word counts            CV
      Sons of Heaven (11 ch)      11     2401 .. 2686          3.2%
      Merope vol. 1  (7 ch)        7     2077 .. 2402          5.8%
      Merope vol. 2  (7 ch)        7     1882 .. 2511         10.8%

  The published control corpus (Wandering Witch, Yen Press, 48 chapters, 177,047
  words) sits at 48.4% / 68.1% / 70.6% CV, with individual chapters running from 466
  to 9,184 words inside a single volume. There is no overlap between the two groups.
  A pipeline that holds every chapter within 3% of its neighbours is not being
  disciplined; it is producing the clearest fingerprint it has.

THRESHOLDS ARE MEASURED
  Same rule as deslop-check.sh: the floor is set below the worst published document
  with headroom, so published prose always passes and only true uniformity fails.

    chapter-length CV   published min 48.4%  ->  FAIL under 30%, warn under 45%
    sentence-length     published min 4.32   ->  FAIL under 3.0,  warn under 4.0
      spread (per-chapter means, max-min, words)
    coda distribution   published 0 of 50 chapters carry the closing coda formula
                                             ->  FAIL above 25% of chapters
    signature frames    published volumes, worst single frame in 23% of chapters
                                             ->  FAIL above 40% of chapters, warn above 30%
    one-sentence        published min 50.3%  ->  FAIL under 35%, warn under 50%
      paragraphs, share
    paragraph-length CV published min 86.9%  ->  FAIL under 55%, warn under 75%

The last two come from the same principle applied to the paragraph: a writer breaks a
paragraph to a single line when the line deserves the white space around it, and lets
paragraphs run where the material runs. Prose with almost no single-line paragraphs and
near-constant paragraph sizes has been laid out by a machine. Measured on the published
control: 50-62% of paragraphs are a single sentence, and paragraph lengths vary by CV
87-89%. One project book came in at 14% and 51%.

U4/U5 ARE SCOPED TO NARRATIVE PROSE, AND THE REASON IS A CALIBRATION LIMIT
The only calibration corpus this project owns is narrative fiction, and paragraph shape
is genre-dependent in a way the other rows are not. Dialogue exchanges manufacture
one-line paragraphs and four-word ones, which is what drives the published figures to
50-62% and to a CV near 90%. An argumentative nonfiction chapter has no reason to do
that: it runs paragraphs where the argument runs, and a low share of one-line paragraphs
in it is a property of the form, not of a machine. Scoping the row is the honest response
to a corpus with no nonfiction in it. The moment a nonfiction corpus is added under
calibration/, these two rows can be given real thresholds and the scope lifted. Until
then a book that declares `positioning: nonfiction` in PROJECT_STATE.yaml has U4 and U5
reported and explained but not failed - and the numbers stay on the page so the trend is
visible rather than hidden.

  The coda check is distributional on purpose. One chapter with a rhetorical close is
  a choice; six chapters out of eleven is a machine habit that no per-chapter rate
  can distinguish from six individual choices.

WHAT IT DOES NOT DO
  It cannot tell a deliberate, justified uniformity from a mechanical one. A novella
  of seven matched movements may legitimately be even. When the numbers fail and the
  author has a reason, the reason goes in RUN_REPORT.md and the row is recorded as
  waived - not silently skipped. Reproducing the same exemption across books is itself
  the pattern this check exists to catch.

  usage:  tools/check-uniformity.py [BOOK_DIR_OR_CHAPTER_DIR ...]
          (no argument = every */manuscript/chapters under the project root)
  exit 0 = PASS (or waived)   exit 1 = uniformity failure, or nothing checkable
"""

import os
import re
import sys
import glob
import statistics as st

MIN_CHAPTERS = 4          # fewer than four chapters cannot show a distribution
CV_FAIL, CV_WARN = 30.0, 45.0
SPREAD_FAIL, SPREAD_WARN = 3.0, 4.0
CODA_SHARE_FAIL = 25.0
ONELINE_FAIL, ONELINE_WARN = 35.0, 50.0
PARACV_FAIL, PARACV_WARN = 55.0, 75.0
FRAME_FAIL, FRAME_WARN = 40.0, 30.0

# U6 - the signature frame.
# This is the check for the failure the user actually reported: a book whose
# chapters are each acceptable but which keeps reaching for the same construction,
# so that the tic stops being a style and becomes a fingerprint. Per-chapter rates
# cannot see it, because one instance per chapter is a low rate in every chapter and
# the tic is only visible in the pattern ACROSS chapters.
#
# Measured on the three published volumes as books: the worst single frame occurs in
# 23% of one volume's chapters ("Nobody X"), and the other two volumes do not put a
# single frame above 20%. The three project books, before this check existed, ran:
#
#   Sons of Heaven   antithesis in 87% of chapters, "which is why" in 40%
#   Merope vol. 1    "I want to be X" in 82%, "that is the" in 73%
#   Merope vol. 2    "I want to be X" in 91%, "that is the" in 91%
#
# The frames below are deliberately the distinctive ones - a stall, a coda, an
# antithesis, a refrain - and not ordinary English. "That is the <noun>" is absent
# for exactly that reason: it is too generic to call a tic.
FRAMES = [
    ("stall", r"I want to be \w+"),
    ("frame-opener", r"Here (?:is|was) what"),
    ("coda-link", r"which is (?:also )?why"),
    ("refrain", r"That is (?:the thing|all)"),
    ("antithesis",
     r"(?:was|were|is|are) not[^.!?]{0,50}[.!?] +(?:It|That|This|He|She|They) (?:was|were|is|are)"),
]
# A frame is a CONSTRUCTION, not a word. "Nobody X" was in the first draft of this
# list and was removed after it fired on Merope vol. 2 in 10 of 11 chapters, because
# it was not measuring a tic at all: being unnoticed is that book's subject, and a
# theme realised in diction will cluster in every chapter that touches it. Leaving it
# in would have pushed the author to stop writing the word the book is about. The
# threshold logic stays the same; the judgement is that a construction counts and a
# content word does not.

# Mirrors CODA_RE in deslop-check.sh. Kept in sync deliberately; if one changes the
# other must, and a mismatch means one of the two gates stops seeing the tic.
CODA = re.compile(
    r"(which|that|this) is (also )?why"
    r"|it is (also )?why"
    r"|that is (what|the) (makes|thing)"
    r"|is the (closest|only|real) thing"
    r"|the (next|following) chapter is"
    r"|which is (the )?position",
    re.I,
)

CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)


def sentences(text):
    text = re.sub(r"^#.*$", "", text, flags=re.M)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 2]


def paragraphs(text):
    text = re.sub(r"^#.*$", "", text, flags=re.M).strip()
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def load(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if CHAPTER.search(name):
            with open(os.path.join(directory, name), encoding="utf-8", errors="ignore") as fh:
                out.append((name, fh.read()))
    return out


def closing_paragraph(text):
    text = re.sub(r"^#.*$", "", text, flags=re.M).strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras[-1] if paras else ""


def resolve(arg):
    """Accept a book dir, a manuscript dir, or a chapter dir.

    The test is per-entry. It used to search one newline-joined string, and because
    CHAPTER is end-anchored and was compiled without re.M, `$` could only match at the
    very end of that string - so the whole thing silently depended on the LAST entry
    that os.listdir happened to return. Adding a subdirectory to the chapters folder
    (a reports/ archive) was enough to make the gate report "no chapters found" on a
    book it had just checked.
    """
    for candidate in (arg, os.path.join(arg, "manuscript"), os.path.join(arg, "manuscript", "chapters")):
        if os.path.isdir(candidate) and any(CHAPTER.search(n) for n in os.listdir(candidate)):
            return candidate
    return None


def declare_nonfiction(book_root):
    """U4/U5 rest on a narrative corpus; nonfiction books carry them as advisory."""
    path = os.path.join(book_root, "PROJECT_STATE.yaml")
    if not os.path.isfile(path):
        return False
    with open(path, encoding="utf-8", errors="ignore") as fh:
        head = fh.read(4000)
    return bool(re.search(r"^\s*(positioning|genre)\s*:\s*\"?[^\n]*nonfiction", head, re.I | re.M))


def check(label, chapters, nonfiction=False):
    words = [len(t.split()) for _, t in chapters]
    means = []
    for _, t in chapters:
        s = sentences(t)
        means.append(st.mean(len(x.split()) for x in s) if s else 0.0)

    cv = 100 * st.pstdev(words) / st.mean(words) if st.mean(words) else 0.0
    spread = max(means) - min(means)
    coda_chapters = [n for n, t in chapters if CODA.search(closing_paragraph(t))]
    coda_share = 100.0 * len(coda_chapters) / len(chapters)

    # Layout: how the prose is broken up. Both of these are averages over the whole
    # manuscript rather than per chapter, because the question is what the book's
    # paragraphs are like, not what one chapter's are like.
    paracvs = []
    onelines = []
    for _, t in chapters:
        plens = [len(p.split()) for p in paragraphs(t)]
        if len(plens) > 2 and st.mean(plens):
            paracvs.append(100 * st.pstdev(plens) / st.mean(plens))
        counts = [len(sentences(p)) for p in paragraphs(t)]
        if counts:
            onelines.append(100.0 * sum(1 for c in counts if c == 1) / len(counts))
    oneline_share = st.mean(onelines) if onelines else 0.0
    para_cv = st.mean(paracvs) if paracvs else 0.0

    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters, {sum(words)} words")
    print("=" * 67)
    print(f"{'ch':<14}{'words':>7}{'mean sentence':>16}")
    for (name, _), w, m in zip(chapters, words, means):
        print(f"{name:<14}{w:>7}{m:>16.1f}")

    failed = 0

    status = "FAIL" if cv < CV_FAIL else ("warn" if cv < CV_WARN else "ok")
    failed += status == "FAIL"
    print()
    print(f"   {status:<5} U1  chapter-length variance  CV {cv:.1f}%  "
          f"(published 48.4-70.6%; fail under {CV_FAIL:.0f}%)")
    print(f"          range {min(words)}-{max(words)} words, ratio {max(words)/max(min(words),1):.2f}x")

    status = "FAIL" if spread < SPREAD_FAIL else ("warn" if spread < SPREAD_WARN else "ok")
    failed += status == "FAIL"
    print(f"   {status:<5} U2  rhythm variance          spread {spread:.2f}  "
          f"(published min 4.32; fail under {SPREAD_FAIL})")

    status = "FAIL" if coda_share > CODA_SHARE_FAIL else "ok"
    failed += status == "FAIL"
    print(f"   {status:<5} U3  coda distribution        {len(coda_chapters)}/{len(chapters)} "
          f"chapters ({coda_share:.0f}%)  (published 0/50; fail above {CODA_SHARE_FAIL:.0f}%)")
    for name in coda_chapters:
        print(f"          - {name}")

    frame_hits = []
    for label, pattern in FRAMES:
        rx = re.compile(pattern, re.I)
        spread = [n for n, t in chapters if rx.search(t)]
        frame_hits.append((label, spread))
    frame_hits.sort(key=lambda kv: -len(kv[1]))
    worst_label, worst = frame_hits[0]
    frame_share = 100.0 * len(worst) / len(chapters)
    status = "FAIL" if frame_share > FRAME_FAIL else ("warn" if frame_share > FRAME_WARN else "ok")
    failed += status == "FAIL"
    print(f"   {status:<5} U6  signature-frame spread   \"{worst_label}\" in {len(worst)}/{len(chapters)} "
          f"chapters ({frame_share:.0f}%)  (published worst 23%; fail above {FRAME_FAIL:.0f}%)")
    for label, spread in frame_hits[1:]:
        share = 100.0 * len(spread) / len(chapters)
        if share > FRAME_WARN:
            print(f"          - \"{label}\" in {len(spread)}/{len(chapters)} chapters ({share:.0f}%)")

    if nonfiction:
        # Narrative-corpus thresholds. Reported, not enforced - see the docstring.
        print(f"   n/a   U4  single-line paragraphs   {oneline_share:.0f}% of paragraphs are one "
              f"sentence  (narrative band 50-62%; advisory: nonfiction book)")
        print(f"   n/a   U5  paragraph-length variance CV {para_cv:.0f}%  "
              f"(narrative band 87-89%; advisory: nonfiction book)")
    else:
        status = "FAIL" if oneline_share < ONELINE_FAIL else ("warn" if oneline_share < ONELINE_WARN else "ok")
        failed += status == "FAIL"
        print(f"   {status:<5} U4  single-line paragraphs   {oneline_share:.0f}% of paragraphs are one "
              f"sentence  (published 50-62%; fail under {ONELINE_FAIL:.0f}%)")

        status = "FAIL" if para_cv < PARACV_FAIL else ("warn" if para_cv < PARACV_WARN else "ok")
        failed += status == "FAIL"
        print(f"   {status:<5} U5  paragraph-length variance CV {para_cv:.0f}%  "
              f"(published 87-89%; fail under {PARACV_FAIL:.0f}%)")

    return failed


def main():
    args = sys.argv[1:]
    targets = []

    if args:
        for arg in args:
            directory = resolve(arg)
            if directory:
                targets.append((arg, directory))
            else:
                print(f"check-uniformity: no chapters found under {arg}")
                return 1
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        found = glob.glob(os.path.join(root, "*", "manuscript", "chapters"))
        if os.path.isdir(os.path.join(root, "manuscript", "chapters")):
            found.append(os.path.join(root, "manuscript", "chapters"))
        for directory in sorted(found):
            label = os.path.basename(os.path.dirname(os.path.dirname(directory)))
            targets.append((label, directory))

    checked = 0
    failures = 0
    for label, directory in targets:
        chapters = load(directory)
        if len(chapters) < MIN_CHAPTERS:
            print(f"check-uniformity: {label} has {len(chapters)} chapters, "
                  f"fewer than {MIN_CHAPTERS} - cannot judge uniformity, skipped")
            continue
        checked += 1
        book_root = os.path.dirname(os.path.dirname(directory))
        failures += check(label, chapters, nonfiction=declare_nonfiction(book_root))
        print()

    if checked == 0:
        print("check-uniformity: nothing checkable - a pass with no books read proves nothing.")
        return 1

    print("=" * 67)
    if failures == 0:
        print(f"UNIFORMITY OK - {checked} manuscript(s) vary like human prose.")
        return 0
    print(f"UNIFORMITY FAILURE - {failures} row(s) across {checked} manuscript(s).")
    print("Chapters are too alike to have been written by a person moving through a book.")
    print("Vary chapter length deliberately; break the rhythm profile between chapters;")
    print("stop closing chapters with an explanatory coda. If a book is uniform by")
    print("design, record the reason in RUN_REPORT.md - do not skip the row.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
