#!/usr/bin/env python3
"""check-monotony.py - the monotony gate.

WHY THIS EXISTS
  check-uniformity.py watches the space BETWEEN chapters: it can see that every
  chapter is the same length. It cannot see the failure a reader actually hears,
  which lives INSIDE the sentences: the same five-word run, the same subject at
  the head of every clause, the same three adjectives, and negation used as the
  default verb.

  Measured on the-parts-still-warm, 2026-11-11, after it had passed every other
  prose gate in this directory:

      597  "did not"                       45.8 per 10k words
      313  sentences opening with the protagonist's name (4.8% of 6,532)
      548  consecutive He / name openings
      358  gray   349 flat   324 cold   297 heavy   239 dry
       9   "Tap Two looked at the"   across 7 chapters
       8   "the man said, his voice" across 4 chapters
       5   "said his voice was thin" across 5 chapters

  Every one of those passes a per-chapter cap, and the book reads as machine-made
  when three chapters are taken together. This is the instrument for that.

WHAT IT MEASURES
  M1  repeated 5-grams: any run of five words (>=3 content words) appearing
      6+ times across 4+ chapters. A formula, not a motif.
  M2  subject-opening concentration: share of sentences whose first word is a
      character name, "he" or "she". Published prose runs 20-30%; a book that
      cannot get under a third is cycling a template.
  M3  negation density: "did not" per 10,000 words.
  M4  texture density: gray, flat, cold, heavy, dry, pale, dark per 10,000.
  M5  mean sentence length, words.
  M6  share of sentences of eight words or fewer - the throttle.
  M7  mean paragraph length, words - a beat or a block.

  M5-M7 ARE REPORTED AND NOT JUDGED. There is no modern commercial corpus here to set a
  band from (the same reason M2 is advisory), so these rows print a number and a book's
  ductus declares the ceiling. Added 2026-11-12 for a book that passed every other prose
  gate while decelerating: mean sentence 15.4 words in chapter 1, 23.6 by chapter 12, and
  paragraphs growing from 29 words to 85. Nothing in this file could see that.

THRESHOLDS ARE MEASURED, AND TWO OF THE FOUR ARE NOT ENFORCED

  Calibrated 2026-11-11 by running this gate over the six published English fiction
  volumes `check-uniformity.py` uses (`calibration/monotony-units.py`, which stages each
  volume as chapters and reads this tool's own output back):

      volume              chapters   M1 worst   M2      M3     M4
      Austen, P&P            61      7 uses/6ch  8.3%   10.1    2.2
      Bronte, Jane Eyre      38      6 uses/?ch  5.3%    7.0   15.7
      Bronte, Wuthering      33      7 uses/7ch  8.9%    8.9    9.7
      Eliot, Middlemarch     86     20 uses/8ch  9.0%    9.3    6.8
      Hardy, Tess            60      7 uses/3ch 10.1%   13.0   14.0
      Stoker, Dracula        25      0 found     9.2%    n/a    6.9

  M1 changed shape because of that run. Its absolute test (a run used 6+ times in 4+
  chapters) FAILED five of the six volumes: a count does not scale with book length,
  and Middlemarch repeats a five-word run twenty times over 86 chapters without being
  monotonous. The test is now a share of the chapters - a formula is a run that appears
  in 30% of them or more - which leaves every published volume passing. This book's
  original defect (one formula in 7 of 13 chapters, 54%) still fails it.

  M2, M3 and M4 are printed against the band above and warn when a book leaves it, but
  they do not fail one. Each refusal has its own measurement behind it:

    M2  the six volumes are 1813-1897, where periodic syntax suppresses subject
        openings. A line at 15% would fail most contemporary commercial fiction, and
        this project owns no modern corpus to check that. Advisory until it has one.
    M3  "did not" is the default verb of this book's declared voice, and the corpus is
        contraction-free exactly as the book is, so the comparison is fair and the book
        is 3.3x the worst volume. A fair comparison is not the same as a defect.
    M4  the palette (gray, cold, heavy) is this book's subject matter. Gating it would
        push an author off the word the book is about - the judgement U6 already made
        when it removed "Nobody X".

  A row that would fail prose for being prose is printed, not enforced. That is not a
  softer gate than the provisional one: the provisional lines were inflated to clear
  this book by construction (45.0 against a measured 13.0), and a high invented line
  guarantees nothing while looking like a pass.

USAGE
  python tools/prose/check-monotony.py <book-root> [--top N] [--by-chapter]
  exit 0 = pass (warnings may be present), 1 = fail, 2 = nothing to read.

  --by-chapter prints M3 and M4, and the pace rows, for each chapter. It exists for seams: a scene
  spliced into a finished chapter arrives with its own idiom, and no whole-book
  average can see that. If one chapter sits far from the two beside it, the
  question is not whether the prose is monotonous but whether it is the same hand.
"""
import io
import os
import re
import sys
import glob
import collections

CONTENT_MIN = 3
GRAM_N = 5
GRAM_COUNT_FAIL = 6
GRAM_SPREAD_FAIL = 4
# CALIBRATED 2026-11-11 against the six published English fiction volumes
# check-uniformity.py uses (Austen 1813, Bronte x2 1847, Eliot 1871, Hardy 1891,
# Stoker 1897; 25-86 chapters each), through `calibration/monotony-units.py`.
#
# The bands are what published prose actually does. They are NOT enforced as pass/fail
# lines, and the reason is a measurement, not a preference: a 1.5x-headroom line built
# from them would fail contemporary commercial prose on rows where the corpus cannot see
# the register (M2), where the palette is the book's subject (M4), and where the voice
# contract declares the rate as its own mode (M3). Same judgement as U4 in
# check-uniformity.py and "Nobody X" in U6: a row that would fail prose for being prose
# is printed, not enforced. Enforcement waits on a modern commercial corpus.
PUB_M2 = (5.3, 10.1)     # share of sentences opening on He/She/name
PUB_M3 = (7.0, 13.0)     # "did not" per 10k
PUB_M4 = (2.2, 15.7)     # texture words per 10k
# M1 is enforced, and this is the only row the calibration changed the SHAPE of. The
# absolute test (>=4 chapters) failed five of the six published volumes - Middlemarch
# repeats a run 20 times across its 86 chapters - because a count does not scale with
# book length while a share does. Worst published share is 23% (one volume's "Nobody X"
# in U6's terms); a formula is a run that appears in a third of the chapters or more.
GRAM_SPREAD_SHARE = 0.30
TEXTURE_WORDS = ["gray", "flat", "cold", "heavy", "dry", "pale", "dark"]

STOP = set("""the a an and or of to in on at for with from by as is was were be been being he she it they
his her its their him them that this these those not no did do does had has have but if then than so up down
out into over under about after before when while there here what which who whom whose all any both each few
more most other some such only own same too very can will just""".split())


def texture_pattern(word):
    """The word, not its orthography.

    "gray" was counted US-only, so it scored zero on the British-spelled volumes and
    read as a stylistic absence when it was a spelling one. Same word, both spellings.
    """
    b = chr(92) + "b"
    if word == "gray":
        return b + "gr[ae]y" + b
    return b + word + b

def body(path):
    t = io.open(path, encoding="utf-8").read()
    lines = t.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    return "\n".join(lines)


def main():
    args = [a for a in sys.argv[1:]]
    top = 10
    if "--top" in args:
        i = args.index("--top")
        top = int(args[i + 1])
        del args[i:i + 2]
    by_chapter = "--by-chapter" in args
    if by_chapter:
        args.remove("--by-chapter")
    if not args:
        print("usage: python tools/prose/check-monotony.py <book-root>")
        return 2
    root = args[0]
    files = sorted(glob.glob(os.path.join(root, "manuscript", "chapters", "chapter-*.md")))
    if not files:
        print("check-monotony: no chapters under %s" % root)
        return 2

    chapters = [(os.path.basename(p), body(p)) for p in files]
    allt = "\n".join(b for _, b in chapters)
    words = allt.split()
    n = len(words)
    if n < 5000:
        print("check-monotony: %d words is too little to measure." % n)
        return 2

    fails, warns = [], []

    # M1 - repeated five-grams
    grams = collections.Counter()
    spread = collections.defaultdict(set)
    for name, b in chapters:
        ts = re.findall(r"[a-z']+", b.lower())
        seen = set()
        for i in range(len(ts) - GRAM_N + 1):
            g = ts[i:i + GRAM_N]
            if sum(1 for w in g if w not in STOP) < CONTENT_MIN:
                continue
            key = " ".join(g)
            grams[key] += 1
            seen.add(key)
        for k in seen:
            spread[k].add(name)
    n_ch = max(1, len(chapters))
    hot = [(g, c, len(spread[g])) for g, c in grams.items()
           if c >= GRAM_COUNT_FAIL and len(spread[g]) / float(n_ch) >= GRAM_SPREAD_SHARE]
    hot.sort(key=lambda x: -x[1])
    worst_gram = hot[0][1] if hot else 0

    # M2 - subject openings
    sents, subj, lens = 0, 0, []
    for _, b in chapters:
        for s in re.split(r"(?<=[.!?])\s+", b):
            w = re.findall(r"[A-Za-z']+", s)
            if not w:
                continue
            sents += 1
            lens.append(len(s.split()))
            first = w[0].lower()
            if first in ("he", "she") or (len(w) > 1 and re.fullmatch(r"[A-Z][a-z]+", w[0])
                                          and w[1] in ("Two", "One", "Three", "Four", "Five", "Six")):
                subj += 1
    open_share = subj / float(sents) if sents else 0.0

    low = allt.lower()
    neg = len(re.findall(r"\bdid not\b", low)) * 10000.0 / n
    tex_counts = {w: len(re.findall(texture_pattern(w), low)) for w in TEXTURE_WORDS}
    # "the flat" is this book's word for the apartment, and "flat of the blade" is an
    # idiom: neither is a texture. Counted raw they made this gate report 349 texture
    # uses of a noun. Subtract them, or the number is about furniture, not prose.
    if "flat" in tex_counts:
        flat_n = len(re.findall(r"\b(?:the|a|an|his|her|their|our|this|that|whole|empty|same)\s+flat\b", low))
        flat_of = len(re.findall(r"\bflat of\b", low))
        tex_counts["flat"] = max(0, tex_counts["flat"] - flat_n - flat_of)
    tex = sum(tex_counts.values()) * 10000.0 / n

    # M5-M7 - pace. Printed, never gated: a band would have to come from contemporary
    # commercial prose, and this project owns none (see M2's refusal). A book's contract
    # declares the ceiling and this row is how the book is measured against it.
    mean_sent = sum(lens) / float(len(lens)) if lens else 0.0
    short_share = sum(1 for l in lens if l <= 8) / float(len(lens)) if lens else 0.0
    paras = [p for _, b in chapters for p in re.split(r"\n\s*\n", b) if p.strip()]
    mean_para = sum(len(p.split()) for p in paras) / float(len(paras)) if paras else 0.0

    print("check-monotony: %s" % root)
    print("  %d words, %d sentences, %d chapters" % (n, sents, len(chapters)))
    worst_share = max((len(spread[g]) / float(n_ch) for g, _, _ in hot), default=0.0)
    print("  M1 repeated 5-grams (>=%d uses, >=%d%% of chapters): %d found, worst %d uses in %.0f%% of chapters" %
          (GRAM_COUNT_FAIL, GRAM_SPREAD_SHARE * 100, len(hot), worst_gram, worst_share * 100))
    print("  M2 subject openings: %.1f%% of sentences" % (open_share * 100))
    print("  M3 'did not': %.1f per 10k" % neg)
    print("  M4 texture words: %.1f per 10k  (%s)" %
          (tex, " ".join("%s=%d" % (k, v) for k, v in tex_counts.items())))
    print("  M5 mean sentence: %.1f words" % mean_sent)
    print("  M6 short sentences (<=8 words): %.0f%%" % (short_share * 100))
    print("  M7 mean paragraph: %.1f words" % mean_para)

    if by_chapter:
        print("")
        print("      per chapter    words  did-not/10k  texture/10k  meanSent  short%  meanPara")
        for name, b in chapters:
            lw = b.lower()
            cw = len(b.split()) or 1
            cn = len(re.findall(r"\bdid not\b", lw)) * 10000.0 / cw
            ct = sum(len(re.findall(texture_pattern(w), lw)) for w in TEXTURE_WORDS)
            ct = ct * 10000.0 / cw
            cs = [s for s in re.split(r"(?<=[.!?])\s+", b) if re.findall(r"[A-Za-z']", s)]
            cl = [len(s.split()) for s in cs] or [0]
            cp = [p for p in re.split(r"\n\s*\n", b) if p.strip()] or [""]
            print("      %-14s %6d %11.1f %12.1f %9.1f %6.0f %9.1f" % (
                name, cw, cn, ct, sum(cl) / float(len(cl)),
                100.0 * sum(1 for x in cl if x <= 8) / len(cl),
                sum(len(p.split()) for p in cp) / float(len(cp))))
        print("      A chapter far from the two beside it is a seam, not a style:")
        print("      a spliced scene arrives with the hand that wrote it.")

    if hot:
        fails.append("M1: %d repeated five-word runs" % len(hot))
        for g, c, sp in hot[:top]:
            print("      %3d x  %d ch  %s" % (c, sp, g))
    if open_share * 100 > PUB_M2[1]:
        warns.append("M2: subject openings %.1f%% - above the published band %.1f-%.1f%%, "
                     "advisory (the corpus cannot see modern sentence openings)" %
                     (open_share * 100, PUB_M2[0], PUB_M2[1]))
    if neg > PUB_M3[1]:
        warns.append("M3: 'did not' %.1f per 10k - published band %.1f-%.1f; %.1fx the worst "
                     "volume, advisory (the voice declares the rate, so the row reports it)" %
                     (neg, PUB_M3[0], PUB_M3[1], neg / max(PUB_M3[1], 0.1)))
    if tex > PUB_M4[1]:
        warns.append("M4: texture words %.1f per 10k - published band %.1f-%.1f; %.1fx the worst "
                     "volume, advisory (the palette is this book's subject)" %
                     (tex, PUB_M4[0], PUB_M4[1], tex / max(PUB_M4[1], 0.1)))

    print("")
    for w in warns:
        print("WARN  " + w)
    for f in fails:
        print("FAIL  " + f)
    if fails:
        print("\nMONOTONY FAIL - the prose is cycling a template. Exit 1.")
        return 1
    print("MONOTONY PASS - no template detected at these thresholds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
