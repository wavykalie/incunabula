#!/usr/bin/env python3
"""blind-packet.py — carry the book, and nothing about the system.

Why this exists
---------------
An engine that reads its own paperwork invents paperwork. A run that reads seventeen
phases of gates, ledger, and voice-contract vocabulary before it invents a world writes a
world made of those words. Two books in a row came back with a court where a game should
have been, and each world was a one-to-one mapping of this tooling's filing system: the
voice spec became a writ, the ledger became a book of terms, the gate became a term, the
digest became a seal.

This tool builds the opposite of that. It assembles a packet from the author's own
sentence, the genre, and the ask, and it refuses to ship a packet containing this
pipeline's vocabulary. The packet goes to a reader or a model that has never seen the
system — a fresh context, a different model, a person — and comes back with three worlds.

It is make-ready, not a gate: it reads no manuscript and can fail no book.

Usage
-----
  python tools/blind-packet.py <book-root> --idea "one sentence"   print the packet
  python tools/blind-packet.py <book-root> --write                 write it to maintenance/
  python tools/blind-packet.py <book-root> --prompt                print the paste-ready ask
  python tools/blind-packet.py <book-root> --gate                  judge world.md (Phase 2)
  python tools/blind-packet.py <book-root> --discards              refuse a scrapped premise
  python tools/blind-packet.py <book-root> --audit <file>          scan an artifact for leak

  --idea may be a file path; otherwise the tool reads <book-root>/maintenance/IDEA.md.
  --allow "word,word" records a deliberate use of a flagged word and continues.

Exit codes: 0 clean, 1 the packet, the audited file, the chosen world engine, or the premise
carries the pipeline's vocabulary or rebuilds a scrapped engine, 2 usage, no idea to send, or
nothing to judge.
"""

import argparse
import datetime
import os
import re
import sys

# Words that belong to this system and cannot help anyone invent a world.
SYSTEM_WORDS = [
    "canon", "ledger", "ductus", "colophon", "quoin", "platen", "incunabula",
    "freeze", "checkpoint", "sha256", "digest", "commonplace", "phase map",
    "run-gates", "press run", "standing type", "premise ledger", "case keeper",
]

# The attractor itself: the vocabulary of administration. These are not forbidden in a
# finished novel — a book may be about a lawsuit — but they must not arrive before the
# world does, because arriving first is how the world becomes a filing cabinet.
ADMIN_WORDS = [
    "contract", "covenant", "indenture", "writ", "charter", "surety", "lien",
    "collateral", "escrow", "statute", "clause", "precedent", "affidavit",
    "tribunal", "tariff", "toll", "deed", "notary", "plaintiff", "defendant",
    "litigation", "debt", "debtor", "creditor", "audit", "permit", "licence",
    "license", "ordinance", "treaty",
]

# Engines this project has already built and thrown away. A premise that rebuilds one is
# refused by name, with the entry that scrapped it -- not scored, not softened, not
# re-named into a pass. Each phrase is a shape, not a word: "debt" is a legitimate subject,
# while "standing buys" is the ladder the scrapped book stood on.
DISCARDS = [
    {
        "slug": "the-debt-engine",
        "what": "the family as collateral on an ancestor's surety, where cleared terms bought "
                "standing, standing bought shares, and shares bought a charter",
        "recorded": "root COMMONPLACE.md, 2026-11-24, under 'Do not rebuild'",
        "phrases": [
            "collateral on a surety", "collateral on the surety", "terms for standing",
            "standing buys", "shares buy", "seat in the concord", "seats in the concord",
            "charter-holder", "buys a charter", "writ-holder", "the assay",
        ],
    },
    {
        "slug": "the-clerk-narrator",
        "what": "a narrator who is a device the story casts: a clerk, notary or registrar "
                "recording the book from inside the fiction",
        "recorded": "root COMMONPLACE.md, 2026-11-24; ductus/game-master/COMMONPLACE.md",
        "phrases": [
            "narrated by a clerk", "the narrator is a clerk", "a clerk of the",
            "the clerk writes", "keeper of the writ", "the undersigned",
        ],
    },
]

PACKET = """# The blind packet — {title}

*Read this and nothing else. There is no system behind this document, no process to
follow, and no one to ask.*

## The sentence

{idea}

## The book

- Genre: {genre}
- Readers: {audience}
- Length: {length}

## What you are asked for

Invent the world this book happens in. Not the plot, not the outline: the world, and the
one thing about it that makes the story possible.

1. **Three worlds.** Each in under two hundred words. Different in kind, not in tone.
2. For each world, four things:
   - the physical fact that puts this family underground and keeps them there;
   - what their work produces that the surface cannot do without;
   - three scenes that could happen nowhere else;
   - one line a reader would repeat to a friend.
3. **Say which world is the most game-like** — the one this genre promises a reader — and
   why the other two are not.
4. **Write the first hundred and fifty words of chapter one** in the voice of a dungeon
   master who enjoys setting traps and is not sorry about it.
5. Choose one world. State the choice in one sentence.

Do not smooth anything. A memorable line matters more than a consistent system.
"""

PROMPT = """You are a novelist and a dungeon master. You have no files, no project, no
process, and no memory of one. Everything you have is below.

{packet}

Answer in full. Do not ask what this is for, and do not describe a method."""


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def field(text, key):
    """A plain `key: value` line, without a YAML dependency."""
    m = re.search(r"^\s*" + re.escape(key) + r"\s*:\s*(.+?)\s*$", text, re.M)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")


def find_field_here(root, key, fallback=""):
    """Only the book's own state files: an ancestor's field is about another book."""
    for name in ("PROJECT_STATE.yaml", "STATE.yaml"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            v = field(read_text(p), key)
            if v:
                return v
    return fallback


def find_field(root, key, fallback=""):
    here = os.path.abspath(root)
    for _ in range(4):
        for name in ("PROJECT_STATE.yaml", "STATE.yaml", "BOOKS.yaml"):
            p = os.path.join(here, name)
            if os.path.isfile(p):
                v = field(read_text(p), key)
                if v:
                    return v
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    return fallback


def clean_length(value):
    """A declared length, not a run status that happened to land in a length field."""
    if not value:
        return ""
    v = value.strip()
    if len(v) > 60:
        return ""
    if re.search(r"(exit|not run|no chapters|pending|tbd|unknown|n/?a)", v, re.I):
        return ""
    if not re.search(r"[0-9]", v):
        return ""
    return v


def hits(text, words):
    found = []
    for n, line in enumerate(text.splitlines(), 1):
        for w in words:
            for _m in re.finditer(r"\b" + re.escape(w) + r"(?:s|es)?\b", line, re.I):
                found.append((n, w, line.strip()))
    return found


def report(found, label, limit=40):
    if not found:
        print("blind-packet: " + label + ": clean")
        return
    by_word = {}
    for _n, w, _line in found:
        by_word[w] = by_word.get(w, 0) + 1
    summary = ", ".join(w + " x" + str(c) for w, c in
                        sorted(by_word.items(), key=lambda kv: -kv[1]))
    print("blind-packet: " + label + ": " + str(len(found)) + " hit(s) — " + summary)
    for n, w, line in found[:limit]:
        print("  line " + str(n) + ": [" + w + "] " + line[:150])
    if len(found) > limit:
        print("  ... " + str(len(found) - limit) + " more")


def section(text, title):
    """The body under a heading whose text starts with `title`, case-insensitive."""
    out, inside, level = [], False, 0
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if m.group(2).strip().lower().startswith(title):
                inside, level = True, len(m.group(1))
                continue
            if inside and len(m.group(1)) <= level:
                break
        if inside:
            out.append(line)
    return "\n".join(out)


def discard_hits(text):
    """[(discard, phrase, line)] for every scrapped engine this text is rebuilding."""
    low = text.lower()
    found = []
    for d in DISCARDS:
        for phrase in d["phrases"]:
            for m in re.finditer(r"\b" + re.escape(phrase), low):
                found.append((d, phrase, low.count("\n", 0, m.start()) + 1))
    return found


def discards_check(root, allowed=frozenset()):
    """Intake's refusal: a premise may not rebuild an engine this project scrapped."""
    checked = []
    premise = os.path.join(root, "premise.md")
    if os.path.isfile(premise):
        checked.append((premise, read_text(premise)))
    world = os.path.join(root, "world.md")
    if os.path.isfile(world):
        # Only the engine that was chosen: `## Discarded` is required to name these.
        checked.append((world, section(read_text(world), "chosen engine")))
    if not checked:
        print("blind-packet: discards: NOT RUN — no premise.md or world.md to judge in " + root)
        return 2

    bad = 0
    for path, text in checked:
        found = [t for t in discard_hits(text) if t[0]["slug"] not in allowed]
        if not found:
            continue
        bad += 1
        print("blind-packet: REFUSED — " + os.path.basename(path) +
              " rebuilds an engine this project already scrapped:")
        seen = set()
        for d, phrase, line in found:
            if d["slug"] in seen:
                continue
            seen.add(d["slug"])
            print("  " + d["slug"] + " — " + d["what"])
            print("    scrapped in " + d["recorded"])
            print("    first at line " + str(line) + ": \"" + phrase + "\"")

    if bad:
        print("blind-packet: discards: FAIL — change the engine, or overturn the record with "
              "a dated entry in the root COMMONPLACE.md saying what the old diagnosis "
              "missed, then re-run with --allow-discard <slug>.")
        return 1

    print("blind-packet: discards: clean — no scrapped engine in "
          + ", ".join(os.path.basename(p) for p, _t in checked))
    return 0


def gate(root, admin, allow_discards=frozenset()):
    """Phase 2's world gate: the artifact, not the process. Returns 0 pass, 1 fail, 2 no world."""
    path = os.path.join(root, "world.md")
    if not os.path.isfile(path):
        print("blind-packet: world gate: NOT RUN — no world.md at " + path + ". "
              "A book that has not reached Phase 2 is not judged by this row.")
        return 2

    text = read_text(path)
    fails = []

    considered = section(text, "engines considered")
    cands = re.findall(r"^###\s+\S", considered, re.M) if considered else []
    if len(cands) < 3:
        fails.append("W1 the world records " + str(len(cands)) + " candidate engine(s) "
                     "under '## Engines considered'; the gate requires three, because a "
                     "single engine cannot be seen to have been chosen")

    chosen = section(text, "chosen engine").strip()
    if not chosen:
        fails.append("W2 no '## Chosen engine' section; the world has not been decided")
    else:
        found = hits(chosen, admin)
        if found:
            print("blind-packet: the chosen engine carries administration:")
            for n, w, line in found[:20]:
                print("  line " + str(n) + ": [" + w + "] " + line[:150])
            fails.append("W3 the chosen engine is administrative ("
                         + ", ".join(sorted({w for _n, w, _l in found}))
                         + "); a world built on a contract, a debt, a charter, a court or "
                         "a title is this tooling's filing system in costume")

    discarded = section(text, "discarded")
    if not hits(discarded, admin):
        fails.append("W4 no administrative engine named among the discarded; the attractor "
                     "goes on the record or the next pilot reaches for it too")

    rebuilt = [t for t in discard_hits(chosen) if t[0]["slug"] not in allow_discards]
    for d in {id(t[0]): t[0] for t in rebuilt}.values():
        fails.append("W5 the chosen engine rebuilds " + d["slug"] + " (" + d["what"] + "), "
                     "scrapped in " + d["recorded"] + "; new nouns over the same ladder is "
                     "the same engine. Change it, or overturn the record and pass "
                     "--allow-discard " + d["slug"])

    if fails:
        for f in fails:
            print("blind-packet: FAIL " + f)
        print("blind-packet: world gate: FAIL — " + str(len(fails)) + " rule(s). "
              "Repair world.md, re-run, and record the verdict.")
        return 1

    print("blind-packet: world gate: PASS (W1 three candidates, W2 chosen engine, "
          "W3 chosen engine physical, W4 attractor named and discarded, W5 no scrapped "
          "engine rebuilt)")
    return 0


def build(root, idea):
    title = find_field_here(root, "title") or find_field(root, "title",
                                                         os.path.basename(os.path.abspath(root)))
    genre = find_field_here(root, "genre") or find_field(root, "genre", "(say what it is)")
    audience = find_field_here(root, "audience") or find_field(root, "audience", "(say who reads it)")
    length = (clean_length(find_field_here(root, "length_target"))
              or clean_length(find_field_here(root, "target_words"))
              or clean_length(find_field_here(root, "length"))
              or "(one novel)")
    return PACKET.format(title=title, idea=idea.strip(), genre=genre,
                         audience=audience, length=length)


def selftest():
    """The four gate rules, both directions. A rule that cannot fail is not a rule."""
    import contextlib
    import io
    import tempfile

    passed, failed = 0, []

    def check(cond, label):
        nonlocal passed
        if cond:
            passed += 1
        else:
            failed.append(label)

    good = """# World

## Engines considered

### 1. A
body

### 2. B
body

### 3. C
body

## Chosen engine

The floor breathes and the family works inside its inhale.

## Discarded

The surety lost: it described the paperwork, not the world.
"""

    def run(text, admin=None, name="world.md", allow=frozenset()):
        d = tempfile.mkdtemp(prefix="blind-packet-selftest-")
        if text is not None:
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(text)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = gate(d, ADMIN_WORDS if admin is None else admin, allow)
        return rc, buf.getvalue()

    rc, out = run(good)
    check(rc == 0, "a well-formed world passes (W1-W4)")
    check("PASS" in out and "W4" in out, "a pass names the rules it satisfied")

    rc, out = run(good.replace("### 3. C\nbody\n\n", ""))
    check(rc == 1, "two candidate engines fail the gate")
    check("W1" in out, "the W1 failure is named")

    rc, out = run(good.replace("## Chosen engine", "## Something else"))
    check(rc == 1, "a world with no chosen engine fails")
    check("W2" in out, "the W2 failure is named")

    rc, out = run(good.replace("The floor breathes",
                               "The surety is securitised against the bloodline. The floor breathes"))
    check(rc == 1, "an administrative chosen engine fails")
    check("W3" in out, "the W3 failure is named")

    rc, out = run(good.replace("The surety lost: it described the paperwork, not the world.",
                               "The other two were duller."))
    check(rc == 1, "discards that name no administrative engine fail")
    check("W4" in out, "the W4 failure is named")

    rebuilt = good.replace("The floor breathes and the family works inside its inhale.",
                           "The family clears terms for standing, and standing buys shares.")
    rc, out = run(rebuilt)
    check(rc == 1, "W5 refuses a scrapped engine rebuilt under new nouns")
    check("W5" in out, "the W5 failure is named")

    rc, out = run(rebuilt, allow={"the-debt-engine"})
    check(rc == 0, "--allow-discard clears a recorded overturn")

    rc, out = run(None)
    check(rc == 2, "no world.md is NOT RUN, never a pass")
    check("NOT RUN" in out, "the NOT RUN verdict says so")

    rc, _out = run(good.replace("The floor breathes",
                                "The floor is held by a charter. It breathes"),
                   admin=[w for w in ADMIN_WORDS if w != "charter"])
    check(rc == 0, "--allow on a flagged word lets the engine through")

    clean = build("selftest", "A family digs a thousand terms of a living body; "
                              "what they carry out is a hand, a lung, an eye.")
    check(not hits(clean, SYSTEM_WORDS + ADMIN_WORDS), "a plain idea builds a clean packet")

    dirty = build("selftest", "A bloodline is bound by a contract of debt and clause; "
                               "the ledger records every term.")
    check(hits(dirty, SYSTEM_WORDS + ADMIN_WORDS), "a contaminated idea is caught and refused")

    if failed:
        print("SELF-TEST FAIL")
        for f in failed:
            print("  FAIL " + f)
        print("  " + str(passed) + " passed, " + str(len(failed)) + " failed")
        return 1

    print("SELF-TEST PASS — " + str(passed) + " assertions (W1 three candidates, W2 chosen "
          "engine, W3 engine not administrative, W4 attractor named, W5 no scrapped engine "
          "rebuilt, the overturn path, NOT RUN without a world, --allow, packet construction "
          "and refusal)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Build a packet that carries the book and nothing about the system.")
    ap.add_argument("book", nargs="?", help="book root, e.g. test-books/<book>")
    ap.add_argument("--idea", help="the author's sentence, or a path holding it")
    ap.add_argument("--write", action="store_true", help="write maintenance/BLIND_PACKET.md")
    ap.add_argument("--prompt", action="store_true", help="print the paste-ready ask")
    ap.add_argument("--selftest", action="store_true", help="run this tool's own assertions")
    ap.add_argument("--gate", action="store_true",
                    help="judge world.md against the Phase 2 world gate (W1-W5)")
    ap.add_argument("--discards", action="store_true",
                    help="refuse a premise that rebuilds a scrapped engine")
    ap.add_argument("--allow-discard", default="",
                    help="comma-separated discard slugs to accept, for a recorded overturn")
    ap.add_argument("--audit", metavar="FILE", help="scan a file for leaked system idiom")
    ap.add_argument("--allow", default="", help="comma-separated words to accept")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    allow = {w.strip().lower() for w in args.allow.split(",") if w.strip()}
    system = [w for w in SYSTEM_WORDS if w not in allow]
    admin = [w for w in ADMIN_WORDS if w not in allow]

    allowed = {s.strip() for s in args.allow_discard.split(",") if s.strip()}

    if args.discards:
        if not args.book or not os.path.isdir(args.book):
            print("blind-packet: --discards needs a book directory", file=sys.stderr)
            return 2
        return discards_check(args.book, allowed)

    if args.gate:
        if not args.book or not os.path.isdir(args.book):
            print("blind-packet: --gate needs a book directory", file=sys.stderr)
            return 2
        return gate(args.book, admin, allowed)

    if args.audit:
        if not os.path.isfile(args.audit):
            print("blind-packet: no such file: " + args.audit, file=sys.stderr)
            return 2
        text = read_text(args.audit)
        found = hits(text, system + admin)
        report(found, os.path.basename(args.audit))
        if found:
            print("blind-packet: this artifact reads like the tooling. The world it "
                  "describes is probably the filing system in costume.")
            return 1
        return 0

    if not args.book or not os.path.isdir(args.book):
        print("blind-packet: give a book directory (or --audit a file)", file=sys.stderr)
        return 2

    idea = args.idea or ""
    if idea and os.path.isfile(idea):
        idea = read_text(idea)
    if not idea:
        p = os.path.join(args.book, "maintenance", "IDEA.md")
        if os.path.isfile(p):
            idea = read_text(p)
    if not idea.strip():
        print("blind-packet: no idea to send. Pass --idea, or write the author's own "
              "sentence to maintenance/IDEA.md. Do not build the packet from a premise "
              "that already carries the system's words — that is the contamination the "
              "packet exists to avoid.", file=sys.stderr)
        return 2

    packet = build(args.book, idea)
    out = PROMPT.format(packet=packet) if args.prompt else packet

    found = hits(out, system + admin)
    report(found, "packet")
    if found:
        print("blind-packet: REFUSED — the packet carries vocabulary from inside the "
              "system. Remove it, or name a deliberate use with --allow.")
        return 1

    if args.write:
        dest = os.path.join(args.book, "maintenance", "BLIND_PACKET.md")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        stamp = datetime.date.today().isoformat()
        body = ("<!-- built " + stamp + " by tools/blind-packet.py; send it as-is -->\n\n"
                + out)
        with open(dest, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        print("blind-packet: wrote " + dest + " (" + str(len(out.split())) +
              " words). Send it to a reader or a model that has never seen this project.")
    else:
        print()
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
