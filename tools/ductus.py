#!/usr/bin/env python3
"""ductus.py — the author voices the press publishes, and the agent that pilots one.

WHAT A DUCTUS IS
  A *ductus* is the individual character of a hand's writing — the word means
  exactly that, and it is the thing this layer holds. One ductus is one authorial
  voice: who they are, how they sound, what they refuse, how the voice breaks under
  pressure, and the benchmark lines the voice can be blind-sorted against. The agent
  PILOTS a ductus: at drafting time it reads `ductus/<slug>/ductus.md` and writes as
  that voice. The identity is the author's to invent, and an invented one is a
  persona, not a deception — the record says which it is, because a record that
  cannot say what a thing is stops being worth reading.

  A ductus DEVELOPS. Alongside the contract sits `ductus/<slug>/COMMONPLACE.md`, that
  voice's own taste ledger, with the root ledger's ceremony: decisions recorded as
  they are made, a preference written only after three agreeing decisions (and
  written `emergent`, never enforced), outcomes recorded when readers land, and
  promotions through the verifier stack. `list` is the surface for watching that
  happen — decisions, preferences, outcomes, last activity per voice.

THE HIERARCHY
  Three layers, and a book resolves through all of them:

    ductus/<voice>/ductus.md                the author's hand
    ductus/<voice>/series/<series>.md       the series the book belongs to
    <book>/ductus.md                        the hand on this material

  `series:` in BOOKS.yaml names the middle layer, and a book resolves book -> series ->
  voice, reporting which of them it used. Each layer may TIGHTEN the one above it and may
  never loosen it. The middle layer exists because a multi-volume project otherwise loses
  it: a persona is a hand and a book is one volume of it, so the throttle volume one spent
  a hundred thousand words learning has nowhere to be written down for volume two, and the
  next volume starts again from a persona that never selected it. A declared series with no
  contract is REFUSED, the way a declared voice with no contract already is.

WHY THE LEDGERS ARE ISOLATED
  Taste does not transfer between voices. A rule earned by one ductus is not evidence
  for another, and the root `COMMONPLACE.md` is not a substitute for either. Evidence
  from one may not move another, the same way evidence from one channel may not move
  another (SELF_IMPROVEMENT.md §2). Nothing crosses except a dated merge in
  `ductus/PROMOTIONS.md`.

  So `check` refuses a ledger outside its own directory, a ledger shared by two
  ductus, and a ductus pointing at the root ledger — a voice that reads the shared
  file has no voice. `cross` reports an entry that appears in two ledgers, because a
  preference in both has stopped being either one's.

WHAT IT WILL NOT DO
  - It does not invent a ductus by default. `new` writes a skeleton; `new --random`
    writes a seeded persona from the palette, marked as generated, and an empty
    contract is reported as empty rather than filled with house defaults.
  - It will not accept a missing ledger as an empty one, and it will not quietly
    assign a book to a voice: `ductus:` in BOOKS.yaml is the author's assignment, and
    `check` NAMES the unassigned books.
  - `check` is not a prose gate; `audit` is the per-book carryover check. Neither
    moves a threshold — a measurement moves on a named corpus, never on taste.
  - `calibrate` reads the lines a contract DECLARES and measures the book against
    them. It never adjusts a line to fit a book: when the book leaves a declared line,
    the report says so and exits 1, and the fix is prose or a dated contract change.

usage:  tools/ductus.py <command> [--root DIR]
  new SLUG [--name "…"] [--register "…"] [--random]
                                           create a voice (skeleton), or a seeded
                                           contract from the random palette
  log BOOK --chapter N --tone "…" --register "…" --survives "…"
                                           record how the voice must carry into a
                                           chapter; one section per chapter
  audit BOOK                               check the book's ductus log is complete,
                                           every chapter entry matches the live
                                           contract digest, and every quoted survival
                                           claim is present in its chapter
  calibrate BOOK                           measure the book against the numeric lines
                                           its contract declares, and fail where the
                                           book leaves them
  check                                    every voice, its isolation, the unassigned books
  contract BOOK [--ductus SLUG]            WHAT A RUN DRAFTS UNDER: the resolved contract
                                           for a book — its own, else its series', else its
                                           voice's — with digests, or UNASSIGNED. A book
                                           assigned to a voice whose contract is a
                                           skeleton is REFUSED, and so is a declared
                                           series with no voice: a phase may not draft
                                           under layers nobody authored.
  cross                                    report an entry held by two ledgers, and two
                                           contracts that are the same voice
  list                                     each voice and how far it has developed
  --self-test

EXIT
  0  clean
  1  a rule failed (each failure names it)
  2  usage error, or no press declared
  3  no YAML parser here — nothing was checked (and not passed)
"""

import contextlib
import glob
import io
import itertools
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

CONFIG = "ductus.yaml"
BOOKS = "BOOKS.yaml"
DEFAULT_DIR = "ductus"
PROMOTIONS = "PROMOTIONS.md"
CONTRACT = "ductus.md"
LEDGER = "COMMONPLACE.md"
ROOT_LEDGER = "COMMONPLACE.md"
BOOK_LOG = "maintenance/DUCTUS_LOG.md"
SERIES_DIR = "series"   # <ductus dir>/<voice>/series/<series>.md — the middle layer
CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)", re.I)

# The ledger entry types, same ceremony as the root COMMONPLACE.md. `list` counts them
# to show development; none of them is enforced by anything.
ENTRY_KINDS = ("decision", "preference", "outcome", "promotion")
ENTRY_HEADING = re.compile(r"^#{2,3}\s+(?:\d{4}-\d{2}-\d{2}\s+[—-]\s+)?(\w+)", re.M)

CONTRACT_SECTIONS = ("identity", "register", "refusals", "breaking", "benchmarks")

# The survival line is the one part of a log entry that can be checked against the
# chapter rather than against the log. Two forms, and only one of them is enforced:
#   - a QUOTED span is a claim of literal presence, and audit fails without it.
#   - the rest of the line is prose written for the next session's eye ("the
#     instruction that sounds like protection"). Matching it literally would fail
#     entries whose chapters are correct, so it is reported, never enforced.
SURVIVES = re.compile(r"\*\*What must survive:\*\*\s*(.+)", re.M)
QUOTED_CLAIM = re.compile(r"[`\"\u201c]([^`\"\u201c\u201d\n]{3,})[`\"\u201d]")
SURVIVES_STOP = set("""the a an and or of to in on at for with from by as is was were be been
being his her its their them that this those not no did do does had has have but if then than so up down
out into over under about after before when while there here what which who all any both each few more
most other some such only own same too very can will just said says one once""".split())


def utf8_stdout():
    """Emit UTF-8 whatever the locale says.

    On Windows the default stdout encoding is a code page, and every em dash in this
    tool's output then goes out as the single byte 0x97 — which a UTF-8 terminal renders
    as junk and `grep` calls a binary file. The rest of the harness is fixed by
    `PYTHONUTF8=1` (README, Dependencies); a tool written today does not add to the
    problem it is documenting.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def write_text(path, text):
    """LF always: a CR is the byte grep cannot see (KF-005)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def load_yaml(path):
    """(data, error). A missing parser is its own state, never a pass."""
    try:
        import yaml
    except ImportError:
        return None, "no-yaml"
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh), None
    except Exception as e:
        return None, str(e)


def press_config(root):
    """(press dict, ductus dir, error)."""
    data, err = load_yaml(os.path.join(root, CONFIG))
    if err:
        return {}, None, err
    press = (data or {}).get("press") or {}
    return press, press.get("ductus_dir") or DEFAULT_DIR, None


def ductus_dirs(root, ddir):
    base = os.path.join(root, ddir)
    if not os.path.isdir(base):
        return []
    return sorted(d for d in os.listdir(base)
                  if os.path.isdir(os.path.join(base, d)))


def entries(path):
    if not os.path.isfile(path):
        return []
    text = read_text(path)
    return [m.group(1).lower() for m in ENTRY_HEADING.finditer(text)]


DATED_ENTRY = re.compile(r"^#{2,3}\s+(\d{4}-\d{2}-\d{2}\s+[—\u2014-]\s+.*\S)\s*$", re.M)
PLACEHOLDER = re.compile(r"^_\(.*\)_\.?\s*$", re.M)


def latest_date(path):
    """The newest dated entry in a ledger, for `list`'s last-activity column."""
    if not os.path.isfile(path):
        return "-"
    dates = re.findall(r"^#{2,3}\s+(\d{4}-\d{2}-\d{2})", read_text(path), re.M)
    return max(dates) if dates else "-"


def held_headings(path):
    """The DATED entry headings, for the cross-voice leak check.

    Dated ones only: every ledger documents itself, and two voices that both have a
    "## Entry types" section have not leaked anything. What must not appear twice is a
    recorded entry — a decision, a preference, an outcome — because that has stopped
    being one voice's.
    """
    if not os.path.isfile(path):
        return []
    return [m.group(1).strip() for m in DATED_ENTRY.finditer(read_text(path))]


def _words(text):
    return re.findall(r"[a-z0-9']+", text.lower().replace("\u2019", "'"))


def _flat(text):
    """Words only, single-spaced — a quote is matched as words, not as characters,
    so punctuation and smart apostrophes cannot make a present phrase look absent."""
    return " ".join(_words(text))


def survival_claims(body):
    """(quoted, items) — an entry's survival line, split into checkable claims."""
    m = SURVIVES.search(body)
    if not m:
        return [], []
    line = m.group(1).strip()
    quoted = [q.strip() for q in QUOTED_CLAIM.findall(line) if q.strip()]
    plain = QUOTED_CLAIM.sub(" ", line)
    items = []
    for chunk in re.split(r"[,;]", plain):
        chunk = re.sub(r"^\s*(?:and|but)\s+", "", chunk.strip(), flags=re.I)
        if _words(chunk):
            items.append(chunk)
    return quoted, items


DUP_MIN_GRAMS = 20
# CALIBRATED 2026-11-11 on this press's four contracts: the worst honest pair shares 7.4%
# of any section (study-voice-a <-> study-voice-b, identity). Palette 1 shares 68% of
# kalie-kirch's Register and palette 2 shares 64% of bastorius-quinn's, which is what the
# line is for: 40% sits far above the observed honest maximum and below a paste.
DUP_SHARE = 0.40


def section_grams(text):
    words = _words(text)
    return {" ".join(words[i:i + 6]) for i in range(len(words) - 5)}


def contract_sections(text):
    """{section: six-gram set} for a contract's five sections."""
    out = {}
    for m in re.finditer(r"^##\s+(\w+)\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S):
        name = m.group(1).lower()
        if name in CONTRACT_SECTIONS:
            out[name] = section_grams(m.group(2))
    return out


def duplicate_share(sections_a, sections_b):
    """(share, section) of the most-overlapping section; (0.0, None) if none is big
    enough to judge. Containment against the smaller side, not Jaccard: a contract that
    pastes another voice's Register and adds to it is that voice wearing more words."""
    best = (0.0, None)
    for name in CONTRACT_SECTIONS:
        a, b = sections_a.get(name, set()), sections_b.get(name, set())
        small = min(len(a), len(b))
        if small < DUP_MIN_GRAMS:
            continue
        share = len(a & b) / small
        if share > best[0]:
            best = (share, name)
    return best


def palette_registers():
    return [section_grams(p["register"]) for p in RANDOM_PALETTES]


PROSE_INVARIANTS = {
    "negation": "negation",
    "subject_openings": "subject openings",
    "texture": "texture words",
}


def contract_invariants(text):
    """(dict, source) — the numeric lines a contract declares.

    Fenced `ductus-invariants` block first; otherwise the prose form this press's
    contracts actually use ("no higher than **38** per 10,000"). The source string is
    printed, because a number read out of prose is a number the reader must be able to
    audit: an instrument that quietly guesses which integer it is enforcing is worse
    than one that reports it.
    """
    m = re.search(r"```ductus-invariants\s*\n(.*?)```", text, re.S)
    if m:
        inv = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                try:
                    inv[key] = int(value.strip())
                except ValueError:
                    pass
        if inv:
            return inv, "the contract's ductus-invariants block"
    inv = {}
    for key, phrase in PROSE_INVARIANTS.items():
        for line in text.splitlines():
            low = line.lower()
            if phrase not in low:
                continue
            # The comparator is required, not the first integer on the line. This book's
            # contract carries "The negation row ... A pass on 2026-11-11 rewrote 268 of
            # the 557 ..." above the invariant bullet, and reading the first integer
            # made the declared limit 2026 -- a number that silently enforces nothing.
            m = re.search(r"no (?:higher|more) than\s*\*{0,2}(\d+)", low)
            if not m:
                continue
            inv[key] = int(m.group(1))
            break
    source = ("the prose invariants (no ductus-invariants block)" if inv else "")
    return inv, source


def compare_invariants(inv, measured):
    """[(key, declared_limit, value, within)] — the judgement, with no printing in it."""
    rows = []
    for key in ("negation", "subject_openings", "texture"):
        if key in inv and key in measured:
            rows.append((key, inv[key], measured[key], measured[key] <= inv[key]))
    return rows


def _stem(word):
    """Enough of a stem that opens/opened and handle/handles are one word.

    Measured on this project's own log: without it, "the door opens six centimeters"
    was reported absent from a chapter that says "opened", which makes the advisory a
    report about inflection rather than about content.
    """
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[:-len(suffix)]
    return word


def survival_check(chapter_text, body):
    """(quoted, missing_quoted, items, missing_items) for one chapter."""
    quoted, items = survival_claims(body)
    flat = _flat(chapter_text)
    present = {_stem(w) for w in _words(chapter_text)}
    missing_quoted = [q for q in quoted if _flat(q) and _flat(q) not in flat]
    missing_items = []
    for item in items:
        content = [(w, _stem(w)) for w in _words(item) if w not in SURVIVES_STOP]
        gone = [w for w, stem in content if stem not in present]
        if gone:
            missing_items.append((item, gone))
    return quoted, missing_quoted, items, missing_items


def book_assignments(root):
    data, err = load_yaml(os.path.join(root, BOOKS))
    if err or not isinstance(data, dict):
        return None
    out = []
    for b in data.get("books") or []:
        if isinstance(b, dict):
            out.append((b.get("path"), b.get("ductus")))
    return out


def series_of(root, rel):
    """(series slug, how) for a registry path; (None, why) when it declares none.

    Read from BOOKS.yaml, the same file that assigns the voice, because the series is part
    of the assignment rather than a fact about a directory. Exact path first, then a unique
    basename, exactly as `resolve_book` does it: a series read off a guessed path is a
    layer nobody declared.
    """
    data, err = load_yaml(os.path.join(root, BOOKS))
    if err or not isinstance(data, dict):
        return None, "books"
    rows = [b for b in (data.get("books") or []) if isinstance(b, dict)]

    def norm(p):
        return str(p).replace("\\", "/").rstrip("/")

    def slug_of(row):
        return str(row.get("series") or "").strip() or None

    want = norm(rel)
    for row in rows:
        if row.get("path") and norm(row["path"]) == want:
            return slug_of(row), "exact"
    base = os.path.basename(want)
    hits = [row for row in rows
            if row.get("path") and os.path.basename(norm(row["path"])) == base]
    if len(hits) == 1:
        return slug_of(hits[0]), "basename"
    return None, "ambiguous" if hits else "none"


NEW_CONTRACT = """# {name}

*A ductus* — the individual character of a writing hand. An agent pilots this voice:
at drafting time it reads this file as the voice contract, the way it reads a book's
`voice-matrix.md` for the cast.

**Status: skeleton.** `tools/ductus.py new` wrote the shape and the placeholders.
Replace each `_(…)_` line with the real thing — `ductus.py check` reports a
placeholder still standing, and will not fill one in for you.

- **Identity** — who the voice is: the name it publishes under, and the invented life
  it writes from, if it has one. A persona's backstory is authored fiction; the
  record's job is to be clear about which kind of author this is, not to check it.
- **Register** — how it sounds: sentence length, diction, what it reaches for, what it
  never does — plus the anti-patterns it may use and the ones it may not.
- **Refusals** — the moves it declines even when they would work. A voice with no
  refusals is a house style.
- **Breaking** — what happens to the sentences under pressure: what it stops doing,
  what it does badly. A hard chapter is drafted against this section.
- **Benchmarks** — three to five lines in this voice, long enough to blind-sort
  against another ductus, which is what the `register` phase is scored with.

## Identity
_(to be authored — who this voice is, and the name it publishes under)_

## Register
_(to be authored — how it sounds)_

## Refusals
_(to be authored — what it will not do)_

## Breaking
_(to be authored — how it changes under pressure)_

## Benchmarks
_(to be authored — three to five lines in this voice)_
"""

NEW_LEDGER = """# COMMONPLACE — {name}

This voice's own taste ledger, and only this voice's. Nothing outside this directory is
evidence for a {name} decision, and nothing here is enforced against a book.

The entry types and the ceremony are the root `COMMONPLACE.md`'s — `decision`,
`preference`, `outcome`, `promotion` — with the same formats and the same limits:

- **`decision`** — one real editorial choice, made between named alternatives.
- **`preference`** — distilled taste, written only after three agreeing decisions, and
  written `emergent`: guidance the next book may decline with a reason. A `limit:` line
  is required, because a preference without one is a rule.
- **`outcome`** — what readers did, with the prediction recorded before publication.
- **`promotion`** — a change the verifier stack adopted, with its falsifier.

**A preference that turns out to hold for another voice is not copied across.** It is
merged deliberately, dated, in `ductus/PROMOTIONS.md`, naming the evidence that
justified it in the second voice. A preference that appears in two ledgers by accident
has stopped being either one's, and `python tools/ductus.py cross` reports it.

**No decisions recorded yet.** An empty ledger is the honest state of a new voice —
seeding it with invented taste would make taste a default.
"""

# `ductus/README.md` and `ductus/PROMOTIONS.md` are written files on disk rather than
# templates held here: a second copy of the documentation inside this file is a second
# thing to keep true, and the docstring above already carries the part that matters.

RANDOM_NAMES = (
    "Bastorius Quinn", "Iris Vane", "Mara Venn", "Orrin Vale", "Sable Rook",
    "Tobias Mire", "Nell Harrow", "Casper Wren", "Ada Fallow", "Rook Calder",
)

# A seeded ductus is a persona, not a claim about a real person. The palette gives the
# fresh-book path a real voice to draft under.
#
# PROVENANCE, MEASURED 2026-11-11. Two of the four palettes below are not independent
# inventions: palette 1's Register shares 30 of 44 six-word runs (68%) with the authored
# `kalie-kirch` contract, and palette 2's shares 64% with `bastorius-quinn`. The comment
# here used to claim the palettes were "deliberately broad enough that two random books do
# not share a register"; that is false for half of them, so a seeded contract now names
# its palette's source and `cross` reports the overlap instead of documentation asserting
# it away.
RANDOM_PALETTES = (
    {
        "register": (
            "Concrete, close, and bodily. The prose stays inside the character's "
            "senses: texture, temperature, pressure, smell, the small physical facts "
            "that reveal what the character cannot say. Sentences mix short physical "
            "declarations with longer accumulations of detail. The environment is "
            "never scenery; it is the character's inner state made visible."
        ),
        "refusals": (
            "- No gore as decoration: violence must cost something on the page.\n"
            "- No clean catharsis.\n"
            "- No explaining a wound the scene has already shown.\n"
            "- No abstract emotion as the subject of a sentence."
        ),
        "breaking": (
            "Under pressure the sentences shorten and the body takes over: hands, "
            "mouth, the weight of a room. Metaphor drops away. The voice does not get "
            "louder; it gets more exact about what is physically happening."
        ),
        "benchmarks": (
            "The floor was wet where the freezer had been, and the smell stayed in "
            "the grout for three days.\n\n"
            "He put his hand flat on the wall and left it there until the plaster "
            "warmed under his palm.\n\n"
            "She counted the teeth in the sink twice; the second count was for the "
            "part of her that had already started lying."
        ),
    },
    {
        "register": (
            "Documentary and oblique. The voice assembles reports, notes, marginalia "
            "and fragments, and lets the reader feel the gaps between them. It is "
            "precise about provenance and careless about consolation. The sentence is "
            "usually flat, with one image allowed to open unexpectedly."
        ),
        "refusals": (
            "- No conventional closure.\n"
            "- No narrator who explains the architecture.\n"
            "- No twist that depends on withholding a fact the record already contains.\n"
            "- No decorative weirdness."
        ),
        "breaking": (
            "Under pressure the documents get shorter and the annotations more "
            "personal. The voice begins to address an absent reader, then stops "
            "addressing anyone. The last fragment is always the shortest."
        ),
        "benchmarks": (
            "The file is complete. That is the problem.\n\n"
            "I have the photocopy. I do not have the report.\n\n"
            "Nothing in this report was estimated; nobody measured the report."
        ),
    },
    {
        "register": (
            "Cold, procedural, and exact. The voice prefers the passive where it hides "
            "a decision, and the active where it assigns blame. Numbers recur. "
            "Emotion arrives as a deviation from procedure, never as a speech."
        ),
        "refusals": (
            "- No melodrama.\n"
            "- No metaphor where a measurement will do.\n"
            "- No villain explaining himself.\n"
            "- No sentence that asks the reader to feel something the record does not "
            "support."
        ),
        "breaking": (
            "Under pressure the voice becomes more formal, then repeats a single "
            "procedural phrase until it stops meaning anything. The break is in the "
            "repetition, not in a raised voice."
        ),
        "benchmarks": (
            "The request was refused. The refusal is not in the file.\n\n"
            "The column for the inspecting officer is blank.\n\n"
            "The second attendance was not authorised. The second attendance took "
            "place."
        ),
    },
    {
        "register": (
            "Lyrical, patient, and sensorily specific, with a long sentence that "
            "earns its length through observed detail. The voice trusts weather, "
            "light and distance to carry feeling. It is willing to be quiet for a "
            "whole page."
        ),
        "refusals": (
            "- No hurry.\n"
            "- No simile that only decorates.\n"
            "- No character announcing what the landscape means.\n"
            "- No ending that resolves the weather."
        ),
        "breaking": (
            "Under pressure the long sentence breaks into fragments of observation, "
            "then returns to one clean declarative. The voice holds the concrete "
            "noun longest and loses the adjective first."
        ),
        "benchmarks": (
            "By afternoon the light had moved off the wall and the room was a "
            "different room.\n\n"
            "The field was not empty; it was holding still.\n\n"
            "She waited until the rain had something to say, and then she went in."
        ),
    },
)


# Which palettes were taken from an existing authored contract, and from which one.
# `cross` measures the overlap; this map is the claim the measurement is checked against.
PALETTE_PROVENANCE = {1: "kalie-kirch", 2: "bastorius-quinn"}


def arg_value(args, flag, default=None):
    if flag not in args:
        return default
    i = args.index(flag)
    return args[i + 1] if i + 1 < len(args) else None


def seeded_contract(name, palette, index=1):
    """A complete contract from the palette, explicitly a generated persona."""
    source = PALETTE_PROVENANCE.get(index)
    provenance = (
        f"Palette {index} is derived from the authored `{source}` contract, so a voice "
        "seeded from it begins inside that voice; `cross` reports the measured overlap."
        if source else
        "A palette seed is a starting contract, not an independent invention."
    )
    return f"""# {name}

*A ductus* — the individual character of a writing hand. This one was seeded by the
random palette: it is a persona, not a claim about a real person. The seed is a starting
contract, not a verdict; edit it and record the decision in this voice's ledger.

**Status: seeded by random mode, 2026-11-07.** The agent that pilots this voice must read
it before drafting, revision, auditing or scoring.

**Provenance:** palette {index} of {len(RANDOM_PALETTES)}. {provenance}

## Identity

{name} is a seeded authorial persona. The name is a fiction and the contract says so.
What the voice has instead of a biography is a temperament: it notices the world through
the register below, and it refuses the moves listed under Refusals even when they would be
easy. It writes for a reader who is willing to be inside a body, a document or a room
rather than above it.

## Register

{palette['register']}

## Refusals

{palette['refusals']}

## Breaking

{palette['breaking']}

## Benchmarks

{palette['benchmarks']}
"""


def cmd_new(root, args):
    slug = next((a for a in args if not a.startswith("--")), None)
    if not slug:
        print("ductus: new needs a slug — `ductus.py new my-voice`.")
        return 2
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        print(f"ductus: {slug!r} is not a slug — lowercase, digits and hyphens.")
        return 2
    random_mode = "--random" in args
    name = arg_value(args, "--name")
    if not name:
        name = random.choice(RANDOM_NAMES) if random_mode else slug
    register = arg_value(args, "--register")
    _press, ddir, err = press_config(root)
    if err == "no-yaml":
        print(f"ductus: no YAML parser here — {CONFIG} was not read (and not passed).")
        return 3
    d = os.path.join(root, ddir, slug)
    if os.path.exists(d):
        print(f"ductus: {ddir}/{slug} already exists — nothing created, nothing changed.")
        return 1
    if random_mode:
        seeded = random.randrange(len(RANDOM_PALETTES))
        contract = seeded_contract(name, RANDOM_PALETTES[seeded], seeded + 1)
    else:
        contract = NEW_CONTRACT.format(name=name)
    if register:
        # Recorded verbatim as an ADDITIONAL section: the template's Register section
        # stays a placeholder, because a declared one-line register is the creator's
        # first taste and not a substitute for the section.
        contract += f"\n## Register (as declared by the creator)\n{register}\n"
    write_text(os.path.join(d, CONTRACT), contract)
    write_text(os.path.join(d, LEDGER), NEW_LEDGER.format(name=name))
    if random_mode:
        print(f"ductus: created {ddir}/{slug}/ — {CONTRACT} (seeded) and {LEDGER} (empty).")
        print("  This is a generated persona. Edit the contract if the seed is wrong; "
              "record that decision in its ledger.")
    else:
        print(f"ductus: created {ddir}/{slug}/ — {CONTRACT} (skeleton) and {LEDGER} (empty).")
        print("  Author the contract, then draft: an agent pilots this voice by reading it.")
    if register:
        print(f"  declared register recorded verbatim in {CONTRACT}: {register}")
    print("  `python tools/ductus.py check` reports a section still empty; it will not "
          "fill one in.")
    return 0


def thin_sections(contract_text):
    """Contract sections with no authored body.

    `new` writes the shape and a one-line placeholder for each section; `check` reports
    a placeholder still standing rather than filling it in. A section is authored when
    anything other than its placeholder line survives.
    """
    thin = []
    for s in CONTRACT_SECTIONS:
        m = re.search(rf"^##\s+{s}\s*$(.*?)(?=^##\s|\Z)", contract_text,
                      re.M | re.S | re.I)
        body = PLACEHOLDER.sub("", m.group(1)) if m else ""
        if not body.strip():
            thin.append(s)
    return thin


def cmd_check(root, args):
    press, ddir, err = press_config(root)
    if err == "no-yaml":
        print("ductus: no YAML parser here — nothing was checked (and not passed).")
        return 3
    if err:
        print(f"ductus: {CONFIG} does not parse — {err}")
        return 1
    if not press.get("name"):
        print(f"ductus: {CONFIG} declares no press.name — a press with no name has "
              "no imprint.")
        return 1

    slugs = ductus_dirs(root, ddir)
    fails, reviews, stats = [], [], {}
    ledgers = {}
    for slug in slugs:
        d = os.path.join(root, ddir, slug)
        contract = os.path.join(d, CONTRACT)
        ledger = os.path.join(d, LEDGER)
        if not os.path.isfile(contract):
            fails.append(f"{slug}: no {CONTRACT} — a directory is not a voice")
        if not os.path.isfile(ledger):
            fails.append(f"{slug}: no {LEDGER} — a missing ledger is a failure, not an "
                         "empty one")
        else:
            rel = f"{ddir}/{slug}/{LEDGER}"
            ledgers[rel] = slug
            kinds = entries(ledger)
            stats[slug] = {k: kinds.count(k) for k in ENTRY_KINDS}
            if not kinds:
                reviews.append(f"{slug}: the ledger is empty — a new voice, and an "
                               "honest state")
        if os.path.isfile(contract):
            thin = thin_sections(read_text(contract))
            if thin:
                reviews.append(f"{slug}: {CONTRACT} section(s) still empty or near-empty: "
                               f"{', '.join(thin)} — the voice is not authored yet")
    root_ledger_used = [s for s, d in ledgers.items() if d == ROOT_LEDGER]
    if root_ledger_used:
        fails.append(f"{ROOT_LEDGER} is being used as a ductus ledger — the press-wide "
                     "ledger is not a voice")

    assignments = book_assignments(root)
    if assignments is not None:
        known = set(slugs)
        for path, slug in assignments:
            if slug and slug not in known:
                fails.append(f"{path}: BOOKS.yaml assigns ductus {slug!r}, which does "
                             "not exist")
        unassigned = [p for p, s in assignments if not s]
        if unassigned:
            reviews.append(f"{len(unassigned)} book(s) carry no `ductus:` — the "
                           "assignment is the author's: " + ", ".join(unassigned[:6])
                           + (" …" if len(unassigned) > 6 else ""))

    print(f"ductus — {press.get('name')}, {len(slugs)} voice(s) in {ddir}/")
    for slug in slugs:
        s = stats.get(slug, {})
        last = latest_date(os.path.join(root, ddir, slug, LEDGER))
        print(f"  {slug:18} {s.get('decision', 0)} decision(s) · "
              f"{s.get('preference', 0)} preference(s) · "
              f"{s.get('outcome', 0)} outcome(s) · last {last}")
    for r in reviews:
        print(f"  REVIEW  {r}")
    for f in fails:
        print(f"  FAIL    {f}")
    if fails:
        print(f"ductus: {len(fails)} failure(s). Isolation is structural — fix it here, "
              "not in a book.")
        return 1
    print("ductus: every voice has its own contract and its own ledger.")
    return 0


def digest(path):
    """First 12 hex of the file's sha256 — what a run records as the contract in force."""
    import hashlib
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:12]


def resolve_book(assignments, book):
    """(registry path, slug, how). Exact path first, then a unique basename."""
    def norm(p):
        return str(p).replace("\\", "/").rstrip("/")

    want = norm(book)
    for path, slug in assignments:
        if path and norm(path) == want:
            return path, slug, "exact"
    base = os.path.basename(want)
    hits = [(p, s) for p, s in assignments
            if p and os.path.basename(norm(p)) == base]
    if len(hits) == 1:
        return hits[0][0], hits[0][1], "basename"
    if len(hits) > 1:
        return None, None, "ambiguous"
    return None, None, None


def cmd_contract(root, args):
    """The interface the phases call: what voice is this book drafted under, and is it real."""
    press, ddir, err = press_config(root)
    if err == "no-yaml":
        print(f"ductus: no YAML parser here — {CONFIG} was not read (and not passed).")
        return 3
    if err:
        print(f"ductus: {CONFIG} does not parse — {err}")
        return 1
    args = [a for a in args]
    override = None
    if "--ductus" in args:
        i = args.index("--ductus")
        override = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
        if not override:
            print("ductus: --ductus needs a slug.")
            return 2
    book = next((a for a in args if not a.startswith("--")), None)
    if not book:
        print("ductus: contract needs a book — `contract test-books/some-book`.")
        return 2

    assignments = book_assignments(root)
    if assignments is None:
        print("ductus: BOOKS.yaml is missing or does not parse — the assignment cannot "
              "be resolved, so nothing can be said about what this run drafts under.")
        return 1
    rel, slug, how = resolve_book(assignments, book)
    if how == "ambiguous":
        print(f"ductus: {book!r} matches more than one registry entry — pass the full "
              "path written in BOOKS.yaml.")
        return 1
    if rel is None:
        print(f"ductus: UNREGISTERED — {book!r} is not in BOOKS.yaml, so it cannot carry "
              "an assignment. A book outside the registry is outside the layer "
              "(tools/check-registry.py owns that failure).")
        return 1

    if override and override != slug:
        print(f"ductus: NOTE the registry assigns {rel} to "
              f"{slug or 'no voice'} — this run overrides it with {override!r}.")
        slug = override

    if not slug:
        print(f"ductus: UNASSIGNED — {rel} carries no `ductus:` in BOOKS.yaml. It is "
              f"drafted under the root {ROOT_LEDGER} alone, which is where the whole "
              "catalogue was drafted. This line is the record: nobody may read the run "
              "as having drafted under a voice.")
        return 0

    d = os.path.join(root, ddir, slug)
    parent = os.path.join(d, CONTRACT)
    ledger = os.path.join(d, LEDGER)
    if not os.path.isfile(parent):
        print(f"ductus: REFUSED — {rel} is assigned to {slug!r}, and there is no "
              f"{ddir}/{slug}/{CONTRACT}. A phase does not draft under a voice that "
              "does not exist.")
        return 1
    if not os.path.isfile(ledger):
        print(f"ductus: REFUSED — {slug!r} has no {ddir}/{slug}/{LEDGER}. Its taste "
              "could not be recorded, which is the one thing the ledger is for.")
        return 1
    thin = thin_sections(read_text(parent))
    if thin:
        print(f"ductus: REFUSED — {ddir}/{slug}/{CONTRACT} is still a skeleton "
              f"({', '.join(thin)}). Author it, or remove the assignment from "
              "BOOKS.yaml so the book is drafted under the root ledger openly.")
        return 1
    child = _book_contract(root, rel, book)
    if child:
        untitled = thin_sections(read_text(child))
        if untitled:
            print(f"ductus: REFUSED — {_relpath(root, child)} is a skeleton "
                  f"({', '.join(untitled)}). A book-level voice under an authored parent "
                  "is still a voice nobody wrote: write it, or delete it so the book is "
                  "openly drafted under the parent alone.")
            return 1

    series_slug, _how = series_of(root, rel)
    series = _series_contract(root, ddir, slug, series_slug) if series_slug else None
    if series_slug and not series:
        print(f"ductus: REFUSED — {rel} declares `series: {series_slug}` in BOOKS.yaml, and "
              f"there is no {ddir}/{slug}/{SERIES_DIR}/{series_slug}.md. A declared series "
              "is a layer, not a label: author it, or take the key out so the volumes are "
              "openly drafted under the voice alone.")
        return 1
    if series:
        thin_series = thin_sections(read_text(series))
        if thin_series:
            print(f"ductus: REFUSED — {_relpath(root, series)} is a skeleton "
                  f"({', '.join(thin_series)}). Every volume after this one would inherit "
                  "an unauthored layer: author it, or take the series key out.")
            return 1

    if series and child:
        about = " — voice, series, and its own ductus"
    elif series:
        about = " and its series"
    elif child:
        about = " and its own ductus"
    else:
        about = ""
    print(f"ductus: {rel} is drafted under {slug}{about}")
    if child:
        print(f"  book voice:   {_relpath(root, child)}  sha256:{digest(child)}")
    if series:
        print(f"  series voice: {_relpath(root, series)}  sha256:{digest(series)}")
    if child or series:
        print(f"  parent:          {ddir}/{slug}/{CONTRACT}  sha256:{digest(parent)}")
    else:
        print(f"  voice:    {ddir}/{slug}/{CONTRACT}  sha256:{digest(parent)}")
    print(f"  ledger:   {ddir}/{slug}/{LEDGER}  "
          f"{os.path.getsize(ledger)} byte(s)  sha256:{digest(ledger)}")
    print("  read before: drafting, revision, auditing and scoring. Record these digests "
          "in the session ledger so a result is attributable to the voice it was "
          "drafted under. Not packaging: the query letter and cover copy are written in "
          "the imprint's register, not the book's.")
    return 0


def _book_dir(root, rel, given):
    """The book on disk. The registry path is workspace-relative, not repo-relative."""
    candidates = [given, os.path.join(root, rel),
                  os.path.join(root, "test-books", rel),
                  os.path.join(root, "books", rel)]
    for c in candidates:
        if c and os.path.isdir(c):
            return os.path.abspath(c)
    return None


def _relpath(root, path):
    """A path for printing, repo-relative and slash-separated whatever the platform."""
    return os.path.relpath(path, root).replace(os.sep, "/")


def _book_contract(root, rel, given):
    """The book's own ductus.md, when it has one.

    A persona contract is the author's hand; a book's contract is that hand on this
    material. The book's file wins when it exists — `ductus-designer` writes one beside
    foundation.md — and the persona stays the parent. Without this preference a
    book-level contract was dead paper: `contract`, `calibrate`, `log` and `audit` all
    read the persona and never the file the book was designed under, so a book could be
    re-registered toward a new register and nothing that measures it would notice.
    """
    bd = _book_dir(root, rel, given)
    if not bd:
        return None
    path = os.path.join(bd, CONTRACT)
    return path if os.path.isfile(path) else None


def _series_contract(root, ddir, slug, series):
    """The middle layer: <ductus dir>/<voice>/<series dir>/<series>.md.

    A persona is the hand and a book is one volume of it, so without this layer a series
    loses its middle: volume one's pace band is written in volume one's own file and volume
    two starts again from the persona. `ductus-designer`'s open question 4 has said since the
    skill was written that each volume is written "under a series parent"; until BOOKS.yaml
    could name the series there was no file behind that sentence.
    """
    path = os.path.join(root, ddir, slug, SERIES_DIR, series + ".md")
    return path if os.path.isfile(path) else None


def _resolved_contract(root, book):
    """(rel, slug, contract, error) for the audit/log paths: book, else series, else voice."""
    _press, ddir, err = press_config(root)
    if err:
        return None, None, None, err
    assignments = book_assignments(root)
    if assignments is None:
        return None, None, None, "books"
    rel, slug, how = resolve_book(assignments, book)
    if how == "ambiguous":
        return None, None, None, "ambiguous"
    if rel is None:
        return None, None, None, "unregistered"
    if not slug:
        return rel, None, None, "unassigned"
    parent = os.path.join(root, ddir, slug, CONTRACT)
    if not os.path.isfile(parent):
        return rel, slug, None, "missing"
    if thin_sections(read_text(parent)):
        return rel, slug, parent, "skeleton"
    series_slug, _how = series_of(root, rel)
    series = None
    if series_slug:
        series = _series_contract(root, ddir, slug, series_slug)
        if not series:
            return rel, slug, None, "missing-series"
        if thin_sections(read_text(series)):
            return rel, slug, series, "skeleton"
    child = _book_contract(root, rel, book)
    if child:
        if thin_sections(read_text(child)):
            return rel, slug, child, "skeleton"
        return rel, slug, child, None
    if series:
        return rel, slug, series, None
    return rel, slug, parent, None


def _chapter_file(book_dir, number):
    for path in glob.glob(os.path.join(book_dir, "manuscript", "chapters", "chapter-*.md")):
        m = CHAPTER.search(os.path.basename(path))
        if m and int(m.group(1)) == number:
            return path
    return None


def _chapter_title(path):
    if not path:
        return "Untitled"
    for line in read_text(path).splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            return re.sub(r"^Chapter\s+\d+\s*[—–-]\s*", "", title, flags=re.I)
    return "Untitled"


def cmd_log(root, args):
    """Record one chapter's carryover entry in the book's ductus log."""
    book = args[0] if args and not args[0].startswith("--") else None
    if not book:
        print("ductus: log needs a book — `ductus.py log test-books/some-book ...`.")
        return 2
    try:
        number = int(arg_value(args, "--chapter", ""))
    except (TypeError, ValueError):
        print("ductus: log needs --chapter N.")
        return 2
    tone = arg_value(args, "--tone")
    register = arg_value(args, "--register")
    survives = arg_value(args, "--survives")
    if not tone or not register or not survives:
        print("ductus: log needs --tone, --register and --survives (each a real sentence).")
        return 2

    rel, slug, contract, err = _resolved_contract(root, book)
    if err == "unassigned":
        print(f"ductus: {rel} is UNASSIGNED — there is no voice to log.")
        return 1
    if err:
        print(f"ductus: cannot log — {err} for {book!r}.")
        return 1
    bookdir = _book_dir(root, rel, book)
    if not bookdir:
        print(f"ductus: no book directory for {rel!r}.")
        return 1
    chapter = _chapter_file(bookdir, number)
    title = _chapter_title(chapter)
    current = digest(contract)
    logpath = os.path.join(bookdir, BOOK_LOG)
    rel_contract = os.path.relpath(contract, root).replace(os.sep, "/")
    entry = (
        f"## Chapter {number:02d} — {title}\n\n"
        f"- **Contract:** {slug} sha256:{current}\n"
        f"- **Tone:** {tone.strip()}\n"
        f"- **Register:** {register.strip()}\n"
        f"- **What must survive:** {survives.strip()}\n"
    )
    if os.path.isfile(logpath):
        text = read_text(logpath).rstrip()
    else:
        text = (
            f"# Ductus log — {os.path.basename(bookdir)}\n\n"
            f"**Ductus:** {slug}  \n"
            f"**Contract:** `{rel_contract}`  \n"
            f"**Contract digest:** `sha256:{current}`\n\n"
            "A fresh session reads this beside the contract. Every chapter must carry its own "
            "entry; `ductus.py audit` checks completeness and digest parity.\n"
        )
    section = re.compile(rf"^##\s+Chapter\s+0*{number}\b.*?(?=^##\s+Chapter|\Z)",
                         re.M | re.S)
    if section.search(text):
        text = section.sub(entry, text, count=1).rstrip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + entry
    write_text(logpath, text)
    print(f"ductus: logged chapter {number:02d} under {slug} (sha256:{current}).")
    print(f"  {os.path.relpath(logpath, root)}")
    return 0


def cmd_audit(root, args):
    """The per-book check: every chapter has a current, readable carryover entry."""
    if len(args) != 1:
        print("usage: python tools/ductus.py audit <book-root>")
        return 2
    book = args[0]
    rel, slug, contract, err = _resolved_contract(root, book)
    if err == "unassigned":
        print(f"ductus audit: NOT RUN — {rel} has no `ductus:` assignment. "
              "Assign one at intake (`--ductus`), or record the absence deliberately.")
        return 2
    if err == "ambiguous":
        print(f"ductus audit: {book!r} matches more than one registry entry.")
        return 1
    if err == "unregistered":
        print(f"ductus audit: UNREGISTERED — {book!r} is not in BOOKS.yaml.")
        return 1
    if err:
        print(f"ductus audit: REFUSED — {err} for {book!r}.")
        return 1
    _press, ddir, cfg_err = press_config(root)
    if cfg_err:
        print(f"ductus audit: {CONFIG} does not parse — {cfg_err}")
        return 1
    ledger = os.path.join(root, ddir, slug, LEDGER)
    if not os.path.isfile(ledger):
        print(f"ductus audit: FAIL — {slug!r} has no {LEDGER}.")
        return 1
    bookdir = _book_dir(root, rel, book)
    if not bookdir:
        print(f"ductus audit: no book directory for {rel!r}.")
        return 1
    chapters = sorted(glob.glob(os.path.join(bookdir, "manuscript", "chapters", "chapter-*.md")))
    if not chapters:
        print(f"ductus audit: no chapters under {bookdir}/manuscript/chapters — nothing to audit.")
        return 2
    logpath = os.path.join(bookdir, BOOK_LOG)
    if not os.path.isfile(logpath):
        print(f"ductus audit: FAIL — no {BOOK_LOG}. A fresh session has no carryover record.")
        return 1
    text = read_text(logpath)
    current = digest(contract)
    fails = []
    quoted_checked = 0
    unquoted_entries = 0
    advisory = []
    if f"**Ductus:** {slug}" not in text:
        fails.append(f"header does not name the assigned ductus {slug!r}")
    for path in chapters:
        m = CHAPTER.search(os.path.basename(path))
        if not m:
            continue
        number = int(m.group(1))
        section = re.search(rf"^##\s+Chapter\s+0*{number}\b(.*?)(?=^##\s+Chapter|\Z)",
                            text, re.M | re.S)
        if not section:
            fails.append(f"chapter {number:02d} has no ductus entry")
            continue
        body = section.group(1)
        if f"**Contract:** {slug} sha256:{current}" not in body:
            fails.append(f"chapter {number:02d} was logged against a different contract digest")
        for field in ("Tone", "Register", "What must survive"):
            if not re.search(rf"\*\*{re.escape(field)}:\*\*\s*\S", body):
                fails.append(f"chapter {number:02d} has no {field} entry")
        quoted, missing_quoted, items, missing_items = survival_check(
            read_text(path), body)
        quoted_checked += len(quoted)
        if not quoted:
            unquoted_entries += 1
        for phrase in missing_quoted:
            fails.append(f"chapter {number:02d}: the entry says {phrase!r} must survive, "
                         "and the chapter does not contain it")
        for item, gone in missing_items:
            advisory.append((number, item, gone))
    print(f"ductus audit — {rel} under {slug} (sha256:{current})")
    print(f"  chapters: {len(chapters)}   log: {os.path.relpath(logpath, root)}")
    print(f"  survival: {quoted_checked} quoted claim(s) checked against the chapters")
    if unquoted_entries:
        print(f"  survival: {unquoted_entries} of {len(chapters)} entr(ies) quote nothing, "
              "so their survival line is prose — reported below, and not enforced")
    for number, item, gone in advisory[:12]:
        print(f"  ADVISORY chapter {number:02d}: {item!r} — "
              f"{', '.join(gone)} not found in the chapter")
    if len(advisory) > 12:
        print(f"  ADVISORY … {len(advisory) - 12} more")

    if fails:
        for f in fails:
            print(f"  FAIL    {f}")
        print("ductus audit: FAIL — a fresh session cannot recover the voice for every chapter.")
        return 1
    print("ductus audit: PASS — every chapter has a current carryover entry.")
    return 0


def cmd_cross(root, args):
    _press, ddir, err = press_config(root)
    if err == "no-yaml":
        print("ductus: no YAML parser here — nothing was checked (and not passed).")
        return 3
    slugs = ductus_dirs(root, ddir)
    seen = {}
    for slug in slugs:
        for h in held_headings(os.path.join(root, ddir, slug, LEDGER)):
            seen.setdefault(h, []).append(slug)
    leaks = {h: s for h, s in seen.items() if len(s) > 1}

    authored, skeleton = {}, []
    for slug in slugs:
        path = os.path.join(root, ddir, slug, CONTRACT)
        if not os.path.isfile(path):
            continue
        text = read_text(path)
        if thin_sections(text):
            skeleton.append(slug)
        else:
            authored[slug] = contract_sections(text)

    dupes = []
    for a, b in itertools.combinations(sorted(authored), 2):
        share, section = duplicate_share(authored[a], authored[b])
        if share >= DUP_SHARE:
            dupes.append((a, b, share, section))

    print(f"ductus cross — {len(seen)} distinct entr(ies), {len(authored)} compared "
          f"contract(s) of {len(slugs)} voice(s)")
    for h, holders in sorted(leaks.items()):
        print(f"  LEAK    {h!r} appears in {', '.join(holders)} — a preference in two "
              "ledgers has stopped being one voice's. Merge it deliberately in "
              f"{ddir}/{PROMOTIONS}, or remove it from the voice it was not earned by.")
    for a, b, share, section in dupes:
        print(f"  DUPLICATE  {a} and {b}: {share * 100:.0f}% of {section}'s six-word "
              "runs are shared — two contracts, one voice. Separate them, or merge one "
              f"deliberately in {ddir}/{PROMOTIONS}.")
    if skeleton:
        print(f"  NOTE    {len(skeleton)} skeleton contract(s) not compared: "
              f"{', '.join(skeleton)}")
    for index, register in enumerate(palette_registers(), 1):
        for slug in sorted(authored):
            share, _section = duplicate_share({"register": register}, authored[slug])
            if share < DUP_SHARE:
                continue
            if PALETTE_PROVENANCE.get(index) == slug:
                print(f"  NOTE    palette {index} is derived from {slug} "
                      f"({share * 100:.0f}% of its Register's six-word runs) — a voice "
                      "seeded from it begins inside that voice.")
            else:
                print(f"  NOTE    palette {index}'s Register is {share * 100:.0f}% shared "
                      f"with {slug}'s — a voice seeded from it begins inside that "
                      "voice, by construction.")
    if leaks or dupes:
        return 1
    print("ductus cross: no entry and no contract is held by two voices.")
    return 0


def cmd_calibrate(root, args):
    """Measure the book against the numeric lines its contract declares."""
    book = next((a for a in args if not a.startswith("--")), None)
    if not book:
        print("ductus: calibrate needs a book — `ductus.py calibrate test-books/some-book`.")
        return 2
    rel, slug, contract, err = _resolved_contract(root, book)
    if err == "unassigned":
        print(f"ductus calibrate: NOT RUN — {rel} carries no `ductus:` assignment, so "
              "no contract declares lines to measure it against.")
        return 2
    if err:
        print(f"ductus calibrate: cannot calibrate — {err} for {book!r}.")
        return 1
    bookdir = _book_dir(root, rel, book)
    if not bookdir:
        print(f"ductus calibrate: no book directory for {rel!r}.")
        return 1
    inv, source = contract_invariants(read_text(contract))
    if not inv:
        print(f"ductus calibrate: NOTHING MEASURED — {slug}'s contract declares no "
              "numeric invariants (no `ductus-invariants` block, and no prose line for "
              "negation / subject openings / texture words).")
        return 2
    gate = os.path.join(root, "tools", "prose", "check-monotony.py")
    if not os.path.isfile(gate):
        print(f"ductus calibrate: NOTHING MEASURED — no {os.path.relpath(gate, root)}.")
        return 2
    proc = subprocess.run([sys.executable, gate, bookdir], capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    measured = {}
    for key, pattern in (("subject_openings", r"M2 subject openings: ([\d.]+)%"),
                         ("negation", r"M3 'did not': ([\d.]+) per 10k"),
                         ("texture", r"M4 texture words: ([\d.]+) per 10k")):
        m = re.search(pattern, out)
        if m:
            measured[key] = float(m.group(1))
    if len(measured) < 3:
        print("ductus calibrate: NOTHING MEASURED — the monotony gate's output could "
              "not be read, so nothing was passed.")
        for line in out.strip().splitlines()[-4:]:
            print(f"  {line}")
        return 2
    labels = {"negation": "'did not' per 10k",
              "subject_openings": "% of sentences opening He/She/name",
              "texture": "texture words per 10k"}
    print(f"ductus calibrate — {rel} under {slug}")
    print(f"  limits read from {source}")
    fails = []
    for key, limit, value, within in compare_invariants(inv, measured):
        print(f"  {labels[key]:42} measured {value:6.1f}   declared {limit:<4} "
              f"{'PASS' if within else 'FAIL'}")
        if not within:
            fails.append(f"{key}: {value:g} against a declared {limit:g}")
    if fails:
        print(f"ductus calibrate: FAIL — the book leaves {len(fails)} line(s) its own "
              "contract declares.")
        for f in fails:
            print(f"  {f}")
        return 1
    print("ductus calibrate: PASS — the book sits inside every numeric line its contract "
          "declares.")
    return 0


def cmd_list(root, args):
    return cmd_check(root, args)


# --- self-test -------------------------------------------------------------

def _empty_voice(root, ddir, slug):
    d = os.path.join(root, ddir, slug)
    write_text(os.path.join(d, CONTRACT), NEW_CONTRACT.format(name=slug))
    write_text(os.path.join(d, LEDGER), NEW_LEDGER.format(name=slug))
    return d


def selftest():
    checks = []

    def ok(cond, label):
        checks.append((bool(cond), label))

    tmp = tempfile.mkdtemp(prefix="ductus-")
    try:
        write_text(os.path.join(tmp, CONFIG),
                   'press:\n  name: "Test Press"\n  ductus_dir: ductus\n')
        write_text(os.path.join(tmp, BOOKS), "books:\n  - path: some-book\n")
        ok(cmd_new(tmp, ["folio", "--name", "Folio",
                         "--register", "long literary"]) == 0,
           "new: a ductus is created from a slug")
        ok(os.path.isfile(os.path.join(tmp, "ductus", "folio", CONTRACT))
           and os.path.isfile(os.path.join(tmp, "ductus", "folio", LEDGER)),
           "new: the contract and the ledger both exist")
        ok(cmd_new(tmp, ["folio"]) == 1, "new: an existing slug is refused, not overwritten")
        ok(cmd_new(tmp, ["Bad Slug"]) == 2, "new: a non-slug is refused")
        ok(cmd_new(tmp, ["../escape"]) == 2, "new: a path traversal is refused")

        def captured(fn, *a):
            """(exit code, stdout). The report is the product — an exit code alone
            would have let a review that never fires look like a passing one."""
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = fn(*a)
            return rc, buf.getvalue()

        rc, out = captured(cmd_check, tmp, [])
        ok(rc == 0 and "still empty or near-empty" in out,
           "check: a skeleton voice passes AND is reported as unauthored")
        ok("identity" in out and "benchmarks" in out,
           "check: the report NAMES which sections have no body")

        # Authoring every section must clear the report, or the report is noise.
        cpath = os.path.join(tmp, "ductus", "folio", CONTRACT)
        authored = read_text(cpath)
        for s in CONTRACT_SECTIONS:
            authored = re.sub(rf"(^## {s}\s*$)\n_\(.*\)_",
                              rf"\1\nThis is the {s} section, written out at length as a "
                              "real body rather than a placeholder line.",
                              authored, flags=re.M | re.I)
        write_text(cpath, authored)
        rc, out = captured(cmd_check, tmp, [])
        ok(rc == 0 and "still empty or near-empty" not in out,
           "check: authoring every section clears the unauthored report")

        # development shows up in the numbers
        write_text(os.path.join(tmp, "ductus", "folio", LEDGER),
                   read_text(os.path.join(tmp, "ductus", "folio", LEDGER)) + (
                       "\n### 2026-01-01 — decision — chose the flat ending\n"
                       "- **book:** one\n- **chose:** a\n- **over:** b\n- **reason:** c\n"
                       "- **source:** author\n"
                       "\n### 2026-01-02 — preference — no consolation\n"
                       "- **status:** emergent\n- **from:** three decisions\n"
                       "- **reason:** r\n- **limit:** when the chapter has earned it\n"))
        kinds = entries(os.path.join(tmp, "ductus", "folio", LEDGER))
        ok(kinds.count("decision") == 1 and kinds.count("preference") == 1,
           "list: the ledger's decisions and preferences are counted")

        # isolation: a missing ledger is a failure, never an empty one
        os.remove(os.path.join(tmp, "ductus", "folio", LEDGER))
        ok(cmd_check(tmp, []) == 1, "check: a voice with no ledger fails")
        _empty_voice(tmp, "ductus", "folio")

        # isolation: a voice cannot read the press-wide ledger
        write_text(os.path.join(tmp, ROOT_LEDGER), "# the press-wide ledger\n")
        os.rename(os.path.join(tmp, "ductus", "folio", LEDGER),
                  os.path.join(tmp, "ductus", "folio", "elsewhere.md"))
        ok(cmd_check(tmp, []) == 1, "check: a voice with no ledger of its own fails")
        os.rename(os.path.join(tmp, "ductus", "folio", "elsewhere.md"),
                  os.path.join(tmp, "ductus", "folio", LEDGER))

        # a directory with no contract is not a voice
        os.makedirs(os.path.join(tmp, "ductus", "stray"))
        ok(cmd_check(tmp, []) == 1, "check: a directory with no contract fails")
        shutil.rmtree(os.path.join(tmp, "ductus", "stray"))

        # assignment: unknown voice fails, absent assignment is the author's call
        write_text(os.path.join(tmp, "BOOKS.yaml"),
                   "books:\n  - path: some-book\n    ductus: nonexistent\n")
        ok(cmd_check(tmp, []) == 1, "check: a book assigned to a missing voice fails")
        write_text(os.path.join(tmp, "BOOKS.yaml"),
                   "books:\n  - path: some-book\n    ductus: folio\n")
        ok(cmd_check(tmp, []) == 0, "check: an assigned book passes")

        # --- the interface the phases call ---------------------------------------
        # Everything below goes through cmd_contract, which is what a skill runs by path.
        def author(slug):
            p = os.path.join(tmp, "ductus", slug, CONTRACT)
            t = read_text(p)
            for name in CONTRACT_SECTIONS:
                t = re.sub(rf"(^## {name}\s*$)\n_\(.*\)_",
                           rf"\1\nA real {name} body, written out at length so the "
                           "placeholder is gone and the voice is authored.",
                           t, flags=re.M | re.I)
            write_text(p, t)

        def assign(slug, series=None):
            key = f"    series: {series}\n" if series else ""
            write_text(os.path.join(tmp, BOOKS),
                       f"books:\n  - path: some-book\n    ductus: {slug}\n{key}")

        # the documented default, named, and not a silent pass
        write_text(os.path.join(tmp, BOOKS), "books:\n  - path: some-book\n")
        rc, out = captured(cmd_contract, tmp, ["some-book"])
        ok(rc == 0 and "UNASSIGNED" in out and "root COMMONPLACE.md" in out,
           "contract: a book with no assignment reports UNASSIGNED and exits 0")

        # assigned to a voice nobody authored: the phase does not run
        _empty_voice(tmp, "ductus", "folio")
        assign("folio")
        rc, out = captured(cmd_contract, tmp, ["some-book"])
        ok(rc == 1 and "REFUSED" in out and "skeleton" in out,
           "contract: a skeleton contract REFUSES the run (exit 1)")

        author("folio")
        rc, out = captured(cmd_contract, tmp, ["some-book"])
        ok(rc == 0 and "is drafted under folio" in out and "sha256:" in out,
           "contract: an authored contract resolves with its digest")
        ok(re.search(r"voice:\s+\S+\s+sha256:[0-9a-f]{12}", out) is not None
           and re.search(r"ledger:\s+\S+\s+\d+ byte\(s\)\s+sha256:[0-9a-f]{12}", out)
           is not None,
           "contract: both digests are printed in the documented form")

        # a voice that exists but has no ledger cannot record taste
        os.rename(os.path.join(tmp, "ductus", "folio", LEDGER),
                  os.path.join(tmp, "ductus", "folio", "held.md"))
        rc, out = captured(cmd_contract, tmp, ["some-book"])
        ok(rc == 1 and "REFUSED" in out and "taste could not be recorded" in out,
           "contract: a voice with no ledger REFUSES the run")
        os.rename(os.path.join(tmp, "ductus", "folio", "held.md"),
                  os.path.join(tmp, "ductus", "folio", LEDGER))

        # a book outside the registry is refused, not defaulted to the root ledger
        rc, out = captured(cmd_contract, tmp, ["not-in-the-registry"])
        ok(rc == 1 and "UNREGISTERED" in out,
           "contract: a book outside BOOKS.yaml is refused, not defaulted")

        # a bare basename can be ambiguous, and then it asks for the full path
        write_text(os.path.join(tmp, BOOKS),
                   "books:\n  - path: a/some-book\n    ductus: folio\n"
                   "  - path: b/some-book\n    ductus: folio\n")
        rc, out = captured(cmd_contract, tmp, ["some-book"])
        ok(rc == 1 and "full path" in out,
           "contract: a basename matching two entries asks for the full path")
        rc, out = captured(cmd_contract, tmp, ["a/some-book"])
        ok(rc == 0 and "drafted under folio" in out,
           "contract: the full path resolves a name two entries share")

        # the override is allowed, and it says so out loud
        assign("folio")
        _empty_voice(tmp, "ductus", "quarto")
        author("quarto")
        rc, out = captured(cmd_contract, tmp, ["some-book", "--ductus", "quarto"])
        ok(rc == 0 and "overrides" in out and "is drafted under quarto" in out,
           "contract: --ductus overrides the registry and reports the override")
        rc, out = captured(cmd_contract, tmp, ["some-book", "--ductus"])
        ok(rc == 2, "contract: --ductus with no slug is a usage error")
        rc, out = captured(cmd_contract, tmp, [])
        ok(rc == 2, "contract: no book is a usage error")

        # the leak detector, proven by injection in both directions
        _empty_voice(tmp, "ductus", "quarto")
        same = "### 2026-01-01 — decision — chose the flat ending\n"
        for slug in ("folio", "quarto"):
            write_text(os.path.join(tmp, "ductus", slug, LEDGER),
                       read_text(os.path.join(tmp, "ductus", slug, LEDGER)) + same)
        ok(cmd_cross(tmp, []) == 1, "cross: an entry held by two voices is reported")
        write_text(os.path.join(tmp, "ductus", "quarto", LEDGER),
                   read_text(os.path.join(tmp, "ductus", "quarto", LEDGER))
                   .replace(same, ""))
        ok(cmd_cross(tmp, []) == 0, "cross: removing the duplicate clears the leak")

        # --- the survival check: a claim the chapter can contradict -----------------
        bookdir = os.path.join(tmp, "test-books", "some-book")
        os.makedirs(os.path.join(bookdir, "manuscript", "chapters"), exist_ok=True)
        chapter = os.path.join(bookdir, "manuscript", "chapters", "chapter-01.md")
        with_lever = ("# 1 — The Cellar\n\nThe brass lever was bedded in the pine stile. "
                      "She counted the seven handles twice.\n")
        write_text(chapter, with_lever)
        assign("folio")
        rc = cmd_log(tmp, [bookdir, "--chapter", "1", "--tone", "cold",
                           "--register", "plain past", "--survives",
                           "`the brass lever`, the gray cap and the seven handles"])
        ok(rc == 0, "log: an entry is written for a real chapter")
        rc, out = captured(cmd_audit, tmp, [bookdir])
        ok(rc == 0 and "1 quoted claim(s) checked" in out,
           "audit: a quoted survival claim the chapter contains passes")
        ok("ADVISORY" in out and "gray" in out,
           "audit: the unquoted part of the line is reported, not enforced")
        write_text(chapter, "# 1 — The Cellar\n\nShe counted the seven handles twice.\n")
        rc, out = captured(cmd_audit, tmp, [bookdir])
        ok(rc == 1 and "the brass lever" in out and "chapter 01" in out,
           "audit: a quoted claim the chapter no longer contains FAILS and is named")
        cmd_log(tmp, [bookdir, "--chapter", "1", "--tone", "cold",
                      "--register", "plain past", "--survives", "the seven handles"])
        rc, out = captured(cmd_audit, tmp, [bookdir])
        ok(rc == 0 and "quote nothing" in out,
           "audit: an entry that quotes nothing says so instead of passing silently")

        # --- calibrate: the contract's numbers, measured ---------------------------
        inv, source = contract_invariants(
            "```ductus-invariants\nnegation: 38\nsubject_openings: 30\ntexture: 130\n```\n")
        ok(inv == {"negation": 38, "subject_openings": 30, "texture": 130}
           and "block" in source,
           "calibrate: the machine block is read as declared limits")
        prose = ("- **negation** — \"did not\" no higher than **38** per 10,000. Under 30 "
                 "is the target.\n"
                 "- **subject openings** — no more than **30%** of sentences.\n"
                 "- **texture words** — the seven above no higher than **130** per 10,000.\n")
        inv2, source2 = contract_invariants(prose)
        ok(inv2 == inv and "no ductus-invariants block" in source2,
           "calibrate: the prose fallback reads the same limits, and says which it read")
        landmine = ("The negation row has since been repaired. A pass on 2026-11-11 "
                    "rewrote 268 of the 557 constructions.\n"
                    "- **negation** — \"did not\" no higher than **38** per 10,000. "
                    "Under 30 is the target; 45 is a book that cannot say what happens.\n")
        inv3, _src3 = contract_invariants(landmine)
        ok(inv3.get("negation") == 38,
           "calibrate: a date and a count on a nearby line do not become the limit")
        rows = compare_invariants({"negation": 38, "texture": 130},
                                  {"negation": 22.2, "subject_openings": 28.9,
                                   "texture": 135.9})
        ok([r[3] for r in rows] == [True, False],
           "calibrate: a book under a declared line passes it, and over one fails it")
        rc, out = captured(cmd_calibrate, tmp, [bookdir])
        ok(rc == 2 and "declares no numeric invariants" in out,
           "calibrate: a contract that declares nothing is NOT MEASURED, not passed")

        # --- cross: two contracts that are the same voice ---------------------------
        register = ("This voice writes close third person past tense in plain modern "
                    "English, short declaratives, objects placed by the hand rather "
                    "than described, no interior commentary, no metaphor the character "
                    "would not make, and a refusal to explain what the scene has "
                    "already shown.")
        for slug in ("dupea", "dupeb"):
            d = os.path.join(tmp, "ductus", slug)
            write_text(os.path.join(d, CONTRACT),
                       f"# {slug}\n\n## Identity\nA voice, seeded.\n\n## Register\n"
                       f"{register}\n\n## Refusals\n- none.\n\n## Breaking\nShorter.\n\n"
                       "## Benchmarks\nOne line only.\n")
            write_text(os.path.join(d, LEDGER), f"# COMMONPLACE — {slug}\n")
        rc, out = captured(cmd_cross, tmp, [])
        ok(rc == 1 and "DUPLICATE" in out and "dupea" in out,
           "cross: two contracts sharing a Register are reported as one voice")

        # --- the series layer: book -> series -> voice ----------------------------
        author("folio")
        series_text = ("# The Sequence\n\n## Identity\nOne man, six volumes.\n\n"
                       "## Register\nThe instrument does not change.\n\n"
                       "## Refusals\n- no reset.\n\n## Breaking\nThe same book twice.\n\n"
                       "## Benchmarks\nPending, and not invented.\n")
        serie = os.path.join(tmp, "ductus", "folio", SERIES_DIR, "the-sequence.md")
        write_text(serie, series_text)
        assign("folio", "the-sequence")
        rc, out = captured(cmd_contract, tmp, ["some-book"])
        ok(rc == 0 and "series voice" in out and "the-sequence" in out,
           "contract: a book resolves through its series, and the report names the layer")
        _r, _s, resolved_s, err_s = _resolved_contract(tmp, "some-book")
        ok(err_s is None and resolved_s == serie,
           "resolution: a book with no contract of its own is measured against its series")
        os.remove(serie)
        rc, out = captured(cmd_contract, tmp, ["some-book"])
        ok(rc == 1 and "REFUSED" in out and "the-sequence" in out,
           "contract: a declared series with no contract REFUSES the run")
        write_text(serie, series_text)
        own = os.path.join(bookdir, CONTRACT)
        write_text(own, "# Some Book\n\n## Identity\nThis book.\n\n## Register\nShort.\n\n"
                        "## Refusals\n- none.\n\n## Breaking\nFaster.\n\n"
                        "## Benchmarks\nOne line.\n")
        _r, _s, resolved_own, err_own = _resolved_contract(tmp, "some-book")
        ok(err_own is None and resolved_own == own,
           "resolution: a book's own contract still wins over its series")
        os.remove(own)

        # the interface: a command reached through main() must actually run
        argv, sys.argv = sys.argv, ["ductus.py", "check", "--root", tmp]
        try:
            rc = main()
        except TypeError as e:
            rc = f"TypeError: {e}"
        finally:
            sys.argv = argv
        ok(isinstance(rc, int), f"main: a dispatched command returns an exit code ({rc})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [label for good, label in checks if not good]
    for good, label in checks:
        print(("  ok    " if good else "  FAIL  ") + label)
    print("-" * 67)
    if failed:
        print(f"SELF-TEST FAILURE — {len(failed)} of {len(checks)} assertions failed.")
        return 1
    print(f"SELF-TEST PASS — {len(checks)} assertions (creation, slug safety, the "
          "unauthored report and its clearing, the voice interface and every "
          "refusal path, the book/series/voice resolution and its precedence, "
          "isolation, missing ledger, stray dir, assignment, development "
          "counts, leak detection, dispatch).")
    return 0


# --- main ------------------------------------------------------------------

def main():
    utf8_stdout()
    args = sys.argv[1:]
    root = repo_root()
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1]
        del args[i:i + 2]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2
    cmd, rest = args[0], args[1:]
    if cmd in ("selftest", "--self-test"):
        return selftest()
    table = {"new": cmd_new, "check": lambda r, a: cmd_check(r, a),
             "log": cmd_log, "audit": cmd_audit, "calibrate": cmd_calibrate,
             "voice": cmd_contract, "contract": cmd_contract,  # old name, kept for scripts
             "cross": lambda r, a: cmd_cross(r, a), "list": cmd_list}
    if cmd not in table:
        print(f"ductus: unknown command {cmd}")
        return 2
    return table[cmd](root, rest)


if __name__ == "__main__":
    sys.exit(main())
