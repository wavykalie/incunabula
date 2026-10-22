#!/usr/bin/env python3
"""build-script.py — Narration-script builder for the Incunabula audiobook stage.

WHY THIS EXISTS
  TTS synthesis cannot be handed raw manuscript markdown. Markdown carries structural
  headings, scene breaks, unexpanded numbers/dates/abbreviations/symbols, interleaved
  dialogue and attribution within single paragraphs, unattributed dialogue lines, and
  unmapped proper nouns. Worse, an agent might attempt to start audiobook production on
  an unfrozen or incomplete manuscript.

  This builder enforces both boundaries:
    1. FREEZE & COMPLETION REFUSAL GATE: Refuses to run (exit 1) unless:
       - `tools/prose/verify-freeze.sh` holds (`FREEZE HOLDS`),
       - `PROJECT_STATE.yaml` exists and its prose status is complete (`complete` or
         `gate_passed` / `published`), NOT `in_progress`, `drafting`, or `concept`,
       - `tools/check-pass-evidence.py` reports 0 missing chapter pass files and >0
         gated words,
       - No prose gate recorded in `PROJECT_STATE.yaml` is in a failed state unless
         covered by an explicit recorded resolution/waiver, AND
       - `tools/audio/check-lexicon.py` exits 0 (every proper noun in the scanned
         chapters is mapped in `audiobook/lexicon.yaml` or waived in
         `maintenance/WAIVERS.md`).
    2. STRUCTURED NARRATION SCRIPT GENERATION: Splits each frozen chapter into ordered
       utterance segments written to `audiobook/scripts/chapter-NN.json`, where each
       segment carries:
       - `segment_id`: deterministic ID (`chNN-segMMMM`)
       - `kind`: `"heading"` | `"narration"` | `"dialogue"` | `"pause"`
       - `speaker`: `"NARRATOR"` or canonical character ID/name
       - `raw_text`: original manuscript text span
       - `spoken_text`: normalized spoken text (numbers, years, currencies, symbols,
         and abbreviations expanded to words; proper-noun phonetic hints attached)
       - `style`: `{speed, pitch, volume, emotion}` defaults merged from book/character
         config and context
       - `paralinguistic_tags`: rationed inline tags (`[breath]`, `[sigh]`, `[laughter]`),
         strictly capped per character per chapter (default <= 2)
       - `pause_after_ms`: explicit pause duration after segment (and explicit pause
         segments for scene breaks and chapter transitions)
       - `lexicon_hits`: proper nouns in this segment and their IPA/respelling from
         `audiobook/lexicon.yaml`

USAGE
  python tools/audio/build-script.py <book-root> [--chapter <num-or-file>]
      [--paralinguistic-cap <N>] [--out-dir <dir>]

EXIT CODES
  0  SCRIPTS BUILT — freeze held, lexicon clean, narration scripts written
  1  REFUSED / GATE FAIL — manuscript not frozen/complete, pass evidence missing,
     or unmapped proper nouns in lexicon
  2  NOT RUN — missing book directory, missing PROJECT_STATE.yaml, or no chapters
  3  ERROR — malformed config or lexicon
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
ROOT_DIR = os.path.dirname(TOOLS_DIR)

CHAPTER_RE = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)
SCENE_BREAK_RE = re.compile(r"^\s*(?:\*\s*\*\s*\*+|---+|___+|#\s*#|\u2042|\u2022\s*\u2022\s*\u2022)\s*$")
HEADING_RE = re.compile(r"^\s*(#{1,4})\s+(.+?)\s*$")

# Double quotes (ASCII and curly) for dialogue extraction
QUOTE_SPAN_RE = re.compile(r'([\"\u201c])([^\"\u201c\u201d]+?)([\"\u201d])')

SPEECH_VERBS = {
    "said", "says", "asked", "replied", "answered", "added", "continued",
    "offered", "called", "shouted", "yelled", "snapped", "muttered", "growled",
    "hissed", "spat", "barked", "laughed", "cried", "begged", "warned", "told",
    "agreed", "countered", "whispered", "gasped", "breathed", "panted",
    "murmured", "moaned", "sighed", "choked", "sobbed", "whimpered", "croaked",
}

EMOTION_CUES = {
    "whispered": ("whisper", {"speed": 0.94, "pitch": -0.02, "volume": -3.0}),
    "murmured": ("soft", {"speed": 0.95, "pitch": -0.01, "volume": -2.0}),
    "sighed": ("weary", {"speed": 0.93, "pitch": -0.02, "volume": -1.5}),
    "gasped": ("tense", {"speed": 1.05, "pitch": 0.03, "volume": 0.0}),
    "panted": ("breathless", {"speed": 1.06, "pitch": 0.02, "volume": -0.5}),
    "shouted": ("urgent", {"speed": 1.08, "pitch": 0.04, "volume": 2.5}),
    "yelled": ("urgent", {"speed": 1.08, "pitch": 0.04, "volume": 2.5}),
    "snapped": ("sharp", {"speed": 1.06, "pitch": 0.02, "volume": 1.0}),
    "hissed": ("tense", {"speed": 1.02, "pitch": 0.01, "volume": -1.0}),
    "growled": ("low", {"speed": 0.94, "pitch": -0.04, "volume": 0.5}),
    "laughed": ("wry", {"speed": 1.02, "pitch": 0.02, "volume": 0.5}),
    "sobbed": ("grief", {"speed": 0.90, "pitch": -0.02, "volume": -1.0}),
    "cried": ("strained", {"speed": 1.03, "pitch": 0.03, "volume": 1.0}),
}

PARALINGUISTIC_CUES = {
    "sighed": "[sigh]",
    "sigh": "[sigh]",
    "gasped": "[breath]",
    "panted": "[breath]",
    "breathed": "[breath]",
    "laughed": "[laughter]",
    "chuckled": "[laughter]",
}

DEFAULT_PAUSES_MS = {
    "heading_after": 1400,
    "sentence_after": 350,
    "paragraph_after": 650,
    "dialogue_turn_after": 450,
    "attribution_after": 220,
    "scene_break": 2200,
    "chapter_end": 3500,
}

DEFAULT_STYLE = {
    "speed": 1.0,
    "pitch": 0.0,
    "volume": 0.0,
    "emotion": "neutral",
}


# ---------------------------------------------------------------------------
# Number, Date, Currency, & Abbreviation Normalizer (stdlib only)
# ---------------------------------------------------------------------------

ONES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen",
]
TENS = [
    "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
]
ORDINAL_ONES = [
    "zeroth", "first", "second", "third", "fourth", "fifth", "sixth", "seventh",
    "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth",
    "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth",
]
ORDINAL_TENS = [
    "", "", "twentieth", "thirtieth", "fortieth", "fiftieth", "sixtieth",
    "seventieth", "eightieth", "ninetieth",
]


def int_to_words(n):
    """Convert non-negative integer n to spoken English words."""
    if n < 0:
        return "minus " + int_to_words(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        t, r = divmod(n, 10)
        return TENS[t] if r == 0 else f"{TENS[t]}-{ONES[r]}"
    if n < 1000:
        h, r = divmod(n, 100)
        return f"{ONES[h]} hundred" if r == 0 else f"{ONES[h]} hundred {int_to_words(r)}"
    if n < 1_000_000:
        th, r = divmod(n, 1000)
        return f"{int_to_words(th)} thousand" if r == 0 else f"{int_to_words(th)} thousand {int_to_words(r)}"
    if n < 1_000_000_000:
        m, r = divmod(n, 1_000_000)
        return f"{int_to_words(m)} million" if r == 0 else f"{int_to_words(m)} million {int_to_words(r)}"
    return str(n)


def ordinal_to_words(n):
    """Convert positive integer n to spoken ordinal words (1st -> first, 23rd -> twenty-third)."""
    if n < 20:
        return ORDINAL_ONES[n]
    if n < 100:
        t, r = divmod(n, 10)
        return ORDINAL_TENS[t] if r == 0 else f"{TENS[t]}-{ORDINAL_ONES[r]}"
    words = int_to_words(n)
    if words.endswith("y"):
        return words[:-1] + "ieth"
    for idx, word in enumerate(ONES[1:], 1):
        if words.endswith(word):
            return words[:-len(word)] + ORDINAL_ONES[idx]
    return words + "th"


def year_to_words(y):
    """Convert 4-digit year (1000-2099) to spoken English year."""
    if 2000 <= y <= 2009:
        return int_to_words(y)
    if 2010 <= y <= 2099:
        hi, lo = divmod(y, 100)
        return f"{int_to_words(hi)} {int_to_words(lo)}"
    if 1100 <= y <= 1999:
        hi, lo = divmod(y, 100)
        if lo == 0:
            return f"{int_to_words(hi)} hundred"
        if lo < 10:
            return f"{int_to_words(hi)} oh {ONES[lo]}"
        return f"{int_to_words(hi)} {int_to_words(lo)}"
    return int_to_words(y)


ABBREVIATIONS = [
    (re.compile(r"\bMrs\.(?=\s|$)"), "Missus"),
    (re.compile(r"\bMr\.(?=\s|$)"), "Mister"),
    (re.compile(r"\bMs\.(?=\s|$)"), "Miz"),
    (re.compile(r"\bDr\.(?=\s|$)"), "Doctor"),
    (re.compile(r"\bProf\.(?=\s|$)"), "Professor"),
    (re.compile(r"\bSt\.(?=\s+[A-Z])"), "Saint"),
    (re.compile(r"\bSgt\.(?=\s|$)"), "Sergeant"),
    (re.compile(r"\bCapt\.(?=\s|$)"), "Captain"),
    (re.compile(r"\bLt\.(?=\s|$)"), "Lieutenant"),
    (re.compile(r"\bCol\.(?=\s|$)"), "Colonel"),
    (re.compile(r"\bGen\.(?=\s|$)"), "General"),
    (re.compile(r"\bRev\.(?=\s|$)"), "Reverend"),
    (re.compile(r"\bJr\.(?=\s|,|$)"), "Junior"),
    (re.compile(r"\bSr\.(?=\s|,|$)"), "Senior"),
    (re.compile(r"\bvs\.(?=\s|$)", re.I), "versus"),
    (re.compile(r"\betc\.(?=\s|,|$)", re.I), "et cetera"),
    (re.compile(r"\be\.g\.(?=\s|,|$)", re.I), "for example"),
    (re.compile(r"\bi\.e\.(?=\s|,|$)", re.I), "that is"),
    (re.compile(r"\bno\.\s*(\d+)\b", re.I), lambda m: f"number {int_to_words(int(m.group(1)))}"),
]


def normalize_spoken_text(text):
    """Expand abbreviations, symbols, currencies, ordinals, years, and cardinal numbers
    into clean spoken form for TTS synthesis."""
    s = text.strip()
    if not s:
        return ""

    # Normalize typography for TTS
    s = s.replace("\u2014", " — ").replace("\u2013", " – ")
    s = s.replace("\u2026", "...")
    s = re.sub(r"\s*&\s*", " and ", s)

    # Expand abbreviations first
    for pat, repl in ABBREVIATIONS:
        s = pat.sub(repl, s)

    # Currency: £11, $45.50, €100
    def _currency_repl(m):
        sym, whole_s, dec_s = m.group(1), m.group(2).replace(",", ""), m.group(3)
        whole = int(whole_s)
        unit_map = {"$": ("dollar", "dollars", "cent", "cents"),
                    "£": ("pound", "pounds", "penny", "pence"),
                    "€": ("euro", "euros", "cent", "cents")}
        u_sing, u_pl, c_sing, c_pl = unit_map[sym]
        w_words = int_to_words(whole) + " " + (u_sing if whole == 1 else u_pl)
        if dec_s:
            dec = int(dec_s)
            if dec > 0:
                c_words = int_to_words(dec) + " " + (c_sing if dec == 1 else c_pl)
                return f"{w_words} and {c_words}"
        return w_words

    s = re.sub(r"([$£€])(\d[\d,]*)(?:\.(\d{1,2}))?\b", _currency_repl, s)

    # Percentages: 22% -> twenty-two percent
    def _pct_repl(m):
        whole = int(m.group(1))
        dec = m.group(2)
        if dec:
            dec_words = " ".join(ONES[int(d)] for d in dec)
            return f"{int_to_words(whole)} point {dec_words} percent"
        return f"{int_to_words(whole)} percent"

    s = re.sub(r"\b(\d+)(?:\.(\d+))?%", _pct_repl, s)

    # Slash dates or incident codes like 2022/114
    def _slash_num_repl(m):
        a, b = int(m.group(1)), int(m.group(2))
        a_w = year_to_words(a) if 1800 <= a <= 2099 else int_to_words(a)
        b_w = " ".join(ONES[int(d)] for d in m.group(2)) if len(m.group(2)) == 3 else int_to_words(b)
        return f"{a_w} slash {b_w}"

    s = re.sub(r"\b(\d{4})/(\d{1,4})\b", _slash_num_repl, s)

    # Ordinals: 1st, 2nd, 3rd, 4th, 21st
    def _ord_repl(m):
        return ordinal_to_words(int(m.group(1)))

    s = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", _ord_repl, s, flags=re.I)

    # Decades: 1990s -> nineteen nineties
    def _decade_repl(m):
        y = int(m.group(1))
        hi, lo = divmod(y, 100)
        decade_names = {
            0: "hundreds", 10: "tens", 20: "twenties", 30: "thirties",
            40: "forties", 50: "fifties", 60: "sixties", 70: "seventies",
            80: "eighties", 90: "nineties",
        }
        if hi in range(15, 21) and lo in decade_names:
            return f"{int_to_words(hi)} {decade_names[lo]}"
        return m.group(0)

    s = re.sub(r"\b(1[5-9]\d0|20\d0)s\b", _decade_repl, s)

    # Decimal numbers: 3.14 -> three point one four
    def _dec_repl(m):
        whole = int(m.group(1).replace(",", ""))
        dec = m.group(2)
        dec_words = " ".join(ONES[int(d)] for d in dec)
        return f"{int_to_words(whole)} point {dec_words}"

    s = re.sub(r"\b(\d[\d,]*)\.(\d+)\b", _dec_repl, s)

    # Comma-grouped integers: 78,070 -> seventy-eight thousand seventy
    def _comma_int_repl(m):
        val = int(m.group(0).replace(",", ""))
        return int_to_words(val)

    s = re.sub(r"\b\d{1,3}(?:,\d{3})+\b", _comma_int_repl, s)

    # 4-digit years (1500–2099) vs plain cardinal integers
    def _int_repl(m):
        val = int(m.group(0))
        if 1500 <= val <= 2099:
            return year_to_words(val)
        return int_to_words(val)

    s = re.sub(r"\b\d+\b", _int_repl, s)

    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------------------------------------------------------------------------
# Gate & Freeze Verification
# ---------------------------------------------------------------------------

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify_gate_freeze():
    """Verify live tools/prose files against GATE_FREEZE.md manifest (same contract
    as tools/prose/verify-freeze.sh, in pure stdlib Python so it executes in <10ms
    with zero Windows subprocess/pipe overhead)."""
    freeze_path = os.path.join(ROOT_DIR, "GATE_FREEZE.md")
    if not os.path.isfile(freeze_path):
        return False, f"no GATE_FREEZE.md at {freeze_path}"
    try:
        with open(freeze_path, "rb") as fh:
            raw = fh.read().decode("utf-8", errors="replace")
    except OSError as exc:
        return False, f"cannot read {freeze_path}: {exc}"

    manifest_part = raw.split("\n## Freeze", 1)[0]
    row_re = re.compile(r"`tools/prose/([a-zA-Z0-9_/-]+\.(?:sh|py|tsv|md))`\s*\|\s*`([0-9a-f]{16})`")
    rows = row_re.findall(manifest_part)
    if not rows:
        return False, f"no manifest rows found in {freeze_path}"

    prose_dir = os.path.join(TOOLS_DIR, "prose")
    for rel_name, want_hash in rows:
        fpath = os.path.join(prose_dir, rel_name)
        if not os.path.isfile(fpath):
            return False, f"frozen gate file MISSING: tools/prose/{rel_name}"
        with open(fpath, "rb") as fh:
            got_hash = hashlib.sha256(fh.read()).hexdigest()[:16]
        if got_hash != want_hash:
            return False, f"frozen gate file CHANGED: tools/prose/{rel_name} (got {got_hash}, frozen {want_hash})"
    return True, "FREEZE HOLDS"


def check_freeze_and_completion(book_root):
    """Enforce Refusal Tests #1 and #3 before building any narration script:
      - GATE_FREEZE manifest must hold (`FREEZE HOLDS`)
      - PROJECT_STATE.yaml must exist and NOT be in_progress / drafting / concept
      - check-pass-evidence.py must report 0 missing pass files and >0 gated words
      - check-lexicon.py must exit 0 (every proper noun mapped or waived)
    Returns (ok, reason_list, lexicon_report).
    """
    reasons = []

    # 1. GATE_FREEZE verification
    freeze_ok, freeze_msg = verify_gate_freeze()
    if not freeze_ok:
        reasons.append(f"verify-freeze failed: {freeze_msg}")

    # 2. PROJECT_STATE.yaml completion check
    state_path = os.path.join(book_root, "PROJECT_STATE.yaml")
    if not os.path.isfile(state_path):
        reasons.append(f"missing PROJECT_STATE.yaml at {state_path} — book is ungoverned")
        return False, reasons, None

    try:
        with open(state_path, "r", encoding="utf-8") as fh:
            state_text = fh.read()
    except OSError as exc:
        reasons.append(f"cannot read {state_path}: {exc}")
        return False, reasons, None

    # Extract project.status, phase.status, and runner.status without backtracking
    def _extract_section_field(text, section_name, field_name):
        in_sec = False
        for raw_line in text.splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip())
            if indent == 0:
                in_sec = raw_line.strip().startswith(f"{section_name}:")
                continue
            if in_sec:
                m = re.match(rf"^[ \t]+{re.escape(field_name)}:\s*[\"']?([A-Za-z0-9_-]+)[\"']?", raw_line)
                if m:
                    return m.group(1).lower()
        return ""

    proj_status = _extract_section_field(state_text, "project", "status")
    phase_status = _extract_section_field(state_text, "phase", "status")
    runner_status = _extract_section_field(state_text, "runner", "status")

    incomplete_statuses = {"in_progress", "drafting", "concept", "halted", "pending", "running"}
    completed_statuses = {"complete", "completed", "gate_passed", "published"}

    if runner_status == "halted":
        reasons.append(
            "PROJECT_STATE.yaml runner.status is HALTED — prose phase runner halted at an earlier gate"
        )
    if proj_status in incomplete_statuses or phase_status in incomplete_statuses:
        reasons.append(
            f"manuscript is not frozen/complete (project.status={proj_status or 'unset'!r}, "
            f"phase.status={phase_status or 'unset'!r}) — audiobook stage requires a completed manuscript"
        )
    elif proj_status not in completed_statuses and phase_status not in completed_statuses:
        reasons.append(
            f"manuscript does not declare completion in PROJECT_STATE.yaml "
            f"(project.status={proj_status or 'unset'!r}, phase.status={phase_status or 'unset'!r})"
        )

    # Check if PROJECT_STATE.yaml records any prose gate with exit: 1 / FAIL without waiver
    for gate_line in re.finditer(
        r"^[ \t]+([a-z_]+):\s*\{[^}]*\bresult:\s*\"FAIL\"[^}]*\}",
        state_text, re.M,
    ):
        gname = gate_line.group(1)
        reasons.append(
            f"PROJECT_STATE.yaml records failed prose gate '{gname}: FAIL' — "
            f"cannot enter audiobook stage on a manuscript with an unresolved gate failure"
        )

    if re.search(r"^length_gate:\s*\"?FAIL\"?", state_text, re.M):
        reasons.append(
            "PROJECT_STATE.yaml records 'length_gate: FAIL' — manuscript failed length contract"
        )

    # 3. Pass evidence check (`tools/check-pass-evidence.py`)
    ev_path = os.path.join(TOOLS_DIR, "check-pass-evidence.py")
    if not os.path.isfile(ev_path):
        reasons.append(f"missing {ev_path}")
    else:
        ev_mod = load_module("check_pass_evidence", ev_path)
        rep = ev_mod.evidence_report(book_root)
        if "error" in rep:
            reasons.append(f"check-pass-evidence: {rep['error']}")
        elif rep["missing"]:
            missing_names = ", ".join(n for n, _ in rep["missing"][:5])
            reasons.append(
                f"check-pass-evidence failed: {len(rep['missing'])} of {rep['chapters']} "
                f"chapter(s) missing pass evidence ({missing_names})"
            )
        elif rep["gated_words"] == 0:
            reasons.append("check-pass-evidence failed: 0 gated words")

    if reasons:
        return False, reasons, None

    return True, [], None


# ---------------------------------------------------------------------------
# Cast & Speaker Attribution
# ---------------------------------------------------------------------------

def load_book_cast_and_audio_config(book_root):
    """Load cast names/aliases and any audiobook voice/style config from the book."""
    cast_map = {}  # alias_lower -> canonical_speaker_id
    character_styles = {}  # canonical_speaker_id -> style dict
    narrator_style = dict(DEFAULT_STYLE)
    paralinguistic_cap = 2
    pauses = dict(DEFAULT_PAUSES_MS)

    # Read CANON_LEDGER.yaml / ENTITY_STATE.yaml for cast declarations
    for fname in ("CANON_LEDGER.yaml", "ENTITY_STATE.yaml"):
        fpath = os.path.join(book_root, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue

        # Match blocks with canonical_name / name / called_in_prose
        for m in re.finditer(
            r"(?:canonical_name|name)\s*:\s*[\"']?([A-Z][A-Za-z'’ -]+?)[\"']?\s*(?:#.*)?$",
            text, re.M,
        ):
            full = m.group(1).strip()
            parts = full.split()
            if not parts:
                continue
            canon = parts[0] if len(parts) == 1 else full
            cast_map[full.lower()] = canon
            cast_map[parts[0].lower()] = canon
            if len(parts) > 1:
                cast_map[parts[-1].lower()] = canon

        for m in re.finditer(
            r"called_in_prose\s*:\s*[\"']?([A-Z][A-Za-z'’ -]+?)[\"']?\s*(?:#.*)?$",
            text, re.M,
        ):
            called = m.group(1).strip()
            if called.lower() not in cast_map:
                cast_map[called.lower()] = called

    # Read optional audiobook config (audiobook/config.yaml or PROJECT_STATE.yaml audiobook block)
    cfg_path = os.path.join(book_root, "audiobook", "config.yaml")
    if os.path.isfile(cfg_path):
        try:
            import yaml
            with open(cfg_path, "r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}
            if isinstance(cfg, dict):
                ab = cfg.get("audiobook", cfg)
                if isinstance(ab, dict):
                    if "paralinguistic_cap_per_chapter" in ab:
                        paralinguistic_cap = int(ab["paralinguistic_cap_per_chapter"])
                    if isinstance(ab.get("pauses_ms"), dict):
                        for k, v in ab["pauses_ms"].items():
                            pauses[k] = int(v)
                    voices = ab.get("voices") or ab.get("cast") or {}
                    if isinstance(voices, dict):
                        for v_id, v_cfg in voices.items():
                            if not isinstance(v_cfg, dict):
                                continue
                            st = dict(DEFAULT_STYLE)
                            if isinstance(v_cfg.get("style"), dict):
                                st.update(v_cfg["style"])
                            if v_id.upper() == "NARRATOR":
                                narrator_style = st
                            else:
                                character_styles[v_id] = st
                                cast_map[v_id.lower()] = v_id
                                for alias in v_cfg.get("aliases", []):
                                    cast_map[str(alias).lower()] = v_id
        except Exception:
            pass

    return cast_map, character_styles, narrator_style, paralinguistic_cap, pauses


def attribute_dialogue(paragraph_text, quote_start, quote_end, cast_map, last_speakers):
    """Determine speaker and emotion/paralinguistic cue for a quoted dialogue span."""
    after = paragraph_text[quote_end:min(len(paragraph_text), quote_end + 140)]
    before = paragraph_text[max(0, quote_start - 140):quote_start]

    speaker = None
    detected_verb = None

    # Look for verb + speaker in after window or before window
    for window in (after, before):
        for w_m in re.finditer(r"\b([A-Za-z'’-]+)\b", window):
            tok = w_m.group(1)
            tok_low = tok.lower()
            if tok_low in SPEECH_VERBS and detected_verb is None:
                detected_verb = tok_low
            clean_tok = tok_low
            for suf in ("'s", "\u2019s"):
                if clean_tok.endswith(suf):
                    clean_tok = clean_tok[:-len(suf)]
            if clean_tok in cast_map and speaker is None:
                speaker = cast_map[clean_tok]

    # Fallback: check anywhere in the paragraph for a cast name if not in immediate window
    if speaker is None:
        for w_m in re.finditer(r"\b([A-Z][a-z'’-]+)\b", paragraph_text):
            tok_low = w_m.group(1).lower()
            if tok_low in cast_map:
                speaker = cast_map[tok_low]
                break

    # Conversational turn-taking fallback for two-hander alternating lines
    if speaker is None:
        if len(last_speakers) >= 2 and last_speakers[-1] != last_speakers[-2]:
            speaker = last_speakers[-2]
        elif len(last_speakers) == 1:
            speaker = last_speakers[-1]
        else:
            speaker = "NARRATOR"

    return speaker, detected_verb


def build_chapter_script(
    ch_num,
    ch_filename,
    ch_text,
    lexicon_entries,
    cast_map,
    character_styles,
    narrator_style,
    paralinguistic_cap,
    pauses,
):
    """Split one chapter's markdown into structured narration script segments."""
    segments = []
    seg_counter = 0
    paralinguistic_counts = {}  # speaker -> count in this chapter
    last_speakers = []

    def next_seg_id():
        nonlocal seg_counter
        seg_counter += 1
        return f"ch{ch_num:02d}-seg{seg_counter:04d}"

    def find_lexicon_hits(raw_span):
        hits = []
        seen = set()
        for m in re.finditer(r"\b([A-Z][a-zA-Z'’-]{1,})\b", raw_span):
            tok = m.group(1)
            for suf in ("'s", "\u2019s", "s'", "s\u2019"):
                if tok.endswith(suf):
                    tok = tok[:-len(suf)]
            low = tok.lower()
            if low in lexicon_entries and low not in seen:
                seen.add(low)
                ent = lexicon_entries[low]
                hits.append({
                    "term": tok,
                    "ipa": ent["ipa"],
                    "respelling": ent["respelling"],
                })
        return hits

    # Group lines into paragraphs / headings / scene breaks
    lines = ch_text.splitlines()
    blocks = []
    buf = []

    def flush_buf():
        if buf:
            blocks.append(("paragraph", "\n".join(buf).strip()))
            buf.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_buf()
            continue
        hm = HEADING_RE.match(stripped)
        if hm:
            flush_buf()
            blocks.append(("heading", hm.group(2).strip()))
            continue
        if SCENE_BREAK_RE.match(stripped):
            flush_buf()
            blocks.append(("scene_break", stripped))
            continue
        buf.append(stripped)
    flush_buf()

    for bkind, btext in blocks:
        if bkind == "heading":
            clean_head = re.sub(r"\s+", " ", btext).strip()
            # If heading is bare number like "1", expand to "Chapter One"
            if clean_head.isdigit():
                spoken_head = f"Chapter {int_to_words(int(clean_head)).title()}"
            else:
                spoken_head = normalize_spoken_text(clean_head)
            segments.append({
                "segment_id": next_seg_id(),
                "kind": "heading",
                "speaker": "NARRATOR",
                "raw_text": clean_head,
                "spoken_text": spoken_head,
                "style": dict(narrator_style),
                "paralinguistic_tags": [],
                "pause_after_ms": pauses["heading_after"],
                "lexicon_hits": find_lexicon_hits(clean_head),
            })
            continue

        if bkind == "scene_break":
            segments.append({
                "segment_id": next_seg_id(),
                "kind": "pause",
                "speaker": "NARRATOR",
                "raw_text": btext,
                "spoken_text": "",
                "style": dict(narrator_style),
                "paralinguistic_tags": [],
                "pause_after_ms": pauses["scene_break"],
                "lexicon_hits": [],
            })
            last_speakers.clear()
            continue

        # Paragraph: split into interleaved narration and quoted dialogue spans
        para = re.sub(r"\s+", " ", btext).strip()
        quotes = list(QUOTE_SPAN_RE.finditer(para))
        if not quotes:
            spoken = normalize_spoken_text(para)
            segments.append({
                "segment_id": next_seg_id(),
                "kind": "narration",
                "speaker": "NARRATOR",
                "raw_text": para,
                "spoken_text": spoken,
                "style": dict(narrator_style),
                "paralinguistic_tags": [],
                "pause_after_ms": pauses["paragraph_after"],
                "lexicon_hits": find_lexicon_hits(para),
            })
            continue

        # Interleaved dialogue + narration/attribution within the paragraph
        cursor = 0
        pieces = []
        for qm in quotes:
            if qm.start() > cursor:
                nar_span = para[cursor:qm.start()].strip()
                # Strip leading/trailing孤立 punctuation that only joined the quote
                nar_clean = nar_span.strip(" ,;:")
                if nar_clean:
                    pieces.append(("narration", nar_span, qm.start(), qm.end()))
            q_inner = qm.group(2).strip()
            if q_inner:
                pieces.append(("dialogue", q_inner, qm.start(), qm.end()))
            cursor = qm.end()

        if cursor < len(para):
            tail_span = para[cursor:].strip()
            tail_clean = tail_span.strip(" ,;:")
            if tail_clean:
                pieces.append(("narration", tail_span, cursor, len(para)))

        for idx, (pkind, ptext, q_start, q_end) in enumerate(pieces):
            is_last_in_para = (idx == len(pieces) - 1)
            if pkind == "narration":
                # Clean leading lowercase conjunction/comma attached to dialogue attribution
                nar_raw = ptext.strip()
                nar_for_tts = nar_raw.strip(" ,")
                spoken = normalize_spoken_text(nar_for_tts)
                if not spoken:
                    continue
                segments.append({
                    "segment_id": next_seg_id(),
                    "kind": "narration",
                    "speaker": "NARRATOR",
                    "raw_text": nar_raw,
                    "spoken_text": spoken,
                    "style": dict(narrator_style),
                    "paralinguistic_tags": [],
                    "pause_after_ms": pauses["paragraph_after"] if is_last_in_para else pauses["attribution_after"],
                    "lexicon_hits": find_lexicon_hits(nar_raw),
                })
            else:
                speaker, verb = attribute_dialogue(para, q_start, q_end, cast_map, last_speakers)
                if speaker != "NARRATOR":
                    last_speakers.append(speaker)

                base_style = dict(character_styles.get(speaker, DEFAULT_STYLE))
                if verb and verb in EMOTION_CUES:
                    emo_name, emo_mods = EMOTION_CUES[verb]
                    base_style["emotion"] = emo_name
                    base_style["speed"] = round(base_style.get("speed", 1.0) * emo_mods["speed"], 3)
                    base_style["pitch"] = round(base_style.get("pitch", 0.0) + emo_mods["pitch"], 3)
                    base_style["volume"] = round(base_style.get("volume", 0.0) + emo_mods["volume"], 2)

                # Rationed paralinguistic tags: capped at `paralinguistic_cap` per speaker per chapter
                tags = []
                if verb and verb in PARALINGUISTIC_CUES:
                    used = paralinguistic_counts.get(speaker, 0)
                    if used < paralinguistic_cap:
                        tag = PARALINGUISTIC_CUES[verb]
                        tags.append(tag)
                        paralinguistic_counts[speaker] = used + 1

                # Clean trailing comma inside dialogue quote when followed by attribution ("Oh," he said -> "Oh.")
                dlg_for_tts = ptext.strip()
                if dlg_for_tts.endswith(","):
                    dlg_for_tts = dlg_for_tts[:-1] + "."
                spoken = normalize_spoken_text(dlg_for_tts)
                if tags:
                    spoken = f"{tags[0]} {spoken}"

                segments.append({
                    "segment_id": next_seg_id(),
                    "kind": "dialogue",
                    "speaker": speaker,
                    "raw_text": ptext,
                    "spoken_text": spoken,
                    "style": base_style,
                    "paralinguistic_tags": tags,
                    "pause_after_ms": pauses["paragraph_after"] if is_last_in_para else pauses["dialogue_turn_after"],
                    "lexicon_hits": find_lexicon_hits(ptext),
                })

    # Explicit chapter-end pause on final segment
    if segments:
        segments[-1]["pause_after_ms"] = pauses["chapter_end"]

    speakers_used = sorted({s["speaker"] for s in segments if s["kind"] != "pause"})
    dialogue_count = sum(1 for s in segments if s["kind"] == "dialogue")
    narration_count = sum(1 for s in segments if s["kind"] in ("narration", "heading"))

    return {
        "schema": "incunabula.audiobook.script.v1",
        "chapter": ch_num,
        "source_file": f"manuscript/chapters/{ch_filename}",
        "source_sha256": hashlib.sha256(ch_text.encode("utf-8")).hexdigest(),
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "paralinguistic_cap_per_chapter": paralinguistic_cap,
        "paralinguistic_usage": paralinguistic_counts,
        "summary": {
            "total_segments": len(segments),
            "narration_segments": narration_count,
            "dialogue_segments": dialogue_count,
            "pause_segments": sum(1 for s in segments if s["kind"] == "pause"),
            "speakers": speakers_used,
        },
        "segments": segments,
    }


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", newline="\n")
    ap = argparse.ArgumentParser(description="Build structured narration scripts from a frozen manuscript.")
    ap.add_argument("book", help="Path to the book root directory")
    ap.add_argument("--chapter", default=None, help="Optional single chapter number or filename")
    ap.add_argument("--paralinguistic-cap", type=int, default=None,
                    help="Max paralinguistic tags per character per chapter (default: 2)")
    ap.add_argument("--out-dir", default=None,
                    help="Output directory (default: <book>/audiobook/scripts)")
    args = ap.parse_args(argv)

    book_root = os.path.abspath(args.book)
    if not os.path.isdir(book_root):
        print(f"build-script: no such book directory: {book_root}", file=sys.stderr)
        return 2

    # 1. Verify freeze and manuscript completion gates (Refusal Test #1)
    ok, reasons, _ = check_freeze_and_completion(book_root)
    if not ok:
        print(f"build-script: REFUSED — manuscript at {book_root} has not cleared the prose freeze/completion gates:",
              file=sys.stderr)
        for r in reasons:
            print(f"  - {r}", file=sys.stderr)
        return 1

    # 2. Run the pronunciation lexicon check (Refusal Test #3)
    lex_mod = load_module("check_lexicon", os.path.join(HERE, "check-lexicon.py"))
    lex_rc, lex_rep = lex_mod.audit_book_lexicon(book_root, args.chapter)
    if lex_rc != 0:
        print(f"build-script: REFUSED — pronunciation lexicon gate failed (exit {lex_rc}):",
              file=sys.stderr)
        if "reason" in lex_rep:
            print(f"  - {lex_rep['reason']}", file=sys.stderr)
        for u in lex_rep.get("unmapped", []):
            print(f"  - unmapped proper noun: {u['token']} (first at {u['first_seen']})", file=sys.stderr)
        return 1 if lex_rc == 1 else lex_rc

    lex_path = os.path.join(book_root, "audiobook", "lexicon.yaml")
    lexicon_entries, _, _ = lex_mod.load_lexicon(lex_path)

    # 3. Load cast, styles, and chapter files
    cast_map, character_styles, narrator_style, cfg_cap, pauses = load_book_cast_and_audio_config(book_root)
    cap = args.paralinguistic_cap if args.paralinguistic_cap is not None else cfg_cap

    chapters = lex_mod.resolve_chapters(book_root, args.chapter)
    if not chapters:
        print(f"build-script: no chapters found under {book_root}/manuscript/chapters", file=sys.stderr)
        return 2

    out_dir = os.path.abspath(args.out_dir) if args.out_dir else os.path.join(book_root, "audiobook", "scripts")
    os.makedirs(out_dir, exist_ok=True)

    written_files = []
    total_segs = 0
    for ch_num, ch_fname, ch_text in chapters:
        script_obj = build_chapter_script(
            ch_num=ch_num,
            ch_filename=ch_fname,
            ch_text=ch_text,
            lexicon_entries=lexicon_entries,
            cast_map=cast_map,
            character_styles=character_styles,
            narrator_style=narrator_style,
            paralinguistic_cap=cap,
            pauses=pauses,
        )
        out_path = os.path.join(out_dir, f"chapter-{ch_num:02d}.json")
        with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(script_obj, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        written_files.append((ch_num, out_path, script_obj["summary"]))
        total_segs += script_obj["summary"]["total_segments"]

    print("=" * 67)
    print(f"## build-script   {book_root}")
    print("=" * 67)
    print(f"   chapters built:     {len(written_files)}")
    print(f"   total segments:     {total_segs}")
    print(f"   paralinguistic cap: {cap} per speaker per chapter")
    print(f"   lexicon entries:    {len(lexicon_entries)} indexed forms")
    for ch_num, out_path, summ in written_files:
        rel_out = os.path.relpath(out_path, book_root).replace("\\", "/")
        print(f"   - ch-{ch_num:02d} -> {rel_out} "
              f"({summ['total_segments']} segs: {summ['narration_segments']} nar, "
              f"{summ['dialogue_segments']} dlg, speakers={summ['speakers']})")
    print()
    print("SCRIPTS BUILT OK — freeze verified, lexicon clean, narration scripts ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
