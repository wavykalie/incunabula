#!/usr/bin/env python3
"""ductus-fit.py - does the calibration corpus fight the voice this book wants?

WHY THIS EXISTS
  `skills/ductus-designer` designs a book's ductus from two things: what the author says
  the voice should be, and 2-5 passages of text that sound like it. The contract that
  comes out of that is prose, and prose cannot be argued with a scanner.

  This tool answers the one question the scanner CAN answer, and it is the question that
  should be asked before the contract is written rather than after a book is finished:

      where does the calibration corpus disagree with the register these excerpts are in,
      and which gate caps sit between them?

  The reason to ask is The Parts Still Warm. A 130k-word book passed every gate and read,
  to its reader, as "so British and boring" - because the caps are set at ~1.5x the worst
  single document in a corpus with no contemporary American voice in it, and a scanner is
  a negative instrument. Flatness becomes the ceiling, and energy reads as deviation. No
  instrument in the pipeline could see that, because none of them compared the voice the
  book wanted against the voice the corpus measured.

WHAT IT MEASURES
  The excerpts and every document in the lane's corpus, with the same arithmetic:

    capped rows   - read from tools/prose/deslop-check.sh, never retyped here:
                    D1 em dash, D2 rule of three, D3 -ly adverbs, A23 parenthetical dash,
                    A24 explanatory coda, A25 antithesis, P1 repeated opener, P3 run
    range rows    - mean sentence length, sentence-length CV, short-sentence share,
                    paragraph-length CV, one-sentence-paragraph share, dialogue share,
                    "did not" per 10k, He/She openings, texture palette, simile markers

  Per document, because that is the unit every cap was derived on. Enforcing a
  document-derived cap on a chapter is the unit error in CALIBRATION.md section 13, and
  this tool does not add a second copy of it.

  The regex rows (D1, D2, D3, A23, A24, A25) are the gate's patterns, copied. The two
  pattern checks (P1, P3) re-implement the measurement in Python, and they split sentences
  at [.!?] followed by whitespace where the shell scanner splits at a space - so near the
  cap the two can disagree, exactly as CALIBRATION.md records that they do. A P1 or P3
  number here is indicative; the scanner's own count governs the row.

WHAT EACH ROW CAN SAY
  SUPPORTED      the excerpt is inside the corpus's own range; the corpus can measure it.
  FIGHT          inside the cap but outside anything the corpus does. The cap is 1.5x the
                 corpus's worst document, so the register lives in the headroom and the
                 corpus has no evidence for it.
  BLOCK          at or past a gate cap: prose in this register fails the row as it stands.
  NO PRECEDENT   a range row outside the corpus's observed range. Reported, never gated.
  CAP NOT READ   the gate row could not be parsed. Nothing is claimed about it.

WHAT IT WILL NOT DO
  - It does not move a cap, and it does not recommend a number. A cap moves by
    re-derivation on a named corpus plus a freeze record; that is a separate action.
  - It does not edit the contract. BLOCK and FIGHT are findings the skill writes down.
  - It does not judge prose. Two excerpts cannot say whether a book is good; they can say
    whether the corpus has ever seen this hand.
  - A missing corpus, or fewer than 500 excerpt words, is NOT RUN (exit 3 / exit 2). A
    fit report that reads as a pass it did not earn is the failure this file exists to
    prevent.

WHY THE EXCERPT FLOOR IS 500 WORDS
  A per-1,000-word rate over 300 words is one or two hits. P1's own recorded lesson is the
  same one: a rate calibrated on chapters fails ordinary published letters below 667
  words, and the honest answer at that size is UNMEASURED. The floor is pooled across the
  excerpts, and each excerpt's word count is printed so a single thin passage can be seen.

usage:  python tools/prose/ductus-fit.py <book-root> --lane NAME [--corpus DIR]
                                         [--excerpts DIR] [--min-words N]
        python tools/prose/ductus-fit.py --self-test

  --lane        a lane from calibration/LANES.tsv. Default: `ductus_lane:` in the book's
                PROJECT_STATE.yaml, then the single `governing` lane.
  --corpus      measure this directory instead of the lane's registered path.
  --excerpts    default <book>/ductus/excerpts, then <book>/excerpts.
  --min-words   the excerpt floor (default 500). Lowering it is allowed and is recorded in
                the report: a lowered floor is a weaker claim, not a smaller one.

EXIT
  0  every capped row SUPPORTED
  1  at least one folded row is BLOCK, FIGHT or NO PRECEDENT
  2  excerpts missing, too short, or the lane cannot be resolved
  3  the corpus is not installed, or too small to profile - the fit is NOT RUN
"""

import glob
import os
import re
import statistics as st
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GATE = os.path.join(HERE, "deslop-check.sh")
LANES = os.path.join(HERE, "calibration", "LANES.tsv")

MIN_EXCERPT_WORDS = 500.0
MIN_CORPUS_WORDS = 5000.0
BACK_MATTER = ("afterword", "appendix")

# The lane rule, printed on every run and enforced by nothing: a lane under construction
# has to be measurable to be finished, and a cap derived from an unfinished lane is a
# number with a plausible story behind it.
LANE_BOOKS = (5, 10)
LANE_WORDS = (500_000, 1_000_000)

EM = "\u2014"

RULE_OF_THREE = re.compile(r"[^,.;:]{3,30}, [^,.;:]{3,30}, and [^,.;:]{3,30}")
# `{4,}` and not `{4}`: the gate's D3 counts four OR MORE letters before -ly, so
# "badly" counts and a transcription of this gone wrong measures adverbs at a third
# of their rate. Found by checking the tool's corpus worst against CALIBRATION.md's
# recorded worst document (24.3/1k); it read 8.8 before this line was corrected.
LY = re.compile(r"(^|[^a-z])[a-z]{4,}ly([^a-z]|$)")
PAREN_DASH = re.compile(EM + r"[^" + EM + r"\n]{1,70}" + EM)
CODA = re.compile(
    r"(which|that|this) is (also )?why"
    r"|it is (also )?why"
    r"|that is (what|the) (makes|thing)"
    r"|the (next|following) chapter is"
    r"|which is (the )?position",
    re.I,
)
ANTITHESIS = re.compile(
    r"(was|were|is|are) not\b[^.!?]{0,50}[.!?] +(It|That|This|He|She|They) (was|were|is|are)",
    re.I,
)
TEXTURE = ["gray", "flat", "cold", "heavy", "dry", "pale", "dark"]
SIMILE = re.compile(r"\b(?:like a|like an|like the|as if|as though)\b", re.I)
# Double quotes are the US convention; British typesetting sets speech in single ones.
# The action-voice lane holds both (Abercrombie 2006 runs 100% single-quoted), so a
# counter that reads only "..." reports a dialogue-dense book as 0% speech - a number
# about the typesetter, not the register. Non-overlapping finditer keeps a nested
# \u201c'...'\u201d from being counted twice.
QUOTED = re.compile(r"\u201c([^\u201d]{1,4000})\u201d|\"([^\"]{1,4000})\""
                    r"|\u2018([^\u2019]{1,4000})\u2019")
STOP_FIRST = set("the a an i it this that there".split())


def utf8_stdout():
    """Emit UTF-8 whatever the locale says - the em dash is data here, not decoration."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def strip_headings(text):
    return re.sub(r"(?m)^#{1,6}.*$", "", text)


def sentences(text):
    """Same splitter as measure.py and the gates: break on [.!?] then whitespace."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", strip_headings(text)) if s.strip()]


def paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n", strip_headings(text).strip()) if p.strip()]


# ------------------------------------------------------------------ the gate's caps
# Read from the scanner rather than retyped: a second copy of a threshold is a second
# thing to keep true, and this directory has been bitten by exactly that.
ARRAY_TIERS = {"HARD": "hard", "DEMOTED": "density", "DENSITY": "density", "REPORT": "report"}


def read_gate(path=GATE):
    """(caps, tiers, problem). caps is row id -> limit in that row's own unit."""
    caps, tiers, problem = {}, {}, None
    if not os.path.isfile(path):
        return {}, {}, "no %s" % os.path.basename(path)
    text = read_text(path)
    tier = None
    for line in text.splitlines():
        head = re.match(r"^([A-Z_]+)=\(", line)
        if head:
            tier = ARRAY_TIERS.get(head.group(1))
            continue
        if line.startswith(")"):
            tier = None
            continue
        m = re.match(r"^\s*'([A-Z]\d+[a-z]?)\|([^'|]*)\|(\d+)\|(\d+)\|", line)
        if m and tier:
            caps[m.group(1)] = int(m.group(3)) * 1000.0 / int(m.group(4))
            tiers[m.group(1)] = tier
    n = re.search(r"^OPEN_PER_N=(\d+)", text, re.M)
    w = re.search(r"^OPEN_PER_W=(\d+)", text, re.M)
    if n and w and int(w.group(1)):
        caps["P1"] = int(n.group(1)) * 1000.0 / int(w.group(1))
        tiers["P1"] = "density"
    f = re.search(r"^FRAG_RUN=(\d+)", text, re.M)
    if f:
        caps["P3"] = float(f.group(1))
        tiers["P3"] = "density"
    if not caps:
        problem = "no cap could be parsed out of %s" % os.path.basename(path)
    return caps, tiers, problem


# ------------------------------------------------------------------------ measurement
def metrics(text):
    """Every number this tool reports, for one document. Counts and rates, no judgement."""
    body = strip_headings(text)
    words = len(body.split())
    if words == 0:
        return None
    sents = sentences(body)
    lens = [len(s.split()) for s in sents] or [0]
    paras = paragraphs(body)
    plens = [len(p.split()) for p in paras] or [0]
    per_k = lambda n: n * 1000.0 / words
    per_10k = lambda n: n * 10000.0 / words

    openers = {}
    for s in sents:
        toks = re.sub(r"^[^A-Za-z]*", "", s).split()
        if len(toks) >= 2:
            key = (toks[0] + " " + toks[1]).lower()
            if re.fullmatch(r"[a-z]+ [a-z]+", key):
                openers[key] = openers.get(key, 0) + 1

    run = best = 0
    for s in sents:
        if 1 <= len(s.split()) <= 4:
            run += 1
            best = max(best, run)
        else:
            run = 0

    quoted = 0
    for m in QUOTED.finditer(body):
        quoted += len((m.group(1) or m.group(2) or m.group(3) or "").split())

    firsts = []
    for s in sents:
        toks = re.sub(r"^[^A-Za-z]*", "", s).split()
        if toks:
            firsts.append(toks[0])
    he_she = sum(1 for f in firsts if f in ("He", "She"))

    low = body.lower()
    texture = sum(len(re.findall(r"\bgr[ae]y\b" if w == "gray" else r"\b%s\b" % w, low))
                  for w in TEXTURE)

    return {
        "words": words,
        "sents": len(sents),
        "d1": body.count(EM),
        "d1_k": per_k(body.count(EM)),
        "dashspell": len(re.findall(r"--", body)),
        "d2_k": per_k(len(RULE_OF_THREE.findall(body))),
        "d3_k": per_k(len(LY.findall(body))),
        "a23_k": per_k(len(PAREN_DASH.findall(body))),
        "a24_k": per_k(len(CODA.findall(body))),
        "a25_k": per_k(len(ANTITHESIS.findall(body))),
        "p1_k": per_k(max(openers.values()) if openers else 0),
        "p1_max": max(openers.values()) if openers else 0,
        "p1_top": sorted(openers.items(), key=lambda kv: -kv[1])[:2],
        "p3_run": best,
        "mean_sent": st.mean(lens),
        "sent_cv": 100.0 * st.pstdev(lens) / st.mean(lens) if st.mean(lens) else 0.0,
        "short_share": 100.0 * sum(1 for n in lens if 1 <= n <= 4) / max(1, len(lens)),
        "para_cv": 100.0 * st.pstdev(plens) / st.mean(plens) if st.mean(plens) else 0.0,
        "oneline_share": 100.0 * sum(1 for p in paras if len(sentences(p)) == 1) / max(1, len(paras)),
        "dialogue_share": 100.0 * quoted / words,
        "neg_k": per_10k(low.count("did not")),
        "subject_share": 100.0 * he_she / max(1, len(firsts)),
        "texture_k": per_10k(texture),
        "simile_k": per_k(len(SIMILE.findall(body))),
    }


def corpus_docs(directory):
    """Narrative documents only - back matter measures a register nobody reads the book in."""
    files = []
    for path in sorted(glob.glob(os.path.join(directory, "*.txt")) +
                       glob.glob(os.path.join(directory, "*.md"))):
        base = os.path.basename(path).lower()
        if any(k in base for k in BACK_MATTER):
            continue
        files.append(path)
    return files


def load_excerpts(directory):
    """[(source, text, words)]. A source is declared, never inferred from a heading."""
    out = []
    for path in sorted(glob.glob(os.path.join(directory, "*.txt")) +
                       glob.glob(os.path.join(directory, "*.md"))):
        # A README documents the excerpt format and a manifest lists it; neither is an
        # excerpt. Counting the instructions as prose measures this project, not the book.
        if os.path.basename(path).lower().startswith(("readme", "manifest")):
            continue
        text = read_text(path)
        source = None
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if m:
            for line in m.group(1).splitlines():
                if line.strip().lower().startswith("source:"):
                    source = line.split(":", 1)[1].strip()
            text = text[m.end():]
        else:
            m = re.match(r"^source:\s*(.+)\n", text)
            if m:
                source = m.group(1).strip()
                text = text[m.end():]
        out.append((source or os.path.splitext(os.path.basename(path))[0], text,
                    len(text.split())))
    return out


# --------------------------------------------------------------------------- verdicts
CAP_ROWS = [
    ("D1", "em dash", "d1_k", "per 1k"),
    ("D2", "rule of three", "d2_k", "per 1k"),
    ("D3", "-ly adverbs", "d3_k", "per 1k"),
    ("A23", "parenthetical dash", "a23_k", "per 1k"),
    ("A24", "explanatory coda", "a24_k", "per 1k"),
    ("A25", "antithesis formula", "a25_k", "per 1k"),
    ("P1", "repeated opener, top", "p1_k", "per 1k"),
    ("P3", "longest short-sentence run", "p3_run", "sentences"),
]

RANGE_ROWS = [
    ("mean sentence length", "mean_sent", "words",
     "never a defect on its own; it is the dimension a rhythm argument is made on"),
    ("sentence-length CV", "sent_cv", "%",
     "within one excerpt this is scene, not book; read it beside the corpus, not alone"),
    ("short sentences (<=4 words)", "short_share", "%",
     "the kinetic register's most visible number"),
    ("paragraph-length CV", "para_cv", "%",
     "U5 is the transferable row in this directory and it measures a manuscript, "
     "not an excerpt: this number is not a verdict on it"),
    ("one-sentence paragraphs", "oneline_share", "%",
     "U4 is a market convention, not a law of prose; the corpus range is the honest input"),
    ("dialogue words", "dialogue_share", "%",
     "a register is partly how much of it is speech"),
    ("'did not'", "neg_k", "per 10k",
     "the voice's engine in a book that runs on negation, and its tell in one that does not"),
    ("He/She sentence openings", "subject_share", "%",
     "advisory everywhere: published 19th-century prose sits at 5-10%, and no modern "
     "corpus here can say what is normal"),
    ("texture palette", "texture_k", "per 10k",
     "gray/flat/cold/heavy/dry/pale/dark - one fixed palette, so a corpus difference is "
     "a register difference and not a subject one"),
    ("simile markers", "simile_k", "per 1k",
     "crude: it counts 'like a' and 'as if', not metaphor. A voice that says 'like' more "
     "than 'is' approximates rather than asserts"),
]


def band(values):
    return min(values), max(values)


def profile(excerpt_metrics, corpus_metrics, caps, tiers):
    """[(row dict)]. Pure: no printing, so --self-test can assert on it."""
    rows = []
    for rid, label, key, unit in CAP_ROWS:
        cap = caps.get(rid)
        worst = max(m[key] for m in corpus_metrics)
        value = excerpt_metrics[key]
        if cap is None:
            state = "CAP NOT READ"
        elif rid == "P3":
            state = "BLOCK" if value >= cap else ("FIGHT" if value > worst else "SUPPORTED")
        else:
            state = "BLOCK" if value > cap else ("FIGHT" if value > worst else "SUPPORTED")
        rows.append({"kind": "cap", "id": rid, "label": label, "key": key, "unit": unit,
                     "value": value, "worst": worst, "cap": cap,
                     "tier": tiers.get(rid, "?"), "state": state})
    for label, key, unit, note in RANGE_ROWS:
        lo, hi = band([m[key] for m in corpus_metrics])
        value = excerpt_metrics[key]
        state = "SUPPORTED" if lo <= value <= hi else "NO PRECEDENT"
        rows.append({"kind": "range", "label": label, "key": key, "unit": unit,
                     "value": value, "lo": lo, "hi": hi, "note": note, "state": state})
    return rows


def findings(rows):
    return [r for r in rows if r["state"] in ("BLOCK", "FIGHT", "NO PRECEDENT")]


def num(row, value):
    """One decimal for rates, integers for counts - and the unit printed with it."""
    if row["unit"] == "sentences":
        return "%d" % value
    return "%.1f%s" % (value, "" if row["unit"] == "%" else "")


def render(label, excerpts, lane, corpus_path, corpus_n, corpus_words, rows, caps_problem,
           excerpt_words, min_words, resolved_note=None):
    out = []
    out.append("ductus-fit - %s" % label)
    out.append("  excerpts   %d file(s), %d words%s" % (
        len(excerpts), excerpt_words,
        "" if excerpt_words >= min_words else
        "   BELOW THE %d-WORD FLOOR: a rate here is one or two hits" % min_words))
    for source, _text, words in excerpts:
        out.append("             - %s (%d words)" % (source, words))
    if lane:
        out.append("  lane       %s  [%s]  %s book(s), %s words  %s" % (
            lane["lane"], lane["role"], lane["books"] or "0", lane["words"] or "0",
            lane["path"]))
        lo, hi = LANE_WORDS
        blo, bhi = LANE_BOOKS
        books = int(lane["books"] or 0)
        words = int(lane["words"] or 0)
        fit = "within" if (blo <= books <= bhi and lo <= words <= hi) else "outside"
        out.append("  lane size  %s the rule (%d-%d books, %dk-%dk words); a lane under "
                   "construction measures what it has, not what it will have" % (
                       fit, blo, bhi, lo // 1000, hi // 1000))
    out.append("  corpus     %d document(s), %d words  %s" % (corpus_n, corpus_words,
                                                              corpus_path))
    if resolved_note:
        out.append("             %s" % resolved_note)
    if caps_problem:
        out.append("  caps       UNREAD - %s; no row below claims a cap" % caps_problem)
    out.append("")
    out.append("  %-28s %10s %15s %9s  %s" % (
        "dimension", "excerpt", "corpus", "cap", "state"))
    for r in rows:
        if r["kind"] == "cap":
            out.append("  %-28s %10s %15s %9s  %s" % (
                "%s %s" % (r["id"], r["label"]), num(r, r["value"]),
                "worst " + num(r, r["worst"]),
                "-" if r["cap"] is None else num(r, r["cap"]), r["state"]))
        else:
            out.append("  %-28s %10s %15s %9s  %s" % (
                r["label"], num(r, r["value"]),
                "%s-%s" % (num(r, r["lo"]), num(r, r["hi"])), "-", r["state"]))
    out.append("")

    found = findings(rows)
    if not found:
        out.append("  No dimension fights. The corpus can measure this register, which is "
                   "the only thing this report establishes.")
    else:
        out.append("  %d dimension(s) where the corpus and the excerpts disagree:"
                   % len(found))
        out.append("")
        for r in found:
            if r["kind"] == "cap":
                cap_txt = ("cap %s, %s tier" % (num(r, r["cap"]), r["tier"])
                           if r["cap"] is not None else "cap unread")
                out.append("  %-9s %s  %s %s   corpus worst %s   %s" % (
                    r["state"], r["label"], num(r, r["value"]), r["unit"],
                    num(r, r["worst"]), cap_txt))
                if r["state"] == "BLOCK":
                    out.append("            Past the row's own limit: prose in this register "
                               "fails %s as it stands." % r["id"])
                    out.append("            A cap moves by re-derivation on a named corpus "
                               "plus a freeze record - never to let a contract breathe.")
                elif r["worst"] > 0 and r["cap"]:
                    head = r["cap"] / r["worst"]
                    out.append("            The cap sits %.1fx above the corpus's worst "
                               "document, so this register is exactly the headroom the cap "
                               "adds above what the corpus measures." % head)
                    out.append("            The corpus has no document like this; a pass here "
                               "is the cap's tolerance, not the corpus's judgement.")
                elif r["cap"]:
                    out.append("            The corpus never reaches this dimension at all "
                               "(worst %s), so there is no precedent for the rate - only "
                               "the cap's allowance of %s." % (
                                   num(r, r["worst"]), num(r, r["cap"])))
            else:
                out.append("  %-9s %s  %s %s   corpus %s-%s" % (
                    r["state"], r["label"], num(r, r["value"]), r["unit"],
                    num(r, r["lo"]), num(r, r["hi"])))
                note = r["note"]
                out.append("            No document in the lane is here. %s%s" % (
                    note[0].upper(), note[1:] + "."))
            out.append("")

    blocked = [r for r in rows if r["state"] == "BLOCK"]
    fought = [r for r in rows if r["state"] == "FIGHT"]
    precedents = [r for r in rows if r["state"] == "NO PRECEDENT"]
    out.append("  corpus fit: %d block, %d fight, %d without precedent, %d supported." % (
        len(blocked), len(fought), len(precedents),
        sum(1 for r in rows if r["state"] == "SUPPORTED")))
    return "\n".join(out)


# ------------------------------------------------------------------------------- lanes
LANE_COLUMNS = ("lane", "role", "register", "books", "words", "path", "note")


def read_lanes(path=LANES):
    """[dict] keyed by the registry's own header row.

    Header-mapped rather than positional since 2026-11-12: the registry grew `works`,
    `era`, `status`, `answers` and `cannot`, and a positional reader would have shifted
    `note` into the wrong field for every lane without ever raising. The seven original
    columns are required; later ones are carried as-is, so a registry can say more
    without every tool learning the new schema at once. Tab-separated on purpose: a
    space-separated row is a parse error, not a guess - a registry read wrongly is a
    lane measured wrongly.
    """
    rows, problem = [], None
    if not os.path.isfile(path):
        return [], "no %s" % os.path.basename(path)
    header = None
    for number, line in enumerate(read_text(path).splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = [p.strip() for p in line.split("\t")]
        if header is None:
            if parts[0] != "lane":
                return [], ("line %d: the first table row is not a header" % number)
            missing = [c for c in LANE_COLUMNS if c not in parts]
            if missing:
                return [], ("the header is missing %s" % ", ".join(missing))
            header = parts
            continue
        if len(parts) != len(header):
            problem = ("line %d has %d columns and the header has %d"
                       % (number, len(parts), len(header)))
            continue
        rows.append(dict(zip(header, parts)))
    if header is None:
        return [], "no header row in %s" % os.path.basename(path)
    return rows, problem


def resolve_corpus(path):
    """(resolved, note, problem). The registry names where a corpus belongs, and a
    checkout may hold it under a book's own calibration directory - the copies the
    .gitignore explicitly allows. Exactly one candidate is used; two is a refusal,
    because picking one would be a guess and this tool exists to not guess.
    """
    if path and os.path.isdir(path):
        return path, None, None
    name = os.path.basename(os.path.normpath(path or ""))
    if not name:
        return None, None, None
    candidates = []
    for pattern in (os.path.join(HERE, "calibration", "corpus", name),
                    os.path.join(ROOT, "test-books", "*", "tools", "calibration",
                                 "corpus", name),
                    os.path.join(ROOT, "demo-books", "*", "tools", "calibration",
                                 "corpus", name)):
        candidates.extend(p for p in glob.glob(pattern) if os.path.isdir(p))
    candidates = sorted(set(os.path.abspath(c) for c in candidates))
    if len(candidates) == 1:
        rel = os.path.relpath(candidates[0], ROOT).replace(os.sep, "/")
        return candidates[0], ("resolved from %s - the registered path has no corpus"
                               " installed here" % rel), None
    if len(candidates) > 1:
        return None, None, (
            "%s is installed in %d places (%s); pass --corpus, because choosing one "
            "would be a guess" % (name, len(candidates), ", ".join(
                os.path.relpath(c, ROOT).replace(os.sep, "/") for c in candidates)))
    return None, None, None


def declared_lane(book):
    """`ductus_lane:` in PROJECT_STATE.yaml, read the way conventions.py reads a mode:
    one regex, no YAML dependency, and an absent key is absent rather than defaulted."""
    path = os.path.join(book, "PROJECT_STATE.yaml")
    if not os.path.isfile(path):
        return None
    m = re.search(r"^\s*ductus_lane\s*:\s*\"?([A-Za-z0-9_-]+)", read_text(path), re.M)
    return m.group(1) if m else None


def resolve_lane(name, book):
    lanes, problem = read_lanes()
    if problem:
        return None, problem
    if name:
        for lane in lanes:
            if lane["lane"] == name:
                return lane, None
        return None, ("%r is not a lane in calibration/LANES.tsv (have: %s)"
                      % (name, ", ".join(l["lane"] for l in lanes) or "none"))
    declared = declared_lane(book) if book else None
    if declared:
        for lane in lanes:
            if lane["lane"] == declared:
                return lane, None
        return None, "PROJECT_STATE.yaml declares ductus_lane %r, which is not registered" % declared
    governing = [l for l in lanes if l["role"] == "governing"]
    if len(governing) == 1:
        return governing[0], None
    return None, ("no --lane given and %d governing lanes registered; name one"
                  % len(governing))


# ---------------------------------------------------------------------------- runner
def analyse(book, lane_name, corpus_dir, excerpts_dir, min_words):
    """(exit code, report text). The only place the arguments are interpreted."""
    if not excerpts_dir:
        for candidate in (os.path.join(book, "ductus", "excerpts") if book else None,
                          os.path.join(book, "excerpts") if book else None):
            if candidate and os.path.isdir(candidate):
                excerpts_dir = candidate
                break
    if not excerpts_dir or not os.path.isdir(excerpts_dir):
        return 2, ("ductus-fit: NOT RUN - no excerpts at %s.\n"
                   "  The fit is unmeasured, which is not the same as supported.\n"
                   "  Expected <book>/ductus/excerpts/*.txt, each with a source line."
                   % (excerpts_dir or "<book>/ductus/excerpts"))

    excerpts = load_excerpts(excerpts_dir)
    if not excerpts:
        return 2, "ductus-fit: NOT RUN - %s holds no .txt or .md files." % excerpts_dir
    total = sum(w for _s, _t, w in excerpts)
    if total < min_words:
        return 2, ("ductus-fit: NOT RUN - %d excerpt words, below the %d-word floor.\n"
                   "  At this size a per-1k rate is one or two hits, so a fit report would\n"
                   "  be a verdict about type. Add excerpt text, or lower --min-words and\n"
                   "  accept that the report says less." % (total, min_words))

    lane, problem = resolve_lane(lane_name, book)
    if problem:
        return 2, "ductus-fit: NOT RUN - %s" % problem
    requested = corpus_dir or (os.path.join(ROOT, lane["path"]) if lane else None)
    path, resolved_note, ambiguous = resolve_corpus(requested)
    if ambiguous:
        return 3, "ductus-fit: NOT RUN - %s" % ambiguous
    if not path:
        return 3, ("ductus-fit: NOT RUN - no corpus installed at %s.\n"
                   "  The corpus is published commercial prose and is not shipped. A fit\n"
                   "  measured against nothing is not a fit, and this exits 3 rather than\n"
                   "  reporting a pass it did not earn. See calibration/LANES.tsv." % requested)

    files = corpus_docs(path)
    profiles = []
    skipped = 0
    for f in files:
        m = metrics(read_text(f))
        if m:
            profiles.append(m)
        else:
            skipped += 1
    words = sum(m["words"] for m in profiles)
    if not profiles or words < MIN_CORPUS_WORDS:
        return 3, ("ductus-fit: NOT RUN - the corpus at %s holds %d words in %d document(s).\n"
                   "  Below %d words the lane's worst document is noise, and a comparison\n"
                   "  against noise reports fights that do not exist."
                   % (path, words, len(profiles), int(MIN_CORPUS_WORDS)))

    pooled_text = "\n\n".join(t for _s, t, _w in excerpts)
    ex = metrics(pooled_text)
    if not ex:
        return 2, "ductus-fit: NOT RUN - the excerpts hold no measurable text."

    caps, tiers, caps_problem = read_gate()
    rows = profile(ex, profiles, caps, tiers)
    report = render(os.path.basename(os.path.normpath(book)) if book else "excerpts",
                    excerpts, lane, os.path.relpath(path, ROOT).replace(os.sep, "/"),
                    len(profiles), words, rows, caps_problem, total, min_words,
                    resolved_note)

    # A dash spelled "--" is typography, not restraint, and the corpus suffers the same
    # artifact (CALIBRATION.md section 2). Say it where the number is read.
    notes = []
    if ex["d1"] == 0 and ex["dashspell"]:
        notes.append("  NOTE  the excerpts spell %d dash(es) as '--' and use no U+2014: D1\n"
                     "        reads 0.00 for typography, not for voice. Re-run on the same\n"
                     "        text with em dashes if the register's dash rate is the question."
                     % ex["dashspell"])
    worst_excerpt = max(range(len(excerpts)), key=lambda i: excerpts[i][2])
    hot = {r["id"] for r in rows if r["state"] in ("BLOCK", "FIGHT")}
    if len(excerpts) > 1 and hot:
        single = []
        for rid, label, key, _unit in CAP_ROWS:
            if rid not in hot:
                continue
            m = metrics(excerpts[worst_excerpt][1])
            if m and rid == "P3":
                if m[key] >= (caps.get(rid) or 0) or m[key] > max(x[key] for x in profiles):
                    single.append(label)
            elif m and (m[key] > max(x[key] for x in profiles)):
                single.append(label)
        if single:
            notes.append("  NOTE  the longest excerpt (%s) alone carries: %s. One passage is\n"
                         "        a scene; ask whether the dimension is book-wide before the\n"
                         "        contract makes it a rule."
                         % (excerpts[worst_excerpt][0], ", ".join(single[:4])))
    if notes:
        report += "\n\n" + "\n".join(notes)

    return (1 if findings(rows) else 0), report


def self_test():
    """The tool must be able to fire, and its caps must come from the gate.

    A comparison that only ever prints SUPPORTED proves nothing - the same rule this
    directory applies to every gate. Two arms on synthetic prose: one excerpt in the
    corpus's register, one that is not.
    """
    caps, tiers, problem = read_gate()
    if problem:
        print("self-test: FAIL - %s" % problem)
        return 1
    expect = {"D1": 10.0, "D2": 5.0, "D3": 26.0, "A23": 3.0, "A24": 1.0, "A25": 1.5,
              "P1": 6.0, "P3": 7.0}
    bad = ["%s=%s not %s" % (k, caps.get(k), v) for k, v in expect.items()
           if abs((caps.get(k) or -1) - v) > 1e-9]
    if bad:
        print("self-test: FAIL - caps disagree with the gate: %s" % "; ".join(bad))
        return 1

    tmp = tempfile.mkdtemp(prefix="ductus-fit-")
    corpus = os.path.join(tmp, "corpus")
    os.makedirs(corpus)
    base = ("The room was quiet and the man sat down with the paper in his hand. "
            "He read the first page and then the second, and he did not look up. "
            "The window was open and the street below was going about its morning. ") * 12
    for i in range(6):
        with open(os.path.join(corpus, "doc-%02d.txt" % i), "w", encoding="utf-8") as fh:
            fh.write(base * 2)

    def run(text, label):
        d = os.path.join(tmp, label)
        os.makedirs(d)
        with open(os.path.join(d, "01.txt"), "w", encoding="utf-8") as fh:
            fh.write("source: synthetic\n" + text)
        code, report = analyse(None, None, corpus, d, 200)
        return code, report

    ok = True
    # Arm 1: the same prose, plus enough dashes to pass D1's cap.
    dashed = base.replace(". ", " \u2014and then\u2014 ", 14)
    code, report = run(dashed, "dashed")
    if "BLOCK" not in report or "em dash" not in report:
        print("self-test: FAIL - a dash-heavy excerpt was not reported as a D1 block.")
        print(report)
        ok = False
    # Arm 2: the corpus's own register must not be reported as a fight on D1.
    code2, report2 = run(base, "matched")
    line = [l for l in report2.splitlines() if "D1 em dash" in l]
    if not line or "SUPPORTED" not in line[0]:
        print("self-test: FAIL - prose matched to the corpus did not clear D1.")
        ok = False
    # Arm 3: absent corpus is NOT RUN, never a pass. The excerpts have to be real here,
    # or the run stops at the excerpt floor and exits 2 - which is what this arm caught
    # the first time it was written: the corpus arm was never reaching the corpus.
    code3, _report3 = analyse(None, None, os.path.join(tmp, "absent"),
                              os.path.join(tmp, "matched"), 200)
    if code3 != 3:
        print("self-test: FAIL - an absent corpus exited %d, not 3." % code3)
        ok = False
    # Arm 4: a thin excerpt is NOT RUN, never a verdict.
    code4, _report4 = analyse(None, None, corpus, os.path.join(tmp, "matched"), 5000)
    if code4 != 2:
        print("self-test: FAIL - a below-floor excerpt exited %d, not 2." % code4)
        ok = False

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    if not ok:
        return 1
    print("self-test: PASS - 8 caps read from deslop-check.sh; a dash-heavy excerpt BLOCKs "
          "D1; matched prose does not; absent corpus exits 3; thin excerpts exit 2.")
    return 0


def main(argv):
    args = list(argv[1:])
    if "--self-test" in args:
        return self_test()

    def take(flag):
        if flag in args:
            i = args.index(flag)
            value = args[i + 1] if i + 1 < len(args) else None
            del args[i:i + 2]
            return value
        return None

    lane_name = take("--lane")
    corpus_dir = take("--corpus")
    excerpts_dir = take("--excerpts")
    min_words = take("--min-words")
    try:
        min_words = float(min_words) if min_words else MIN_EXCERPT_WORDS
    except ValueError:
        print("ductus-fit: --min-words wants a number.")
        return 2
    book = next((a for a in args if not a.startswith("--")), None)
    if not book and not (corpus_dir and excerpts_dir):
        print(__doc__.strip().splitlines()[0])
        print("usage: python tools/prose/ductus-fit.py <book-root> --lane NAME "
              "[--corpus DIR] [--excerpts DIR]")
        print("       python tools/prose/ductus-fit.py --self-test")
        return 2
    if book:
        book = book.rstrip("/\\") or book

    code, report = analyse(book, lane_name, corpus_dir, excerpts_dir, min_words)
    print(report)
    if code == 0:
        print("\nductus-fit: no fight. The corpus can measure this register; it says nothing "
              "about whether the voice is good.")
    elif code == 1:
        print("\nductus-fit: the corpus fights this register in %s. Write it into the "
              "contract's Corpus fit section - a fit that is found and not recorded is the "
              "failure this tool exists for." % ("at least one dimension"))
    elif code == 3:
        print("\nductus-fit: NOT RUN. Not a pass.")
    return code


if __name__ == "__main__":
    utf8_stdout()
    sys.exit(main(sys.argv))
