#!/usr/bin/env python3
"""features.py - the frozen per-book feature extractor for the 50-novel study.

One script, one version, every number in the report traceable to a run of it on a filed
text (design §9.2). The regexes, lexicons and splitters are **imported from the shipped
gates**, not re-derived, for the reason `calibration/arc-units.py` states: a copy is free
to drift, and a drifted copy measures something the gate does not measure. This repo has
already shipped four defects of that exact shape (a truncated valence lexicon, a different
tokenizer, the wrong analysis window, a filtered machine corpus).

What "frozen" means here: the constants in this file, together with the pre-registered
feature list in `PREREGISTRATION.md`, are hashed at freeze time. Changing a regex after
generation is a protocol deviation, not an edit.

VERSION 2 (2026-11-06) is such a deviation, requested and recorded in `DECISIONS.md`: the
dialogue-tag window now ends at the next opening quote, and the weather lexicography no
longer counts body/object temperature, interior heating or capitalised proper nouns. The
v1 values are unchanged in `features/` and reproducible from the commit that wrote them;
v2 is written to `features-v2/` and never overwrites them.

FEATURE NAMES ENCODE THEIR FAMILY AND THEIR UNIT:
    lex_  lexical      syn_  syntax      str_  structure
    nme_  names        (cross-book rows are computed in analysis/analyze.py)
    *_per_1k            a rate per 1,000 analysis words
    *_share             a proportion, 0-1, printed as a proportion everywhere
    *_words             an absolute word count
    *_cv                a coefficient of variation, in percent

Rows that this repo has already measured as nulls or backwards (design §8.1-8.3) are
still extracted, because re-measuring them costs nothing here and the study wants the
replication. They are marked in `FEATURES` with `replication=True` and are NOT primary
endpoints; see study/REDTEAM.md B2.

usage:
    python features.py BOOK_DIR_OR_FILE            one book, prints and writes JSON
    python features.py --all BOOKS_ROOT [--out D]  every immediate subdirectory
    python features.py --selfcheck                 constants and import sanity
    python features.py --list                      the feature registry
"""

import argparse
import glob
import importlib.util
import json
import os
import re
import statistics as st
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PROSE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROSE)          # check-uniformity.py imports `conventions`


def _load(modname, filename):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(PROSE, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


arc = _load("check_arc", "check-arc.py")
uni = _load("check_uniformity", "check-uniformity.py")
tags = _load("check_dialogue_tags", "check-dialogue-tags.py")
nme = _load("check_names", "check-names.py")
measure = _load("measure", os.path.join("calibration", "measure.py"))

# ------------------------------------------------------------------ registry
# v2 notes: `syn_tag_breath_share` and `str_open_weather_share` were re-read after the
# first measurement showed the v1 window and lexicon were counting things they did not
# define. Both keep their name and their pre-registered direction.
# direction: "lower" = lower is more human / "higher" = higher is more human /
#            "twosided" = distance from the human median matters, sign does not /
#            "none" = a book-level outcome, not a paired feature.
# replication=True: a row this repo has already measured as a null or with the opposite
# sign (REDTEAM.md B2). Extracted, reported, never a primary endpoint.
FEATURES = {}


def _f(name, family, direction="lower", replication=False, note=""):
    FEATURES[name] = {"family": family, "direction": direction,
                      "replication": replication, "note": note}


# lexical
_f("lex_ai_term_hits", "lexical", note="pooled count of the §8.1 starter list")
_f("lex_ai_terms_per_1k", "lexical")
_f("lex_ly_adverbs_per_1k", "lexical", note="the repo's -ly row, document rate")
_f("lex_hedges_per_1k", "lexical")
_f("lex_opener_and_share", "lexical")
_f("lex_opener_but_share", "lexical")
_f("lex_opener_as_share", "lexical")
_f("lex_opener_when_share", "lexical")
_f("lex_opener_suddenly_share", "lexical")
_f("lex_opener_top1_share", "lexical")
_f("lex_ttr_rarefied", "lexical", direction="twosided", replication=True,
   note="length-confounded unrarefied; machine prose measures MORE varied")
# syntax
_f("syn_sent_words_mean", "syntax", direction="twosided")
_f("syn_sent_words_median", "syntax", direction="twosided")
_f("syn_sent_words_sd", "syntax", direction="twosided", replication=True,
   note="burstiness; measured null within document, see U2 across chapters")
_f("syn_short_sent_share", "syntax", direction="twosided")
_f("syn_long_sent_share", "syntax", direction="twosided")
_f("syn_em_dash_per_1k", "syntax", direction="twosided", replication=True,
   note="D1 report-only: AI control sits inside the published distribution")
_f("syn_semicolon_per_1k", "syntax", direction="twosided")
_f("syn_colon_per_1k", "syntax", direction="twosided")
_f("syn_exclamation_per_1k", "syntax")
_f("syn_ellipsis_per_1k", "syntax", direction="twosided")
_f("syn_dialogue_share", "syntax", direction="twosided")
_f("syn_tag_said_share", "syntax", direction="twosided")
_f("syn_tag_breath_share", "syntax",
   note="v2: tag window ends at the next opening quote")
_f("syn_correlative_per_1k", "syntax", replication=True,
   note="A5 measured on normal English at 0.61/1k in published prose")
_f("syn_passive_proxy_per_1k", "syntax", note="aux+participle proxy, over-counts adjectival passives")
_f("syn_commas_per_sentence", "syntax", direction="twosided")
_f("syn_para_words_mean", "syntax", direction="twosided")
_f("syn_para_cv", "syntax", direction="higher", note="U5: 0 of 140 published novels fail it")
_f("syn_oneline_para_share", "syntax", direction="twosided", replication=True,
   note="U4: 140-novel median 33.2%, opposite direction from this project's register")
_f("syn_chapter_sentlen_spread", "syntax", direction="higher", note="U2, across chapters")
# structure
_f("str_chapters", "structure", "none")
_f("str_words", "structure", "none")
_f("str_chapter_cv", "structure", direction="higher", note="U1, chapter length")
_f("str_chapter_min", "structure", "none")
_f("str_chapter_max", "structure", "none")
_f("str_open_wake_share", "structure", direction="twosided")
_f("str_open_weather_share", "structure", direction="twosided",
   note="v2: atmospheric only; no object/body temperature, no proper nouns")
_f("str_open_time_share", "structure", direction="twosided")
_f("str_open_habitual_share", "structure", direction="twosided")
_f("str_coda_share", "structure", direction="lower", note="F1: 0 of 50 published chapters")
_f("str_frame_max_share", "structure", direction="lower", note="U6, worst frame")
_f("str_ngram_repeat_per_1k", "structure", direction="lower")
_f("str_scene_mark_per_1k", "structure", direction="twosided")
_f("str_arc_turns", "structure", direction="higher", note="A1, mean over windows")
_f("str_arc_range", "structure", direction="twosided", note="A2, reported never gated")
# names
_f("nme_distinct_first", "names", "none")
_f("nme_distinct_surnames", "names", "none")
_f("nme_names_per_1k", "names", "none")
_f("nme_ssa_top20_share", "names", direction="lower", note="tier A of NAME_FREQUENCY.tsv")
_f("nme_popular_list_share", "names", direction="lower", note="tier B of NAME_FREQUENCY.tsv")
_f("nme_reference_unlisted_share", "names", direction="twosided",
   note="not in the repo's 220-name reference: rare or invented, NOT a verdict")
_f("nme_syllables_mean", "names", direction="twosided")
_f("nme_alliterative_pairs", "names", "none")
_f("nme_a_endings_share", "names", direction="twosided", note="-a/-ia endings")
_f("nme_shared_surname_share", "names", direction="twosided")

AI_TERMS = (
    "delve", "delves", "delving", "tapestry", "intricate", "resonate", "resonates",
    "testament", "navigating", "navigate", "landscape", "vibrant", "profound",
    "in the heart of", "a world where",
)
# The §8.1 hedge list. Measured against Arm C before it is called anything.
HEDGES = (
    "somewhat", "rather", "in a way", "sort of", "kind of", "perhaps", "arguably",
    "to some extent", "more or less", "if anything", "it seems", "seemingly",
)
CORRELATIVE = re.compile(r"\b(?:not just|not only|isn't just|wasn't just|not merely|not simply)\b", re.I)
PASSIVE = re.compile(
    r"\b(?:was|were|is|are|been|being|be)\s+(?:\w+ed|shown|taken|given|made|known|seen|"
    r"held|kept|left|told|brought|found|written|built|sent|set)\b", re.I)
HEDGE_RX = re.compile("|".join(re.escape(h) for h in HEDGES), re.I)
AI_RX = [(t, re.compile(r"\b" + re.escape(t) + r"\b", re.I)) for t in AI_TERMS]
# measure.py's own -ly row, kept case-sensitive on purpose: the caps were calibrated on
# the case-sensitive reading, and a study number that disagrees with the gate is a new
# measurement, not a better one. CALIBRATION.md §A24 records what happens when the
# reading changes under a pinned threshold.
LY = re.compile(r"\b[a-z]{4,}ly\b")

WAKE = re.compile(r"\b(woke|wakes|woken|awoke|awakened|opened (?:her|his|their|its) eyes|"
                  r"lay awake|could not sleep|sat up in bed)\b", re.I)
# v2, atmospheric only. v1's list carried `heat`, `cold` and bare `sun`/`cloud`, which
# matched a stethoscope's cold, a woodstove's heat, "Cold Repository" and a metaphor's
# "choking cloud": about a fifth of its chapter-opening firings were not weather. What is
# left is precipitation, wind, fog and sky state. A capitalised match that is not the
# sentence's first word is read as a proper noun and skipped (see `weather_match`).
WEATHER = re.compile(r"\b(?:rain(?:ed|ing|s|y)?|snow(?:ed|ing|s|y)?|storm(?:s|ed|ing|y)?|"
                     r"fog(?:s|gy)?|mist(?:s|y)?|frost(?:s|y)?|thunder(?:s|ed|ing|ous)?|"
                     r"lightning|hail(?:ed|ing|s)?|sleet|drizzle|blizzard|gale(?:s)?|"
                     r"downpour|squall(?:s)?|overcast|cloudy|sunlight|sunshine|"
                     r"wind(?:s|y)?|clouds)\b", re.I)
TIME_OPENER = re.compile(r"^(?:when|at|on|in|by|that|the next|later|after|before|each|"
                         r"every|it was|for)\b", re.I)
HABITUAL = re.compile(r"\b(always|never|every|used to|would)\b", re.I)
SCENE_MARK_LINE = re.compile(r"^\s*(?:\*\s*){3,}$|^\s*(?:-\s*){3,}$|^\s*#{3,}\s*$")
TIME_SKIP = re.compile(r"\b(?:the next (?:morning|day|week|month|year)|hours later|"
                       r"days later|a week later|by morning|by nightfall|the following)\b", re.I)
FRONT_MATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)
HEADING = re.compile(r"^#{1,6}\s.*$", re.M)
CHAPTER_LINE = re.compile(
    r"^(?:chapter|part|book)\s+(?:\d+|[ivxlcdm]+|one|two|three|four|five|six|seven|"
    r"eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    r"eighteen|nineteen|twenty)\b.{0,60}$", re.I | re.M)
# Character for character the rule `dispatch.py` counts a filed book's chapters with
# (dispatch.py:774, in `finalize`). The extractor has to split on the same one: its chapter
# count is checked against the row's at filing time (`ARM_B_BRIEFING.md` trap 1), and two
# rules would report a count the row does not have. Verified against all twenty filed Arm A
# rows on 2026-11-03 -- every one reproduces its `chapter_count` exactly.
CHAPTER_HEAD = re.compile(r"(?m)^#{1,3}\s*(?:chapter|\d+[.:])", re.I)

VOWELS = "aeiouy"


# ------------------------------------------------------------------ loaders
def strip_headers(text):
    """One declared header rule for both arms (REDTEAM.md B3).

    Arm B ships YAML front matter and `#` chapter titles; Arm A ships "Chapter One" lines.
    Neither is prose, and leaving them in would make the pipeline's front matter read as
    narrative in one arm and not the other. Both `words` and `raw_words` are reported.
    """
    out = FRONT_MATTER.sub("", text)
    out = HEADING.sub("", out)
    out = CHAPTER_LINE.sub("", out)
    return out


def split_flat(text, name):
    """Split one flat manuscript into chapters on the filer's own chapter rule.

    Arm A books are filed as a single `manuscript/naive-text.md` -- the responses appended
    into one continuous text, headings and all, with no chapter tree (Arm B and C-dist both
    have one). Handing that back as one chapter starves `syn_chapter_sentlen_spread`, the
    primary endpoint, of the thing it measures spread over: ARM_B_BRIEFING.md trap 1 reached
    by a different road. The headings are in the text; they are read, not invented.

    Text before the first chapter heading is the book's title line. It is attached to the
    first chapter rather than dropped, so nothing is silently discarded -- `strip_headers`
    takes it out of the analysis text either way, and `raw_words` still counts it.
    """
    marks = [m.start() for m in CHAPTER_HEAD.finditer(text)]
    if not marks:
        return [(name, text)]
    out = []
    for i, start in enumerate(marks):
        end = marks[i + 1] if i + 1 < len(marks) else len(text)
        body = text[start:end]
        title = body.splitlines()[0].strip() if body.splitlines() else ""
        if i == 0:
            body = text[:start] + body
        out.append((title or f"{name} {i + 1}", body))
    return out


def load_book(path):
    """Return (label, [(chapter_name, text)]). A directory is resolved the way the gates
    resolve it, so the study tree and the gate tree are the same tree."""
    if os.path.isfile(path):
        stem = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return stem, [(os.path.basename(path), fh.read())]
    d = uni.resolve(path)
    if not d:
        # No chapter tree. Arm A ships its one flat manuscript under `manuscript/`, beside
        # nothing else; a bare directory of text files is still read as one chapter each.
        searched = ["", "manuscript"]
        files = []
        for sub in searched:
            files = sorted(glob.glob(os.path.join(path, sub, "*.txt")) +
                           glob.glob(os.path.join(path, sub, "*.md")))
            if files:
                break
        if not files:
            raise SystemExit(f"no chapters and no text files under {path} "
                             f"(looked in {', '.join(os.path.join(path, s) for s in searched)})")
        out = []
        for f in files:
            with open(f, encoding="utf-8", errors="ignore") as fh:
                raw = fh.read()
            if len(files) == 1:
                out.extend(split_flat(raw, os.path.splitext(os.path.basename(f))[0]))
            else:
                out.append((os.path.basename(f), raw))
        return os.path.basename(os.path.normpath(path)), out
    return os.path.basename(os.path.dirname(os.path.dirname(os.path.normpath(d)))), uni.load(d)


# ------------------------------------------------------------------ helpers
def per_1k(n, words):
    return 1000.0 * n / words if words else None


def share(n, d):
    return n / d if d else None


def pct_cv(vals):
    if len(vals) < 2 or not st.mean(vals):
        return None
    return 100.0 * st.pstdev(vals) / st.mean(vals)


def syllables(word):
    w = word.lower()
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups)
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee")):
        n -= 1
    return max(1, n)


def weather_match(sentence):
    """The first weather token in a sentence, or None.

    A capitalised weather word that is not the sentence's first word is a proper noun
    ("Cold Repository"), not weather. The sentence-start allowance is what keeps "Rain
    lashed the roof" while dropping the name, without a list of names to maintain.
    """
    for m in WEATHER.finditer(sentence):
        if m.group(0)[0].isupper() and re.search(r"[A-Za-z]", sentence[:m.start()]):
            continue
        return m.group(0)
    return None


def strip_dialogue(text):
    return tags.QUOTE.sub(" ", text)


def quotes(text):
    return [m.group(1) for m in tags.QUOTE.finditer(text)]


def ttr_rarefied(tokens, size=1000):
    """Mean type/token ratio over non-overlapping fixed windows.

    Raw TTR falls as a document grows, which is why two books of different length cannot
    be compared on it (CALIBRATION.md records it as confounded and ungated). Fixing the
    window is the minimum needed for the row to mean anything.
    """
    if len(tokens) < size:
        return None
    vals = []
    for i in range(0, len(tokens) - size + 1, size):
        chunk = tokens[i:i + size]
        vals.append(len(set(chunk)) / size)
    return st.mean(vals)


# ------------------------------------------------------------------ extraction
def extract(path):
    label, chapters = load_book(path)
    raw = [(n, t) for n, t in chapters]
    chapters = [(n, strip_headers(t)) for n, t in chapters]
    text = "\n\n".join(t for _, t in chapters)
    raw_words = sum(len(t.split()) for _, t in raw)
    w = len(text.split())
    if w < 200:
        raise SystemExit(f"{path}: {w} analysis words - too short to measure anything")

    sents = uni.sentences(text)
    sent_lens = [len(s.split()) for s in sents]
    paras = uni.paragraphs(text)
    para_lens = [len(p.split()) for p in paras]
    qs = quotes(text)
    quote_words = sum(len(q.split()) for q in qs)
    words_l = re.findall(r"[a-z']+", text.lower())
    per_k = lambda n: per_1k(n, w)
    out, details, unmeasured = {}, {}, []

    # ---- lexical
    hits = {t: len(rx.findall(text)) for t, rx in AI_RX}
    details["ai_term_hits"] = {k: v for k, v in hits.items() if v}
    out["lex_ai_term_hits"] = sum(hits.values())
    out["lex_ai_terms_per_1k"] = per_k(sum(hits.values()))
    out["lex_ly_adverbs_per_1k"] = per_k(len(LY.findall(text)))
    out["lex_hedges_per_1k"] = per_k(len(HEDGE_RX.findall(text)))
    firsts = Counter()
    for s in sents:
        m = re.match(r"[^A-Za-z]*([A-Za-z']+)", s)
        if m:
            firsts[m.group(1)] += 1
    for word in ("And", "But", "As", "When", "Suddenly"):
        out[f"lex_opener_{word.lower()}_share"] = share(firsts[word], len(sents))
    out["lex_opener_top1_share"] = share(max(firsts.values()) if firsts else 0, len(sents))
    details["opener_top5"] = firsts.most_common(5)
    out["lex_ttr_rarefied"] = ttr_rarefied(words_l)

    # ---- syntax
    out["syn_sent_words_mean"] = st.mean(sent_lens)
    out["syn_sent_words_median"] = st.median(sent_lens)
    out["syn_sent_words_sd"] = st.pstdev(sent_lens) if len(sent_lens) > 1 else None
    out["syn_short_sent_share"] = share(sum(1 for n in sent_lens if n < 6), len(sent_lens))
    out["syn_long_sent_share"] = share(sum(1 for n in sent_lens if n > 35), len(sent_lens))
    out["syn_em_dash_per_1k"] = per_k(text.count("\u2014"))
    out["syn_semicolon_per_1k"] = per_k(text.count(";"))
    out["syn_colon_per_1k"] = per_k(text.count(":"))
    out["syn_exclamation_per_1k"] = per_k(text.count("!"))
    out["syn_ellipsis_per_1k"] = per_k(len(re.findall(r"\.\.\.|\u2026", text)))
    out["syn_dialogue_share"] = share(quote_words, w)
    out["syn_correlative_per_1k"] = per_k(len(CORRELATIVE.findall(text)))
    out["syn_passive_proxy_per_1k"] = per_k(len(PASSIVE.findall(text)))
    out["syn_commas_per_sentence"] = share(text.count(","), len(sents))
    out["syn_para_words_mean"] = st.mean(para_lens) if para_lens else None
    out["syn_para_cv"] = pct_cv(para_lens)
    out["syn_oneline_para_share"] = share(
        sum(1 for p in paras if len(uni.sentences(p)) == 1), len(paras))

    # tags: look just after each quoted span, the way check-dialogue-tags.py does.
    # v1 read a flat 80 characters, so when two short lines sat close together the window
    # ran past the next opening quote: the tag was charged to the speaker above it, and a
    # speech verb inside the NEXT line's dialogue ("Can you breathe?" she demanded) was
    # read as this line's tag. v2 ends the window at the next opening quote. A tag between
    # two quotes (a quote split by its attribution) still counts; a tag inside the next
    # line's speech does not.
    said = breath = tagged = 0
    for m in tags.QUOTE.finditer(text):
        rest = text[m.end():m.end() + 80]
        nxt = re.search(r"[\"\u201c]", rest)
        window = rest[:nxt.start()] if nxt else rest
        tm = tags.TAG.search(window)
        if not tm:
            continue
        tagged += 1
        word = tm.group(1).lower()
        if word in tags.BREATH:
            breath += 1
        elif word in ("said", "says", "asked", "replied", "answered", "told"):
            said += 1
    out["syn_tag_said_share"] = share(said, tagged)
    out["syn_tag_breath_share"] = share(breath, tagged)
    details["dialogue_turns"] = len(qs)
    details["tagged_turns"] = tagged

    # per-chapter sentence-length means -> across-chapter spread (U2's quantity)
    per_ch_mean = []
    for _, t in chapters:
        s = uni.sentences(t)
        if s:
            per_ch_mean.append(st.mean(len(x.split()) for x in s))
    out["syn_chapter_sentlen_spread"] = (max(per_ch_mean) - min(per_ch_mean)
                                         if len(per_ch_mean) > 1 else None)

    # ---- structure
    ch_words = [len(t.split()) for _, t in chapters]
    out["str_chapters"] = len(chapters)
    out["str_words"] = w
    out["str_chapter_cv"] = pct_cv(ch_words)
    out["str_chapter_min"] = min(ch_words) if ch_words else None
    out["str_chapter_max"] = max(ch_words) if ch_words else None

    opens = {"wake": 0, "weather": 0, "time": 0, "habitual": 0}
    weather_hits = []
    for chname, t in chapters:
        s = uni.sentences(t)
        if not s:
            continue
        first = s[0]
        opens["wake"] += bool(WAKE.search(first))
        wm = weather_match(first)
        opens["weather"] += bool(wm)
        if wm:
            weather_hits.append([chname, wm])
        opens["time"] += bool(TIME_OPENER.match(first.strip()))
        opens["habitual"] += bool(HABITUAL.search(first))
    for k, v in opens.items():
        out[f"str_open_{k}_share"] = share(v, len(chapters))
    details["weather_openings"] = weather_hits

    coda = sum(1 for _, t in chapters if uni.CODA.search(uni.closing_paragraph(t)))
    out["str_coda_share"] = share(coda, len(chapters))

    frame_share = {}
    for name, pattern in uni.FRAMES:
        rx = re.compile(pattern, re.I)
        frame_share[name] = share(sum(1 for _, t in chapters if rx.search(t)), len(chapters))
    details["frame_share"] = frame_share
    out["str_frame_max_share"] = max(frame_share.values()) if frame_share else None

    body = re.findall(r"[a-z']+", strip_dialogue(text).lower())
    grams = Counter(tuple(body[i:i + 6]) for i in range(len(body) - 5))
    repeats = sum(c - 1 for c in grams.values() if c >= 2)
    out["str_ngram_repeat_per_1k"] = per_k(repeats)
    marks = sum(1 for line in text.splitlines() if SCENE_MARK_LINE.match(line))
    marks += len(TIME_SKIP.findall(text))
    out["str_scene_mark_per_1k"] = per_k(marks)

    whole = arc.strip_gutenberg(text)
    wins = arc.windows(whole)
    shapes = []
    for win in wins:
        s = arc.shape(arc.curve(arc.sentences(win)))
        if s:
            shapes.append(s)
    if len(shapes) >= 2:
        out["str_arc_turns"] = st.mean(s["turns"] for s in shapes)
        out["str_arc_range"] = st.mean(s["range"] for s in shapes)
    else:
        out["str_arc_turns"] = None
        out["str_arc_range"] = None
        unmeasured.append({"feature": "str_arc_turns",
                           "reason": f"{len(shapes)} measurable window(s) of ~{arc.WINDOW} "
                                     f"words; the floor is a mean over ~15. UNMEASURED, "
                                     f"not passing (WINDOW_FLOOR)."})

    # ---- names
    # What this measures, precisely: capitalised tokens that are not sentence-start noise,
    # not also lowercase common words, not weekdays/honorifics, and not contractions. It
    # is a PROPER-NOUN inventory, not a cast list - a place name that recurs is counted.
    # That is acceptable here for one reason only: both arms get the identical treatment,
    # so the arm comparison is fair even where the absolute number is inflated. It is not
    # acceptable to quote the inventory as "the characters in this book".
    #
    # Possessives and contractions are the whole false-positive problem: "Anne's" is not a
    # name, "Don't" truncates to "Don" (check-dialogue-tags.py records that bug), and a
    # cast report full of them is a report a reader stops believing. Tokens containing an
    # apostrophe are therefore dropped outright; the cost is that O'Brien is missed, which
    # is cheaper than counting "Didn't" as a character.
    # Words that occur in lowercase somewhere in the text. Built from the ORIGINAL case:
    # text.lower() would put "Anne" into this set and then filter Anne out of her own book.
    lower_words = set(re.findall(r"\b[a-z]+\b", text))
    single, pair, mid = Counter(), Counter(), Counter()
    name_rx = re.compile(r"\b([A-Z][a-z]{2,})(?:['\u2019]s)?\b")
    pair_rx = re.compile(r"\b([A-Z][a-z]{2,})\s+([A-Z][a-z]{2,})\b")
    for s in sents:
        # Count sentence-initial and mid-sentence occurrences separately. "Nobody" and
        # "Rain" at the head of a sentence are the whole false-positive class here, and a
        # real name is attested mid-sentence ("said Anne") somewhere in the book. A
        # candidate that only ever appears as the first word is a common noun, not a
        # character, and the demo books' own cast report recorded exactly this bug.
        lead = len(s) - len(s.lstrip())
        first_tok = True
        for m in name_rx.finditer(s):
            tok = m.group(1)
            if tags.is_name_candidate(tok, lower_words):
                single[tok] += 1
                if m.start() == lead and first_tok:
                    first_tok = False
                else:
                    mid[tok] += 1
        for a, b in pair_rx.findall(s):
            if (tags.is_name_candidate(a, lower_words)
                    and tags.is_name_candidate(b, lower_words)):
                pair[(a, b)] += 1

    first_names, surnames, full = set(), set(), set()
    kept_pairs = [(a, b) for (a, b), c in pair.items() if c >= 2]
    for a, b in kept_pairs:
        full.add(f"{a} {b}")
        first_names.add(a)
        surnames.add(b)
    for tok, c in single.items():
        if c >= 3 and mid[tok] >= 2 and tok not in surnames:
            first_names.add(tok)
    details["names"] = {
        "full": sorted(full),
        "firsts": sorted(first_names),
        "surnames": sorted(surnames),
        "counts": {k: v for k, v in single.most_common(40)},
    }
    out["nme_distinct_first"] = len(first_names)
    out["nme_distinct_surnames"] = len(surnames)
    out["nme_names_per_1k"] = per_k(len(first_names) + len(surnames))
    if first_names:
        tiers = Counter(nme.TIERS.get(f) for f in first_names)
        out["nme_ssa_top20_share"] = share(tiers.get("A", 0), len(first_names))
        out["nme_popular_list_share"] = share(tiers.get("B", 0), len(first_names))
        out["nme_reference_unlisted_share"] = share(tiers.get(None, 0), len(first_names))
        out["nme_syllables_mean"] = st.mean(syllables(f) for f in first_names)
        out["nme_a_endings_share"] = share(
            sum(1 for f in first_names if f.lower().endswith(("a", "ia"))), len(first_names))
    else:
        for k in ("nme_ssa_top20_share", "nme_popular_list_share",
                  "nme_reference_unlisted_share", "nme_syllables_mean",
                  "nme_a_endings_share"):
            out[k] = None
    out["nme_alliterative_pairs"] = sum(
        1 for a, b in kept_pairs if a[0].lower() == b[0].lower())
    surname_counts = Counter(b for _, b in kept_pairs)
    out["nme_shared_surname_share"] = share(
        sum(1 for b, c in surname_counts.items() if c >= 2), len(surname_counts)) \
        if surname_counts else None

    # ---- cross-book payload, computed in analyze.py
    first_sent = uni.sentences(chapters[0][1])[:1]
    last_sent = uni.sentences(chapters[-1][1])[-1:]
    norm = lambda s: [x for x in re.findall(r"[a-z']+", s.lower()) if len(x) > 1]
    cross = {
        "opening": norm(first_sent[0]) if first_sent else [],
        "closing": norm(last_sent[0]) if last_sent else [],
        "chapter_first_sentences": [norm(uni.sentences(t)[0]) for _, t in chapters
                                    if uni.sentences(t)][:40],
    }

    for k, v in list(out.items()):
        if v is None:
            unmeasured.append({"feature": k, "reason": "not computable on this text"})

    return {
        "book": label,
        "path": os.path.abspath(path),
        "words": w,
        "raw_words": raw_words,
        "header_words_removed": raw_words - w,
        "chapters": len(chapters),
        "extractor": {"script": "study/extract/features.py", "version": VERSION},
        "features": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in out.items()},
        "details": details,
        "cross": cross,
        "unmeasured": unmeasured,
    }


VERSION = "2"


# ------------------------------------------------------------------ cli
def selfcheck():
    checks = [
        ("arc lexicon sizes", (len(arc.POSITIVE), len(arc.NEGATIVE)) == (121, 143)),
        ("arc window", arc.WINDOW == 4000),
        ("frames", len(uni.FRAMES) >= 5),
        ("name tiers loaded", len(nme.TIERS) > 100),
        ("quote regex", tags.QUOTE.search('"a line of speech"') is not None),
        ("name candidate filter", tags.is_name_candidate("Mira", {"mira"}) is False),
        ("measure imports", callable(measure.measure)),
        ("feature registry complete", set(FEATURES) >= {
            "lex_ai_terms_per_1k", "syn_chapter_sentlen_spread", "str_coda_share",
            "nme_reference_unlisted_share"}),
    ]
    bad = 0
    for name, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
        bad += not ok
    print(f"\n{VERSION}: {len(FEATURES)} registered features, {bad} failure(s)")
    return 1 if bad else 0


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?", help="a book directory or one text file")
    ap.add_argument("--all", metavar="ROOT", help="every immediate subdirectory of ROOT")
    ap.add_argument("--out", metavar="DIR", help="write JSON here (default: beside the run)")
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    if args.selfcheck:
        return selfcheck()
    if args.list:
        for name, meta in FEATURES.items():
            flag = " (replication)" if meta["replication"] else ""
            print(f"{name:<28} {meta['family']:<10} {meta['direction']:<9}{flag}")
        return 0

    targets = []
    if args.all:
        targets = sorted(d for d in glob.glob(os.path.join(args.all, "*"))
                         if os.path.isdir(d))
    elif args.target:
        targets = [args.target]
    else:
        print(__doc__.strip())
        return 2

    outdir = args.out
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    rows, failed = [], []
    for t in targets:
        try:
            book = extract(t)
        except SystemExit as exc:
            # One unreadable book must not hide the nineteen that are readable: a directory
            # of books is extracted in one pass, and stopping at the first failure makes the
            # other results unavailable with no way to see which one broke. It is reported,
            # counted, and the exit status still says something is wrong.
            failed.append((t, str(exc)))
            print(f"{os.path.basename(os.path.normpath(t)):<10} NOT EXTRACTED  {exc}")
            continue
        rows.append(book)
        dest = os.path.join(outdir, f"{book['book']}.json") if outdir else None
        if dest:
            with open(dest, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(book, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
        unmeasured = len(book["unmeasured"])
        print(f"{book['book']:<10} {book['words']:>7}w {book['chapters']:>3}ch  "
              f"{sum(1 for v in book['features'].values() if v is not None):>2} features"
              f"{f'  {unmeasured} unmeasured' if unmeasured else ''}"
              f"{'  -> ' + dest if dest else ''}")
    if failed:
        print(f"\n{len(failed)} of {len(targets)} target(s) not extracted: "
              f"{', '.join(os.path.basename(os.path.normpath(t)) for t, _ in failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
