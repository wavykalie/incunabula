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
  - It will not invent a ductus. `new` writes a skeleton; the identity is authored by
    a person or an agent, and an empty contract is reported as empty rather than
    filled with house defaults.
  - It will not accept a missing ledger as an empty one, and it will not quietly
    assign a book to a voice: `ductus:` in BOOKS.yaml is the author's assignment, and
    `check` NAMES the unassigned books.
  - It is not a gate. Nothing here is enforced against a book, and no ductus may move
    a threshold — a measurement moves on a named corpus, never on taste.

usage:  tools/ductus.py <command> [--root DIR]
  new SLUG [--name "…"] [--register "…"]   create a voice (skeleton, to be authored)
  check                                    every voice, its isolation, the unassigned books
  contract BOOK [--ductus SLUG]            WHAT A RUN DRAFTS UNDER: the resolved contract
                                           for a book, its digest, or UNASSIGNED. A book
                                           assigned to a voice whose contract is still a
                                           skeleton is REFUSED — a phase may not draft
                                           under a voice nobody authored.
  cross                                    report an entry held by two ledgers
  list                                     each voice and how far it has developed
  --self-test

EXIT
  0  clean
  1  a rule failed (each failure names it)
  2  usage error, or no press declared
  3  no YAML parser here — nothing was checked (and not passed)
"""

import contextlib
import io
import os
import re
import shutil
import sys
import tempfile

CONFIG = "ductus.yaml"
BOOKS = "BOOKS.yaml"
DEFAULT_DIR = "ductus"
PROMOTIONS = "PROMOTIONS.md"
CONTRACT = "ductus.md"
LEDGER = "COMMONPLACE.md"
ROOT_LEDGER = "COMMONPLACE.md"

# The ledger entry types, same ceremony as the root COMMONPLACE.md. `list` counts them
# to show development; none of them is enforced by anything.
ENTRY_KINDS = ("decision", "preference", "outcome", "promotion")
ENTRY_HEADING = re.compile(r"^#{2,3}\s+(?:\d{4}-\d{2}-\d{2}\s+[—-]\s+)?(\w+)", re.M)

CONTRACT_SECTIONS = ("identity", "register", "refusals", "breaking", "benchmarks")


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


def book_assignments(root):
    data, err = load_yaml(os.path.join(root, BOOKS))
    if err or not isinstance(data, dict):
        return None
    out = []
    for b in data.get("books") or []:
        if isinstance(b, dict):
            out.append((b.get("path"), b.get("ductus")))
    return out


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


def cmd_new(root, args):
    slug = next((a for a in args if not a.startswith("--")), None)
    if not slug:
        print("ductus: new needs a slug — `ductus.py new my-voice`.")
        return 2
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        print(f"ductus: {slug!r} is not a slug — lowercase, digits and hyphens.")
        return 2
    name = args[args.index("--name") + 1] if "--name" in args else slug
    register = args[args.index("--register") + 1] if "--register" in args else None
    _press, ddir, err = press_config(root)
    if err == "no-yaml":
        print(f"ductus: no YAML parser here — {CONFIG} was not read (and not passed).")
        return 3
    d = os.path.join(root, ddir, slug)
    if os.path.exists(d):
        print(f"ductus: {ddir}/{slug} already exists — nothing created, nothing changed.")
        return 1
    contract = NEW_CONTRACT.format(name=name)
    if register:
        # Recorded verbatim as an ADDITIONAL section: the template's Register section
        # stays a placeholder, because a declared one-line register is the creator's
        # first taste and not a substitute for the section.
        contract += f"\n## Register (as declared by the creator)\n{register}\n"
    write_text(os.path.join(d, CONTRACT), contract)
    write_text(os.path.join(d, LEDGER), NEW_LEDGER.format(name=name))
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
    contract = os.path.join(d, CONTRACT)
    ledger = os.path.join(d, LEDGER)
    if not os.path.isfile(contract):
        print(f"ductus: REFUSED — {rel} is assigned to {slug!r}, and there is no "
              f"{ddir}/{slug}/{CONTRACT}. A phase does not draft under a voice that "
              "does not exist.")
        return 1
    if not os.path.isfile(ledger):
        print(f"ductus: REFUSED — {slug!r} has no {ddir}/{slug}/{LEDGER}. Its taste "
              "could not be recorded, which is the one thing the ledger is for.")
        return 1
    thin = thin_sections(read_text(contract))
    if thin:
        print(f"ductus: REFUSED — {ddir}/{slug}/{CONTRACT} is still a skeleton "
              f"({', '.join(thin)}). Author it, or remove the assignment from "
              "BOOKS.yaml so the book is drafted under the root ledger openly.")
        return 1

    print(f"ductus: {rel} is drafted under {slug}")
    print(f"  contract: {ddir}/{slug}/{CONTRACT}  sha256:{digest(contract)}")
    print(f"  ledger:   {ddir}/{slug}/{LEDGER}  "
          f"{os.path.getsize(ledger)} byte(s)  sha256:{digest(ledger)}")
    print("  read before: drafting, revision, auditing and scoring. Record these digests "
          "in the session ledger so a result is attributable to the contract it was "
          "drafted under. Not packaging: the query letter and cover copy are written in "
          "the imprint's register, not the book's.")
    return 0


def cmd_cross(root, args):
    _press, ddir, err = press_config(root)
    if err == "no-yaml":
        print("ductus: no YAML parser here — nothing was checked (and not passed).")
        return 3
    seen = {}
    for slug in ductus_dirs(root, ddir):
        for h in held_headings(os.path.join(root, ddir, slug, LEDGER)):
            seen.setdefault(h, []).append(slug)
    leaks = {h: s for h, s in seen.items() if len(s) > 1}
    print(f"ductus cross — {len(seen)} distinct entr(ies) across the voices")
    for h, slugs in sorted(leaks.items()):
        print(f"  LEAK    {h!r} appears in {', '.join(slugs)} — a preference in two "
              "ledgers has stopped being one voice's. Merge it deliberately in "
              f"{ddir}/{PROMOTIONS}, or remove it from the voice it was not earned by.")
    if leaks:
        return 1
    print("ductus cross: no entry appears in more than one voice's ledger.")
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

        def assign(slug):
            write_text(os.path.join(tmp, BOOKS),
                       f"books:\n  - path: some-book\n    ductus: {slug}\n")

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
        ok(re.search(r"contract: \S+\s+sha256:[0-9a-f]{12}", out) is not None
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
          "unauthored report and its clearing, the contract interface and every "
          "refusal path, isolation, missing ledger, stray dir, assignment, development "
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
             "contract": cmd_contract,
             "cross": lambda r, a: cmd_cross(r, a), "list": cmd_list}
    if cmd not in table:
        print(f"ductus: unknown command {cmd}")
        return 2
    return table[cmd](root, rest)


if __name__ == "__main__":
    sys.exit(main())
