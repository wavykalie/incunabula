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

  The published control corpus this floor was FIRST derived from was a light novel
  (Wandering Witch, Yen Press, 48 chapters, 177,047 words) at 48.4% / 68.1% / 70.6% CV,
  with chapters from 466 to 9,184 words inside one volume. That is a translated
  Japanese light-novel register with short interludes, and it is not the register this
  pipeline writes.

  Re-measured against six published ENGLISH FICTION volumes, split on real chapter
  headings (Austen, the Brontes x2, Eliot, Hardy, Stoker; 25-86 chapters each), U1 gives:

      Pride and Prejudice  61 ch   43.0%      Jane Eyre       38 ch   39.7%
      Wuthering Heights   33 ch   45.1%      Middlemarch     86 ch   43.5%
      Tess                 60 ch   33.4%      Dracula         25 ch   42.2%

  The worst is 33.4%, not 48.4%, and the old 45% warn line sat ABOVE five of these six -
  the gate was warning on the human canon it was supposed to be calibrated against. The
  old 30% floor also gave only 1.11x headroom against the worst real novel, against this
  project's own 1.5x convention. Both numbers are re-derived below.

  There is still no overlap with the project books (3.2% / 5.8% / 10.8%). A pipeline
  that holds every chapter within 3% of its neighbours is not being disciplined; it is
  producing the clearest fingerprint it has.

THRESHOLDS ARE MEASURED
  Same rule as deslop-check.sh: the floor is set below the worst published document
  with headroom, so published prose always passes and only true uniformity fails.

    chapter-length CV   published fiction min 33.4%  ->  FAIL under 22%, warn under 28%
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

U4/U5 ARE A PUBLISHING CONVENTION, NOT A LAW OF HUMAN PROSE
  A much larger independent measurement contradicts these two rows' direction, and the
  contradiction is worth more than the rows. VERMILLION (vermillion-study/, 140 public-domain
  English novels, 13.04M words, 185 machine texts, controlled for genre, period and length)
  measures short-paragraph frequency - this project's U4 - running the OTHER way: AUC 0.715
  for the MACHINE side. Machine prose in that corpus carries MORE one-line paragraphs than
  human prose does. The human figures there are 19th-century novels, which predate the
  convention entirely; the machine figures are Royal Road serialisation, which runs on it.

  Both measurements are right about their corpora, and the disagreement is the finding.
  U4's 50-62% is a property of dialogue-dense commercial fiction aimed at the current
  market - the corpus it was calibrated on. It is not a property of English prose, and a
  book outside that market can sit far below 50% without being laid out by a machine.

  So the thresholds are unchanged and the labels are not. U4 and U5 are labelled as market
  convention at the point of use, because the failure mode is not a wrong number here - it
  is this row being generalised into a rule about writing. A check that reads as a law gets
  obeyed in a book it does not describe. See CALIBRATION.md, "U4/U5 are a convention".

  U4 IS ADVISORY UNLESS THE BOOK DECLARES THE CONVENTION
  The argument above was then measured, using this file's own arithmetic over the 140
  public-domain English novels in ../vermillion-study/corpus (13,061,961 words):

      U4  one-sentence paragraph share   min 11.0  q25 27.0  MEDIAN 33.2  q75 39.3  max 77.9
      U5  paragraph-length CV            min 57    q25 88    MEDIAN 101   q75 113   max 189

  U4's own failure line is 35%. Its MEDIAN on the human canon is 33.2%, and 82 of 140 novels
  (59%) fall below it. Five real novels sit at 11.0, 12.3, 13.4, 13.6 and 14.0 per cent. A
  gate that fails three novels in five is not measuring a defect, so U4 no longer fails
  anything by default: the number is printed, both conventions are printed, and the reader
  judges. A book that wants the market row declares

      paragraph_convention: commercial-dialogue      # in PROJECT_STATE.yaml

  and gets it enforced exactly as before. Nonfiction books already carried U4 as advisory;
  that is unchanged.

  An automatic trigger was tried and rejected on evidence. The obvious mechanism is that
  dialogue manufactures one-line paragraphs, so the gate could scope itself to books with
  enough of them. Measured across the same 140 novels, the correlation between the share of
  paragraphs that are entirely speech and the one-sentence share is r = 0.234 - speech
  density does not predict the row. (The 19th-century canon is dialogue-sparse and still
  reaches 77.9%.) So there is no measured basis for an automatic cut, and an unmeasured one
  is the one thing this directory's own README forbids.

  U5 STAYS ENFORGED, AND IT IS NOW THE PROVEN ROW
  The same 140 novels return 0 failures and 14 warnings against U5's 55%/75% lines. Across
  five eras and 13M words of human prose, flat paragraph layout never once appeared - and
  machine prose is the flat one in every corpus measured, on this project and on
  VERMILLION's independently. Variation survives every control. Sameness does not.

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
# Chapter-length CV. The floor is 1.5x below the worst published ENGLISH FICTION volume
# measured (Tess of the d'Urbervilles, 33.4% over 60 real chapters), and the warn line
# sits below that worst case so published prose never warns. It previously read 30/45
# against a light-novel corpus, which warned on five of six English novels.
CV_FAIL, CV_WARN = 22.0, 28.0
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


def declare_convention(book_root):
    """Read the book's declared paragraph convention. Returns one of:
         "nonfiction"          - an argument, not a scene; U1, U4 and U5 all advisory
         "commercial-dialogue" - the dialogue-dense market U4 was calibrated on; U4 enforced
         "default"             - narrative, undeclared; U4 ADVISORY, U5 enforced

    The default was changed deliberately and the evidence is in CALIBRATION.md,
    "U4 is advisory by default". In short: U4's direction is not a law of prose. It
    measures 50-62% on the calibration corpus and a median of 33.2% - below its own
    failure line - across 140 public-domain English novels, 13.06M words. 82 of those
    140 (59%) would fail. A gate that fails three novels in five is not measuring a
    defect, so the burden of proof moves to the book: declare the convention to be held
    to the market row, or get the number reported and the market signal anyway.
    """
    path = os.path.join(book_root, "PROJECT_STATE.yaml")
    convention = "default"
    if os.path.isfile(path):
        with open(path, encoding="utf-8", errors="ignore") as fh:
            head = fh.read(4000)
        if re.search(r"^\s*(positioning|genre)\s*:\s*\"?[^\n]*nonfiction", head, re.I | re.M):
            convention = "nonfiction"
        else:
            # An explicit opt-in, declared by the book. Only "commercial-dialogue"
            # reinstates the gate; any other value is a declaration of something else
            # and leaves U4 advisory.
            m = re.search(r"^\s*paragraph_convention\s*:\s*\"?([^\n\"]*)", head, re.I | re.M)
            if m and m.group(1).strip().lower().replace("_", "-") in ("commercial-dialogue",
                                                                       "commercial dialogue"):
                convention = "commercial-dialogue"
    return convention


def check(label, chapters, convention="default"):
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
    # U1 is a SCENE-shaped row: a chapter in a novel runs as long as its scene does. Six
    # published English fiction volumes give 33.4-45.1% CV. Published NON-FICTION does not
    # behave that way - a chapter on a species runs as long as the argument does - and
    # measures 28.2-113.7% over six volumes from five authors, with Darwin's Journal of
    # Researches at 28.2% sitting between the two bands. One floor cannot serve both, so
    # U1 joins U4 and U5 as advisory on a declared nonfiction book, number still printed.
    if convention == "nonfiction" and status in ("FAIL", "warn"):
        print()
        print(f"   --    U1  chapter-length variance  CV {cv:.1f}%  (fiction band 33.4-45.1%; "
              f"advisory on a nonfiction book)")
        print(f"          range {min(words)}-{max(words)} words, ratio {max(words)/max(min(words),1):.2f}x")
        print("          measured: published non-fiction spans 28.2-113.7% CV, so this row")
        print("          is a statement about scenes and not about arguments.")
        status = "ok"
    else:
        failed += status == "FAIL"
        print()
        print(f"   {status:<5} U1  chapter-length variance  CV {cv:.1f}%  "
              f"(published fiction 33.4-45.1%; fail under {CV_FAIL:.0f}%, warn under {CV_WARN:.0f}%)")
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

    # U4 and U5 both rest on a narrative corpus, and the two rows now have different
    # standing inside it: U5 is enforced, U4 is not unless the book opts in.
    enforce_u4 = convention == "commercial-dialogue"
    enforce_u5 = convention in ("default", "commercial-dialogue")

    if enforce_u4:
        status = "FAIL" if oneline_share < ONELINE_FAIL else ("warn" if oneline_share < ONELINE_WARN else "ok")
        failed += status == "FAIL"
        print(f"   {status:<5} U4  single-line paragraphs   {oneline_share:.0f}% of paragraphs are one "
              f"sentence  (declared commercial-dialogue: market convention 50-62%, "
              f"fail under {ONELINE_FAIL:.0f}%)")
    else:
        why = "nonfiction book" if convention == "nonfiction" else "no convention declared"
        print(f"   n/a   U4  single-line paragraphs   {oneline_share:.0f}% of paragraphs are one "
              f"sentence  (advisory: {why})")
        print(f"          market convention 50-62% (fail under {ONELINE_FAIL:.0f}%, "
              f"warn under {ONELINE_WARN:.0f}%)")
        print(f"          19th-c. English novels: median 33.2%, 59% below {ONELINE_FAIL:.0f}% - "
              f"so this row")
        print(f"          does not generalise, and the number above is yours to judge. "
              f"Declare")
        print(f"          paragraph_convention: commercial-dialogue in PROJECT_STATE.yaml to "
              f"hold it to the")
        print(f"          market gate. Full reasoning: CALIBRATION.md, 'U4 is advisory by default'.")

    if enforce_u5:
        status = "FAIL" if para_cv < PARACV_FAIL else ("warn" if para_cv < PARACV_WARN else "ok")
        failed += status == "FAIL"
        print(f"   {status:<5} U5  paragraph-length variance CV {para_cv:.0f}%  "
              f"(fail under {PARACV_FAIL:.0f}%, warn under {PARACV_WARN:.0f}%)")
        print(f"          ^ enforced. 0 of 140 public-domain English novels (13.06M words, five "
              f"eras)")
        print(f"            fall below the failure line, and machine prose is the flat one in "
              f"every")
        print(f"            corpus measured. Flat paragraph layout is the transferable tell; "
              f"the one-line")
        print(f"            share is not.")
    else:
        print(f"   n/a   U5  paragraph-length variance CV {para_cv:.0f}%  "
              f"(narrative band 87-89%; advisory: nonfiction book)")

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
        failures += check(label, chapters, convention=declare_convention(book_root))
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
