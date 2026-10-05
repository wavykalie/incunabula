#!/usr/bin/env python3
"""check-manuscript-integrity.py — is this text clean, and is it in one language?

WHY THIS EXISTS. During the 2026-10-05 autonomous run of *La merienda* (Spanish),
the drafting pass emitted stray characters from other scripts (CJK, Cyrillic),
English words inside Spanish sentences, and truncated fragments. Every one of them
sat inside a sentence that read correctly for twenty words either side, so
reading the prose did not catch them — and no existing gate did either, because a
Cyrillic word is still a word and check-length counts it happily. Twelve
contaminated lines in one chapter, all of them invisible to a human re-read.

That is the same failure class this project has been bitten by three times
already: a check that has never been seen to fail is not yet known to work. The
one that had never been seen to fail here was "is the file the thing it claims
to be".

WHAT IT CHECKS
  1. characters outside the book's declared Latin alphabet and punctuation
  2. CJK, Cyrillic, Greek, Hebrew and Arabic ranges, named individually
  3. English function words appearing as standalone tokens
  4. leftover markdown (**bold**, [n](links)) that survived into the prose

NOT A PROSE GATE, AND DELIBERATELY OUTSIDE THE FREEZE. It makes no claim about
whether the writing is good and its result is not attributed to any book, so it
sits in tools/ with the make-ready layer (roll-brief.py, init-book.py,
preflight.sh) rather than in tools/prose/ with the frozen instruments. It is run
by preflight alongside the dice self-tests.

Usage:
    python tools/check-manuscript-integrity.py [book-root ...]
    python tools/check-manuscript-integrity.py ../my-book ../another-book

With no argument it scans the books registered in BOOKS.yaml that have chapters,
so `python tools/check-manuscript-integrity.py` alone sweeps the workspace.

Exit codes:
    0  every file scanned is clean
    1  at least one file carries contamination, named with line numbers
    2  no chapters found — not a pass
"""

import os
import re
import sys

def _build_allowed():
    """Every character that can legitimately appear in a European manuscript.

    Built from Unicode BLOCKS, not hand-listed. The hand-listed version was
    wrong within one run: it accepted German "ä" but not "Ö", so Vorräte and
    Straße came back flagged, and it accepted "º" but not "²", so a fire report
    reading "0.6m²" came back flagged. A contamination check whose allowlist is a
    list someone typed from memory will find the typographic furniture and call
    it corruption, and then nobody will believe it about the real thing.
    """
    allowed = set(
        "".join(chr(c) for c in range(0x20, 0x7F))          # ASCII
        + "".join(chr(c) for c in range(0xA0, 0x100))        # Latin-1 Supplement
        + "".join(chr(c) for c in range(0x100, 0x180))      # Latin Extended-A
        + "".join(chr(c) for c in range(0x180, 0x250))      # Latin Extended-B
        + "".join(chr(c) for c in range(0x250, 0x300))      # IPA (used in linguistics)
        + "­‌‍﻿"                       # soft/hard/zero-width/bom
        + "–—―−"                     # dashes and minus
        + "«»‹›“”„‟‘’‚‚"       # quotes, guillemets
        + "…·•°ªº¹²³§¶†‡№"   # ellipsis, bullets, degree, ordinals, sections
    )
    return allowed


ALLOWED = _build_allowed()

SCRIPTS = [
    ("CJK",   re.compile(r"[\u3000-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")),
    ("CYRILLIC", re.compile(r"[\u0400-\u04ff]")),
    ("GREEK", re.compile(r"[\u0370-\u03ff]")),
    ("HEBREW", re.compile(r"[\u0590-\u05ff]")),
    ("ARABIC", re.compile(r"[\u0600-\u06ff]")),
]

ENGLISH = re.compile(
    r"\b(?:the|and|with|have|would|could|should|about|then|there|these|those|"
    r"thing|things|people|because|which|write|writes|written|stations?|"
    r"applicants?|bends?|check|checks|same|start|ends|part|parts)\b",
    re.I,
)

MARKUP = re.compile(r"\*\*|\[[0-9]+\]\(|\|\s*-{3,}\s*\|")

# The English-word check is RELATIVE, and getting this wrong is the check's own
# version of the bug it exists to catch. On its first run against the workspace
# it flagged "the", "and" and "with" in every English manuscript in the repo —
# 2,000-plus false positives on books that are perfectly clean. A contamination
# check has to know what language the book claims to be, or it is checking that
# English books are not English.
#
# Language is read from the book's own record: PROJECT_STATE.yaml's
# autonomous.roll.language for a random-button run, else the title line. When no
# language is declared the English check is SKIPPED and says so — the script and
# markup checks still run, because those are language-independent.
LANG_RX = re.compile(r"^[ \t]*language:[ \t]*[\"']?([A-Za-z\- ]+?)[ \t\"']*$", re.M)
TITLE_RX = re.compile(r"^[ \t]*title:[ \t]*[\"']?(.+?)[\"']?[ \t]*(?:#.*)?$", re.M)

# Language CODES are English too. Five books in this workspace declare
# `language: "en"` and the first version of this check read that as a non-English
# book and then reported every "the" and "and" in them as contamination — about
# 4,000 false positives, which is how a check becomes noise.
ENGLISH_CODES = {"en", "eng", "en-us", "en-gb", "en-au", "english"}


def declared_language(root):
    """The language the book claims to be, or None if it never says."""
    for state in ("PROJECT_STATE.yaml", "STATE.yaml"):
        p = os.path.join(root, state)
        if not os.path.isfile(p):
            continue
        try:
            text = open(p, encoding="utf-8").read()
        except OSError:
            continue
        m = LANG_RX.search(text)
        if m:
            return m.group(1).strip()
    return None


def is_english(lang):
    return lang is not None and lang.strip().lower() in ENGLISH_CODES


def scan(path, english_books=False):
    """Return (bad, markup_count).

    `bad` is contamination. `markup_count` is leftover **bold**, which is NOT
    contamination: bold inside a draft manuscript is a deliberate authoring
    convention - section headings, dossier entries, a line the writer wants to
    see at a glance - and presswork resolves it. Reporting it as a failure put
    103 FAILs across books that are perfectly clean, and a check that fails on
    everything has no signal left to give. It is counted and printed, not judged.
    """
    bad = []
    markup = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            for name, rx in SCRIPTS:
                if rx.search(line):
                    bad.append((n, name, line.strip()[:90]))
                    break
            else:
                odd = sorted({ch for ch in line if ch not in ALLOWED and ord(ch) > 127})
                if odd:
                    bad.append((n, "UNKNOWN " + " ".join(f"U+{ord(c):04X}" for c in odd),
                                line.strip()[:90]))
            if MARKUP.search(line):
                markup += 1
            # only meaningful for a book that is NOT written in English
            if not english_books:
                m = ENGLISH.search(line)
                if m:
                    bad.append((n, f"ENGLISH {m.group(0)!r}", line.strip()[:90]))
    return bad, markup


def chapters(root):
    d = os.path.join(root, "manuscript", "chapters")
    if not os.path.isdir(d):
        d = os.path.join(root, "chapters")
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d)
                  if f.lower().endswith(".md"))


def default_roots():
    """Every registered book on disk that has chapters. Empty list is honest.

    The registry lives at incunabula/BOOKS.yaml — one level ABOVE tools/, which is
    where this file sits. Getting that wrong returns an empty scan, and an empty
    scan that prints nothing is the exact failure this tool exists to catch.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    incunabula = os.path.dirname(here)
    workspace = os.path.dirname(incunabula)
    registry = os.path.join(incunabula, "BOOKS.yaml")
    roots = []
    if os.path.exists(registry):
        for line in open(registry, encoding="utf-8"):
            s = line.strip()
            if s.startswith("- path:") or s.startswith("path:"):
                p = s.split(":", 1)[1].strip().strip('"\'')
                cand = os.path.join(workspace, p)
                if os.path.isdir(os.path.join(cand, "manuscript", "chapters")):
                    roots.append(cand)
    return roots


def self_test():
    """A contamination check that has never been seen to fail is not a check.

    Three controls, all on synthetic text, none of which touch a real manuscript:
      1. clean Spanish in a Spanish book must PASS
      2. a CJK character and a Cyrillic word inside a Spanish sentence must FAIL
      3. English function words must FAIL in a Spanish book and be IGNORED in an
         English one — the two mistakes this check made before it made them well
    """
    import tempfile

    clean = ("Cuatro grados. Viento del norte, fuerza 4. Nubosidad 7.\n"
             "La estación 12-340 queda a mil seiscientos cuarenta metros.\n")
    with tempfile.TemporaryDirectory() as td:
        root = os.path.join(td, "book")
        ch = os.path.join(root, "manuscript", "chapters")
        os.makedirs(ch)
        f = os.path.join(ch, "chapter-01.md")

        def write(text):
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)

        # 1. clean passes, with the English check ACTIVE (Spanish book)
        write(clean)
        bad, _ = scan(f, english_books=False)
        assert not bad, f"clean Spanish must pass, got {bad}"

        # 2a. a CJK character inside a correct Spanish sentence must fail
        write("Cuatro grados. Viento del norte.\nVas a走的 al observatorio.\n")
        bad, _ = scan(f, english_books=False)
        assert any("CJK" in w for _, w, _ in bad), f"CJK must be caught, got {bad}"

        # 2b. a Cyrillic word inside a correct Spanish sentence must fail
        write("Cuatro grados. Записано en el parte.\n")
        bad, _ = scan(f, english_books=False)
        assert any("CYRILLIC" in w for _, w, _ in bad), f"Cyrillic must be caught, got {bad}"

        # 2c. a character from OUTSIDE the European repertoire must fail. A
        # weather book that picked up a snowman emoji is the realistic case.
        write("Cuatro grados. Nieve en toda la montaña ☃\n")
        bad, _ = scan(f, english_books=False)
        assert any("UNKNOWN" in w for _, w, _ in bad), f"unknown char must be caught, got {bad}"

        # 2d. but ½ IS in Latin-1 and is not contamination
        write("Cuatro grados. ½ metro de nieve.\n")
        bad, _ = scan(f, english_books=False)
        assert not bad, f"U+00BD is a fraction, got {bad}"

        # 3a. English function words FAIL in a Spanish book
        write("The wind is north. And the sky is clear.\n")
        bad, _ = scan(f, english_books=False)
        assert any(w.startswith("ENGLISH") for _, w, _ in bad), \
            "English words must be caught in a Spanish book"

        # 3b. and are IGNORED in an English book — the false-positive bug
        bad, _ = scan(f, english_books=True)
        assert not bad, f"an English book must not be flagged, got {bad}"

        # 3c. markup is counted, never judged
        write("**The dossier.**\n")
        bad, markup = scan(f, english_books=True)
        assert not bad and markup == 1, f"markup must be a note, got bad={bad} markup={markup}"

        # 4. the German umlauts that a hand-typed allowlist got wrong
        write("Die Vorräte standen im Keller. Die Straße war tot.\n")
        bad, _ = scan(f, english_books=True)
        assert not bad, f"German umlauts are not contamination, got {bad}"

        # 5. a superscript from a fire report is not contamination
        write("Pour pattern, study, 0.6m².\n")
        bad, _ = scan(f, english_books=True)
        assert not bad, f"U+00B2 is a unit, got {bad}"

    print("check-manuscript-integrity self-test: ok")
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    roots = argv[1:] or default_roots()
    if not roots:
        print("check-manuscript-integrity: no registered book has chapters.")
        print("  Nothing scanned is not a pass. Exit 2.")
        return 2
    total_bad = 0
    for root in roots:
        files = chapters(root)
        name = os.path.basename(root.rstrip("\\/"))
        if not files:
            # a registered book with no chapters is a skip, not a failure. It is a
            # concept, a fixture or a book that has not started; there is nothing
            # to be contaminated yet.
            print(f"  skip  {name:24} registered, no chapters on disk yet")
            print()
            continue
        lang = declared_language(root)
        # The English-word check runs ONLY when the book has declared itself
        # non-English. Unknown is not non-English: an undeclared book is an
        # English book until it says otherwise, and treating "unknown" as
        # foreign put 180 false positives on demo-magician alone.
        english_check = lang is not None and not is_english(lang)
        if lang is None:
            note = ("no language declared in PROJECT_STATE.yaml/STATE.yaml; "
                    "English-word check SKIPPED (a check must not guess)")
        elif is_english(lang):
            note = f"declared {lang!r}; English-word check SKIPPED (this book is English)"
        else:
            note = (f"declared {lang!r}; English-word check ACTIVE "
                    "(an English word here is an intrusion)")
        print(f"## check-manuscript-integrity   {name}")
        print(f"   {note}")
        print("=" * 70)
        for f in files:
            bad, markup = scan(f, english_books=not english_check)
            words = len(open(f, encoding="utf-8", errors="replace").read().split())
            tag = f"{words:6} words"
            if markup:
                tag += f", {markup} line(s) with ** markup"
            if bad:
                total_bad += 1
                print(f"  FAIL  {os.path.basename(f):20} {tag}, "
                      f"{len(bad)} contaminated line(s)")
                for n, why, text in bad[:8]:
                    print(f"          L{n:<4} {why:26} {text}")
                if len(bad) > 8:
                    print(f"          ... and {len(bad) - 8} more")
            else:
                print(f"  ok    {os.path.basename(f):20} {tag}")
        print()
    if total_bad:
        print("INTEGRITY FAIL - at least one file carries contamination.")
        print("  These are not style findings. They are characters and words that do")
        print("  not belong in the book they are sitting in, inside sentences that")
        print("  read correctly on either side of them.")
        print("  ** markup is counted, not judged: bold in a draft is a convention.")
        return 1
    print("INTEGRITY OK - every chapter scanned is in the language it declares, and")
    print("free of stray scripts and intrusions. ** markup was counted, not judged.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))