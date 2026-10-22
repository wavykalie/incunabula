#!/usr/bin/env python3
"""check-lexicon.py — proper-noun pronunciation lexicon gate for the audiobook stage.

WHY THIS EXISTS
  TTS synthesis guesses at proper nouns it has never been told how to say: character
  names, fictional places, technical terms, foreign-origin names, and titled entities
  get pronounced differently from chapter to chapter or misstressed on first appearance.
  A narration script that reaches synthesis without a pronunciation entry for every
  proper noun is relying on a model's guess, and a guess is not a specification.

  This gate reads the book's cast/entity declarations (CANON_LEDGER.yaml,
  ENTITY_STATE.yaml, characters.md, cast.md, voice-matrix.md) AND scans the manuscript
  chapters for proper-noun tokens, then verifies that every proper noun is either:
    1. Mapped in the book's pronunciation lexicon (`audiobook/lexicon.yaml`), OR
    2. Explicitly waived in `maintenance/WAIVERS.md` with a recorded reason
       (rule `lexicon` or `lexicon:<term>`).

  An absent `audiobook/lexicon.yaml` is NOT a pass and does NOT silently create an
  empty lexicon: not-run is never a pass.

LEXICON FORMAT (`audiobook/lexicon.yaml`)
  Strict or standard YAML / key-value structure:

    meta:
      language: "en"
      alphabet: "ipa+respelling"
    entries:
      Ines:
        ipa: "iːˈnɛs"
        respelling: "ee-NESS"
        note: "protagonist first name"
      "Ines Varga":
        ipa: "iːˈnɛs ˈvɑːrɡə"
        respelling: "ee-NESS VAR-guh"

  Or a flat mapping under `lexicon:` or `entries:` where each key maps to either a
  dict with at least one of (`ipa`, `respelling`, `phonetic`, `pronunciation`, `say_as`)
  or a non-empty phonetic string. An entry with an empty value is refused (exit 3).

USAGE
  python tools/audio/check-lexicon.py <book-root> [--chapter <path-or-num>] [--json]

EXIT CODES
  0  LEXICON OK — every proper noun is mapped in audiobook/lexicon.yaml or waived
     in maintenance/WAIVERS.md
  1  LEXICON FAIL — one or more unmapped, unwaived proper nouns found (named with
     chapter and line numbers)
  2  NOT RUN — missing audiobook/lexicon.yaml or no chapters to scan (never a pass)
  3  REFUSED — malformed lexicon entry or unreadable file
"""

import argparse
import json
import os
import re
import sys

CHAPTER_RE = re.compile(r"chapter[-_ ]?0*(\d+)\.(md|txt)$", re.I)

# Standard English non-proper tokens that appear capitalised at sentence start,
# in headings, or in dialogue openings. A proper noun is a capitalised token that
# either (a) is declared in the book's canon/entity files, or (b) appears mid-sentence
# capitalised (or never appears lowercase in the manuscript and is not a common
# English function/starter word, calendar word, or roman numeral).
STOP_WORDS = {
    # Calendar & time
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "Today", "Tonight", "Tomorrow", "Yesterday", "Morning", "Afternoon", "Evening", "Night",
    # Pronouns, determiners, conjunctions, prepositions, common starters
    "I", "Me", "My", "Mine", "Myself", "We", "Us", "Our", "Ours", "Ourselves",
    "You", "Your", "Yours", "Yourself", "Yourselves",
    "He", "Him", "His", "Himself", "She", "Her", "Hers", "Herself",
    "It", "Its", "Itself", "They", "Them", "Their", "Theirs", "Themselves",
    "The", "A", "An", "This", "That", "These", "Those",
    "And", "But", "Or", "Nor", "For", "Yet", "So",
    "In", "On", "At", "To", "From", "By", "With", "Without", "Within",
    "Into", "Onto", "Upon", "Out", "Off", "Over", "Under", "Above", "Below",
    "Through", "Across", "Behind", "Beyond", "Between", "Among", "Around",
    "Before", "After", "During", "Until", "Till", "Since", "While", "When", "Where",
    "Why", "How", "What", "Which", "Who", "Whom", "Whose", "Whether",
    "If", "Unless", "Although", "Though", "Because", "As", "Than", "Then",
    "There", "Here", "Now", "Still", "Already", "Just", "Only", "Even", "Also",
    "Too", "Very", "Quite", "Rather", "Almost", "Enough", "Indeed", "Perhaps",
    "Maybe", "Probably", "Certainly", "Surely", "Really", "Actually", "Finally",
    "Suddenly", "Quickly", "Slowly", "Quietly", "Softly", "Loudly", "Carefully",
    "Hardly", "Barely", "Scarcely", "Nearly", "Mostly", "Usually", "Often",
    "Sometimes", "Always", "Never", "Ever", "Again", "Once", "Twice", " Together",
    "Away", "Back", "Down", "Up", "Left", "Right", "North", "South", "East", "West",
    # Numbers & quantifiers
    "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
    "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen",
    "Eighteen", "Nineteen", "Twenty", "Thirty", "Forty", "Fifty", "Sixty",
    "Seventy", "Eighty", "Ninety", "Hundred", "Thousand", "Million", "Billion",
    "First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth",
    "Ninth", "Tenth", "Last", "Next", "Other", "Another", "Each", "Every", "Either",
    "Neither", "Both", "All", "Some", "Any", "No", "None", "Nothing", "Something",
    "Anything", "Everything", "Someone", "Anyone", "Everyone", "Nobody", "Somebody",
    "Anybody", "Everybody", "Somewhere", "Anywhere", "Everywhere", "Nowhere",
    "Few", "Little", "Many", "Much", "More", "Most", "Several", "Such", "Same",
    "Own", "Enough", "Half", "Whole",
    # Common dialogue openers, interjections, imperatives, & titles/headings
    "Yes", "Yeah", "Yep", "No", "Nope", "Nah", "Oh", "Ah", "Uh", "Um", "Hmm", "Mm",
    "Well", "Okay", "Ok", "Right", "Sure", "Fine", "Good", "Great", "Thank", "Thanks",
    "Please", "Sorry", "Excuse", "Pardon", "Hello", "Hi", "Hey", "Goodbye", "Bye",
    "Look", "Listen", "Wait", "Stop", "Go", "Come", "Take", "Give", "Put", "Keep",
    "Let", "Make", "Do", "Don", "Doesn", "Didn", "Won", "Wouldn", "Couldn", "Shouldn",
    "Can", "Cannot", "Could", "Would", "Should", "May", "Might", "Must", "Shall", "Will",
    "Have", "Has", "Had", "Having", "Haven", "Hasn", "Hadn",
    "Be", "Am", "Is", "Are", "Was", "Were", "Been", "Being", "Isn", "Aren", "Wasn", "Weren",
    "Say", "Says", "Said", "Ask", "Asked", "Tell", "Told", "Think", "Thought",
    "Know", "Knew", "See", "Saw", "Want", "Wanted", "Need", "Needed", "Try", "Tried",
    "Use", "Used", "Find", "Found", "Get", "Got", "Leave", "Left", "Call", "Called",
    "Feel", "Felt", "Become", "Became", "Seem", "Seemed", "Turn", "Turned",
    "Start", "Started", "Begin", "Began", "Help", "Helped", "Show", "Showed",
    "Hear", "Heard", "Play", "Played", "Run", "Ran", "Move", "Moved", "Live", "Lived",
    "Believe", "Believed", "Hold", "Held", "Bring", "Brought", "Happen", "Happened",
    "Write", "Wrote", "Provide", "Sit", "Sat", "Stand", "Stood", "Lose", "Lost",
    "Pay", "Paid", "Meet", "Met", "Include", "Continue", "Set", "Learn", "Change",
    "Lead", "Understand", "Watch", "Follow", "Create", "Speak", "Spoke", "Read",
    "Allow", "Add", "Spend", "Spent", "Grow", "Grew", "Open", "Opened", "Walk", "Walked",
    "Win", "Offer", "Remember", "Love", "Consider", "Appear", "Buy", "Bought",
    "Serve", "Die", "Died", "Send", "Sent", "Expect", "Build", "Stay", "Stayed",
    "Fall", "Fell", "Cut", "Reach", "Kill", "Remain", "Suggest", "Raise", "Pass",
    "Sell", "Sold", "Require", "Report", "Decide", "Pull", "Return", "Explain",
    "Hope", "Develop", "Carry", "Break", "Broke", "Receive", "Agree", "Support",
    "Hit", "Produce", "Eat", "Cover", "Catch", "Draw", "Choose",
    # Structural / craft words in headings or ledgers
    "Chapter", "Part", "Book", "Act", "Scene", "Prologue", "Epilogue", "Interlude",
    "Section", "Volume", "Page", "Line", "Paragraph", "Note", "Notes", "Rule", "Fact",
    "Item", "Phase", "Gate", "Freeze", "Outline", "Premise", "Canon", "Entity",
    "State", "Name", "Role", "Age", "Status", "Draft", "Complete", "Planned",
    # Honorifics (handled separately when attached to names)
    "Mr", "Mrs", "Ms", "Miss", "Dr", "Prof", "Sir", "Madam", "Madame", "Lord", "Lady",
    "St", "Sgt", "Capt", "Col", "Gen", "Lt", "Rev", "Fr",
    # Common expletives / deity interjections in dialogue
    "God", "Lord", "Christ", "Jesus", "Hell", "Damn", "Shit", "Fuck",
    # Common German/multilingual function words for non-English books
    "Der", "Die", "Das", "Ein", "Eine", "Einen", "Einem", "Einer", "Eines",
    "Und", "Oder", "Aber", "Denn", "Sondern", "Doch", "Jedoch",
    "Ich", "Du", "Er", "Sie", "Es", "Wir", "Ihr", "Mich", "Mir", "Dich", "Dir",
    "Sich", "Uns", "Euch", "Ihm", "Ihn", "Ihnen", "Mein", "Meine", "Dein", "Deine",
    "Sein", "Seine", "Unser", "Unsere", "Kein", "Keine", "Keinen", "Keinem",
    "Nicht", "Nichts", "Noch", "Schon", "Nur", "Auch", "So", "Wie", "Wo", "Was",
    "Wer", "Wann", "Warum", "Wenn", "Weil", "Dass", "Ob", "Als", "Nach", "Vor",
    "Mit", "Ohne", "Auf", "In", "Im", "An", "Am", "Um", "Aus", "Bei", "Von", "Vom",
    "Zu", "Zum", "Zur", "Für", "Über", "Unter", "Zwischen", "Durch", "Gegen",
    "Hinter", "Neben", "Seit", "Bis", "Jetzt", "Dann", "Da", "Dort", "Hier",
    "Immer", "Nie", "Niemals", "Heute", "Gestern", "Morgen", "Ja", "Nein",
    "Kapitel", "Teil", "Herr", "Frau",
}

ROMAN_RE = re.compile(r"^[IVXLCDM]+$")

DECL_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:name|canonical_name|called_in_prose)\s*:\s*[\"']?([^\"'#\r\n]+?)[\"']?\s*(?:#.*)?$",
    re.IGNORECASE,
)

WAIVER_ENTRY_RE = re.compile(
    r"^##\s+(W-\d+)\s*[-\u2013\u2014]\s*(\d{4}-\d{2}-\d{2})\s*[-\u2013\u2014]\s*"
    r"chapter\s+([A-Za-z0-9_.-]+)\s*[-\u2013\u2014]\s*(\S+)\s*$",
    re.M | re.I,
)
WAIVER_REASON_RE = re.compile(r"^-\s+reason:\s+(.*\S)\s*$", re.M | re.I)


def strip_possessive(word):
    for suf in ("'s", "\u2019s", "s'", "s\u2019"):
        if word.endswith(suf):
            return word[:-len(suf)]
    return word


def load_lexicon(lex_path):
    """Parse `audiobook/lexicon.yaml`.

    Returns (entries_dict, meta_dict, error_message_or_None).
    entries_dict maps lowercase normalized key -> {
        "canonical": original_key,
        "ipa": ...,
        "respelling": ...,
        "note": ...,
    }
    Refuses empty or malformed entries (exit 3).
    """
    if not os.path.isfile(lex_path):
        return None, None, None

    try:
        with open(lex_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        return None, None, f"cannot read {lex_path}: {exc}"

    # Try PyYAML first if available, else strict stdlib parser
    data = None
    try:
        import yaml
        try:
            data = yaml.safe_load(raw)
        except Exception as exc:
            return None, None, f"YAML parse error in {lex_path}: {exc}"
    except ImportError:
        data, err = _parse_lexicon_stdlib(raw, lex_path)
        if err:
            return None, None, err

    if not isinstance(data, dict):
        return None, None, f"{lex_path}: top-level structure must be a mapping"

    meta = data.get("meta", {}) if isinstance(data.get("meta"), dict) else {}
    raw_entries = data.get("entries")
    if raw_entries is None:
        raw_entries = data.get("lexicon")
    if raw_entries is None:
        # Allow top-level keys other than 'meta' / 'schema' / 'version'
        reserved = {"meta", "schema", "version", "book", "language"}
        raw_entries = {k: v for k, v in data.items() if k not in reserved}

    if not isinstance(raw_entries, dict):
        return None, None, f"{lex_path}: 'entries' must be a mapping of proper_noun -> pronunciation"

    entries = {}
    for k, v in raw_entries.items():
        key = str(k).strip()
        if not key:
            return None, None, f"{lex_path}: empty proper-noun key in entries"
        if isinstance(v, str):
            val = v.strip()
            if not val:
                return None, None, f"{lex_path}: entry {key!r} has an empty pronunciation string"
            rec = {"canonical": key, "ipa": val, "respelling": val}
        elif isinstance(v, dict):
            ipa = str(v.get("ipa") or v.get("phonetic") or "").strip()
            resp = str(v.get("respelling") or v.get("pronunciation") or v.get("say_as") or "").strip()
            if not ipa and not resp:
                return None, None, (
                    f"{lex_path}: entry {key!r} must declare at least one non-empty "
                    f"'ipa' or 'respelling' field"
                )
            rec = {
                "canonical": key,
                "ipa": ipa or resp,
                "respelling": resp or ipa,
                "note": str(v.get("note", "")).strip(),
            }
        else:
            return None, None, f"{lex_path}: entry {key!r} has invalid value type {type(v).__name__}"

        entries[key.lower()] = rec
        # Also index individual tokens of a multi-word entry if not already present,
        # so declaring "Ines Varga" with ipa/respelling or individual tokens works cleanly
        parts = key.split()
        if len(parts) > 1:
            ipa_parts = rec["ipa"].split()
            resp_parts = rec["respelling"].split()
            for idx, part in enumerate(parts):
                p_low = part.lower()
                if p_low not in entries:
                    p_ipa = ipa_parts[idx] if len(ipa_parts) == len(parts) else rec["ipa"]
                    p_resp = resp_parts[idx] if len(resp_parts) == len(parts) else rec["respelling"]
                    entries[p_low] = {
                        "canonical": part,
                        "ipa": p_ipa,
                        "respelling": p_resp,
                        "from_full": key,
                    }

    return entries, meta, None


def _parse_lexicon_stdlib(raw, lex_path):
    """Fallback stdlib parser for audiobook/lexicon.yaml when PyYAML is absent."""
    data = {"meta": {}, "entries": {}}
    section = None
    current_entry = None
    for lineno, line in enumerate(raw.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            if ":" not in stripped:
                return None, f"{lex_path}:{lineno}: expected key: value"
            k, v = stripped.split(":", 1)
            k = k.strip().strip("\"'")
            v = v.strip()
            if v and not v.startswith("#"):
                data[k] = v.strip("\"'")
                section = None
            else:
                section = k
                if section not in data:
                    data[section] = {}
            current_entry = None
        elif section == "meta":
            if ":" not in stripped:
                return None, f"{lex_path}:{lineno}: invalid meta line"
            k, v = stripped.split(":", 1)
            data["meta"][k.strip().strip("\"'")] = v.strip().strip("\"'")
        elif section in ("entries", "lexicon"):
            if indent <= 2 and ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip().strip("\"'")
                v = v.strip()
                if v.startswith("#"):
                    v = ""
                if v:
                    if v.startswith("{") and v.endswith("}"):
                        inner = v[1:-1].strip()
                        sub = {}
                        if inner:
                            for pair in inner.split(","):
                                if ":" not in pair:
                                    return None, f"{lex_path}:{lineno}: malformed inline dict"
                                sk, sv = pair.split(":", 1)
                                sub[sk.strip().strip("\"'")] = sv.strip().strip("\"'")
                        data["entries"][k] = sub
                    else:
                        data["entries"][k] = v.strip("\"'")
                    current_entry = None
                else:
                    current_entry = k
                    data["entries"][current_entry] = {}
            elif current_entry is not None and ":" in stripped:
                sk, sv = stripped.split(":", 1)
                sv = sv.strip()
                if " #" in sv:
                    sv = sv.split(" #", 1)[0].strip()
                data["entries"][current_entry][sk.strip().strip("\"'")] = sv.strip("\"'")
            else:
                return None, f"{lex_path}:{lineno}: unexpected indentation or syntax"
    return data, None


def load_lexicon_waivers(book_root):
    """Read `maintenance/WAIVERS.md` for waived proper nouns.

    Accepts rules:
      - `lexicon:<ProperNoun>` (waives a specific proper noun in that chapter or `book`)
      - `lexicon` (if the reason names the proper noun, or waives the chapter's lexicon check)
    Returns (waived_global_set_lower, waived_by_chapter_dict_lower, waiver_records).
    """
    ledger = os.path.join(book_root, "maintenance", "WAIVERS.md")
    global_waived = set()
    chapter_waived = {}
    records = []
    if not os.path.isfile(ledger):
        return global_waived, chapter_waived, records

    try:
        with open(ledger, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return global_waived, chapter_waived, records

    marks = list(WAIVER_ENTRY_RE.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        wid, date, chapter, rule = m.group(1), m.group(2), m.group(3), m.group(4)
        body = text[m.end():end]
        rm = WAIVER_REASON_RE.search(body)
        if not rm:
            continue
        reason = rm.group(1).strip()
        rule_low = rule.lower()
        if not (rule_low == "lexicon" or rule_low.startswith("lexicon:")):
            continue
        target = rule.split(":", 1)[1].strip().lower() if ":" in rule else "*"
        records.append({
            "id": wid,
            "date": date,
            "chapter": chapter,
            "rule": rule,
            "target": target,
            "reason": reason,
        })
        if chapter.lower() in ("book", "*"):
            global_waived.add(target)
        elif chapter.isdigit():
            chapter_waived.setdefault(int(chapter), set()).add(target)
    return global_waived, chapter_waived, records


def harvest_declared_cast_and_entities(book_root):
    """Collect proper nouns explicitly declared in CANON_LEDGER.yaml, ENTITY_STATE.yaml,
    characters.md, cast.md, and voice-matrix.md."""
    declared = set()
    candidates = [
        "CANON_LEDGER.yaml", "CANON_LEDGER.yml", "ENTITY_STATE.yaml",
        "artifacts/03-characters.md", "characters.md", "cast.md", "voice-matrix.md",
    ]
    for rel in candidates:
        path = os.path.join(book_root, rel)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                lines = fh.read().splitlines()
        except OSError:
            continue
        for line in lines:
            low = line.lower()
            if any(h in low for h in ("reader", "persona", "segment", "benchmark", "comp")):
                continue
            m = DECL_RE.match(line)
            if m:
                val = m.group(1).strip()
                # Skip placeholder/generic strings that aren't proper names
                for tok in re.findall(r"\b[A-Z][a-zA-Z'’-]{1,}\b", val):
                    tok = strip_possessive(tok)
                    if tok and tok not in STOP_WORDS and not ROMAN_RE.match(tok):
                        declared.add(tok)
    return declared


def extract_proper_nouns_from_chapters(chapters, declared_cast):
    """Scan chapter texts for proper nouns.

    A token is treated as a proper noun in the manuscript if:
      1. It appears in `declared_cast` (and appears in the chapter text), OR
      2. It is a capitalised word `[A-Z][a-z'’-]{2,}` that:
         - is not in STOP_WORDS or ROMAN_RE,
         - never appears in all-lowercase anywhere in the manuscript (or appears
           mid-sentence after a non-sentence-ending token at least once and is not
           a common lowercase word in the manuscript).

    Returns list of findings:
      [{"token": tok, "chapter": ch_num, "chapter_file": fname, "line": lineno, "context": snippet}, ...]
    grouped by token.
    """
    whole = "\n".join(text for _, _, text in chapters)
    lowercase_vocab = set(re.findall(r"(?<![A-Za-z'’])[a-z][a-z'’-]{1,}\b", whole))

    # Words that appear mid-sentence capitalised (preceded by a lowercase word or comma/semicolon)
    mid_sentence_caps = set()
    for _ch_num, _fname, text in chapters:
        for m in re.finditer(r"(?<=[a-z,;:])\s+([A-Z][a-z'’-]{2,})\b", text):
            tok = strip_possessive(m.group(1))
            if tok and tok not in STOP_WORDS and not ROMAN_RE.match(tok):
                mid_sentence_caps.add(tok)

    occurrences = {}  # token -> list of (ch_num, fname, lineno, line_snippet)
    word_re = re.compile(r"\b([A-Z][a-z'’-]{2,})\b")

    for ch_num, fname, text in chapters:
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped:
                continue
            is_heading = stripped.startswith("#")
            for m in word_re.finditer(line):
                raw_tok = m.group(1)
                # Guard against apostrophe truncations like "Don't" -> "Don" or "I'll"
                after_idx = m.end(1)
                if after_idx < len(line) and line[after_idx] in ("'", "\u2019"):
                    suf = line[after_idx:after_idx + 3]
                    if not (suf.startswith("'s") or suf.startswith("\u2019s")):
                        continue
                tok = strip_possessive(raw_tok)
                if len(tok) < 2 or tok in STOP_WORDS or ROMAN_RE.match(tok):
                    continue
                is_declared = tok in declared_cast
                is_mid = tok in mid_sentence_caps
                is_never_lower = tok.lower() not in lowercase_vocab

                # A proper noun must either be in the declared cast/entity state,
                # or appear mid-sentence capitalised (not merely at sentence start
                # or in a title-cased chapter heading) while never appearing lowercase.
                if is_declared or (is_never_lower and is_mid and not is_heading):
                    occurrences.setdefault(tok, []).append((ch_num, fname, lineno))

    return occurrences


def resolve_chapters(book_root, chapter_filter=None):
    chdir = os.path.join(book_root, "manuscript", "chapters")
    if not os.path.isdir(chdir):
        return []
    out = []
    for name in sorted(os.listdir(chdir)):
        m = CHAPTER_RE.search(name)
        if not m:
            continue
        ch_num = int(m.group(1))
        if chapter_filter is not None:
            # chapter_filter may be an integer or a filename/path
            if str(chapter_filter).isdigit():
                if ch_num != int(chapter_filter):
                    continue
            else:
                if os.path.basename(str(chapter_filter)) != name:
                    continue
        path = os.path.join(chdir, name)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                out.append((ch_num, name, fh.read()))
        except OSError:
            continue
    return out


def audit_book_lexicon(book_root, chapter_filter=None):
    """Run the full lexicon audit on `book_root`.

    Returns (exit_code, report_dict).
    """
    book_root = os.path.abspath(book_root)
    lex_path = os.path.join(book_root, "audiobook", "lexicon.yaml")
    chapters = resolve_chapters(book_root, chapter_filter)

    if not chapters:
        return 2, {
            "status": "NOT RUN",
            "book": book_root,
            "reason": f"no chapter files found under {os.path.join(book_root, 'manuscript', 'chapters')}",
        }

    if not os.path.isfile(lex_path):
        return 2, {
            "status": "NOT RUN",
            "book": book_root,
            "lexicon_path": lex_path,
            "reason": (
                f"missing pronunciation lexicon at {lex_path} — not-run is never a pass. "
                f"Create audiobook/lexicon.yaml with IPA/respelling entries for every proper noun."
            ),
        }

    entries, meta, err = load_lexicon(lex_path)
    if err:
        return 3, {
            "status": "REFUSED",
            "book": book_root,
            "lexicon_path": lex_path,
            "reason": err,
        }

    declared_cast = harvest_declared_cast_and_entities(book_root)
    occurrences = extract_proper_nouns_from_chapters(chapters, declared_cast)
    global_waived, chapter_waived, waiver_records = load_lexicon_waivers(book_root)

    mapped = []
    waived = []
    unmapped = []

    for tok in sorted(occurrences):
        tok_low = tok.lower()
        locs = occurrences[tok]
        if tok_low in entries:
            mapped.append({
                "token": tok,
                "ipa": entries[tok_low]["ipa"],
                "respelling": entries[tok_low]["respelling"],
                "occurrences": len(locs),
            })
            continue

        # Check waivers
        if "*" in global_waived or tok_low in global_waived:
            waived.append({
                "token": tok,
                "scope": "book",
                "occurrences": len(locs),
            })
            continue

        # Check if every chapter where `tok` appears has a chapter-level waiver for it
        unwaived_locs = [
            loc for loc in locs
            if "*" not in chapter_waived.get(loc[0], set())
            and tok_low not in chapter_waived.get(loc[0], set())
        ]
        if not unwaived_locs:
            waived.append({
                "token": tok,
                "scope": "chapter",
                "occurrences": len(locs),
            })
            continue

        first_ch, first_fname, first_line = unwaived_locs[0]
        chapters_seen = sorted({loc[0] for loc in unwaived_locs})
        unmapped.append({
            "token": tok,
            "declared_cast": tok in declared_cast,
            "occurrences": len(unwaived_locs),
            "first_seen": f"{first_fname}:{first_line}",
            "chapters": chapters_seen,
        })

    status = "FAIL" if unmapped else "PASS"
    rc = 1 if unmapped else 0
    return rc, {
        "status": status,
        "book": book_root,
        "lexicon_path": lex_path,
        "chapters_scanned": len(chapters),
        "lexicon_entries_count": len(entries),
        "proper_nouns_found": len(occurrences),
        "mapped_count": len(mapped),
        "waived_count": len(waived),
        "unmapped_count": len(unmapped),
        "mapped": mapped,
        "waived": waived,
        "unmapped": unmapped,
    }


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", newline="\n")
    ap = argparse.ArgumentParser(description="Proper-noun pronunciation lexicon gate for audiobook stage.")
    ap.add_argument("book", help="Path to the book root directory")
    ap.add_argument("--chapter", default=None, help="Optional single chapter number or filename")
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    args = ap.parse_args(argv)

    rc, rep = audit_book_lexicon(args.book, args.chapter)
    if args.json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        return rc

    if rc in (2, 3):
        print(f"check-lexicon: {rep['status']} — {rep['reason']}", file=sys.stderr)
        return rc

    print("=" * 67)
    print(f"## check-lexicon   {rep['book']}   ({rep['chapters_scanned']} chapter(s))")
    print("=" * 67)
    print(f"   lexicon:       {rep['lexicon_path']} ({rep['lexicon_entries_count']} indexed forms)")
    print(f"   proper nouns:  {rep['proper_nouns_found']} found | "
          f"{rep['mapped_count']} mapped | {rep['waived_count']} waived | "
          f"{rep['unmapped_count']} unmapped")

    if rep["waived"]:
        print("\n   waived proper nouns (in maintenance/WAIVERS.md):")
        for w in rep["waived"]:
            print(f"     - {w['token']:<20} ({w['occurrences']} occurrence(s), scope: {w['scope']})")

    if rep["unmapped"]:
        print("\n   UNMAPPED PROPER NOUNS (FAIL):")
        for u in rep["unmapped"]:
            cast_tag = " [CAST]" if u["declared_cast"] else ""
            ch_list = ", ".join(f"ch-{c:02d}" for c in u["chapters"][:6])
            if len(u["chapters"]) > 6:
                ch_list += f", ... (+{len(u['chapters']) - 6} more)"
            print(f"     - {u['token']:<20}{cast_tag:<8} first at {u['first_seen']:<18} "
                  f"({u['occurrences']}x in {ch_list})")
        print()
        print(f"LEXICON FAIL — {rep['unmapped_count']} proper noun(s) have no pronunciation "
              f"in audiobook/lexicon.yaml and no waiver in maintenance/WAIVERS.md.")
        print("Add each term to audiobook/lexicon.yaml (with ipa and/or respelling) or "
              "waive it explicitly via:")
        print(f"  bash tools/run-phases.sh {args.book} --waive lexicon:<Term> --chapter book "
              f"--reason \"<why>\"")
        return 1

    print()
    print("LEXICON OK — every proper noun in the scanned manuscript is mapped or waived.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
