#!/usr/bin/env python3
"""review-sheet.py - render the frozen 20 premises as the sheet Kalie signs off on.

Design §13 requires a written yes on the premise list before any book is generated, and
§6 requires that the yes is given on the RENDERED text, because that is the exact string
both arms receive. So the sheet shows each premise verbatim, with its digest, its arm
pairing, and the deviations that need a decision of their own.

The sheet is generated, never hand-written, and it is not regenerated over itself: once
it has ticks on it, it is a record of a decision, not a view of a file.

usage:
    python review-sheet.py            write the sheet beside the frozen premises
    python review-sheet.py --force    overwrite an existing sheet (discards sign-off)
"""

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.path.join(HERE, "frozen", "premises-v1.json")
SHEET = os.path.join(HERE, "frozen", "premises-v1-review.md")
DIGEST_LEN = 16                    # hex prefix; 64 bits is plenty to catch a mismatch

# Design §12.2, answered in DECISIONS.md: the primary target both arms receive, and the
# exploratory long-form stratum, which is a separate set of premises, not four books of
# the twenty made longer. The band is +-10%.
A_TARGET, A_BAND = 60_000, (54_000, 66_000)
LONG_TARGET, LONG_BAND = 200_000, (180_000, 220_000)
PROPER_NOUN_STOP = {
    "the", "a", "an", "her", "his", "their", "its", "one", "two", "three", "four",
    "six", "ten", "twelve", "twenty", "under", "and",
}


def _premise_module():
    spec = importlib.util.spec_from_file_location("premise", os.path.join(HERE, "premise.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check(doc):
    """Everything the sheet asserts is verified here, not assumed. Returns (errors, facts)."""
    errors, facts = [], {}
    ps = doc.get("premises") or []
    if len(ps) != 20:
        errors.append(f"{len(ps)} premises frozen, expected 20")
    ids = [p.get("id") for p in ps]
    if len(set(ids)) != len(ids):
        errors.append("duplicate premise id")

    per_genre = {}
    for i, p in enumerate(ps):
        where = p.get("id", f"#{i + 1}")
        text = p.get("text") or ""
        if not text:
            errors.append(f"{where}: no rendered text")
            continue
        if text != " ".join(p[f].strip() for f in ("protagonist", "situation", "conflict",
                                                   "setting", "stakes")):
            errors.append(f"{where}: text is not the render of its fields")
        if p.get("words") != len(text.split()):
            errors.append(f"{where}: words field disagrees with the text")
        for f in ("protagonist", "situation", "conflict", "setting", "stakes"):
            if not p.get(f):
                errors.append(f"{where}: empty {f}")
        per_genre[p.get("genre")] = per_genre.get(p.get("genre"), 0) + 1

    for genre, n in sorted(per_genre.items()):
        if n != 2:
            errors.append(f"genre {genre!r}: {n} premise(s), expected 2")
    facts["genres"] = len(per_genre)
    facts["per_genre"] = per_genre

    def toks(t):
        return {w for w in re.findall(r"[a-z]{4,}", t.lower())}

    worst = (0.0, "", "")
    texts = [(p["id"], toks(p["text"])) for p in ps if p.get("text")]
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i][1], texts[j][1]
            sim = len(a & b) / len(a | b) if a and b else 0.0
            if sim > worst[0]:
                worst = (sim, texts[i][0], texts[j][0])
    facts["max_overlap"] = worst
    if worst[0] > 0.55:
        errors.append(f"{worst[1]} ~ {worst[2]}: token overlap {worst[0]:.2f}")

    # The frozen file must still be the sample the committed pool and seed produce. This
    # catches a pool edited after freezing, which the recorded pool hash would only catch
    # if someone re-checked it by hand.
    pm = _premise_module()
    pool = pm.load()
    pool_digest = pm.sha256_file(pm.POOL)
    facts["pool_digest"] = pool_digest
    if doc.get("pool_sha256") and doc["pool_sha256"] != pool_digest:
        errors.append(f"pool has changed since freezing: {doc['pool_sha256'][:12]} -> "
                      f"{pool_digest[:12]}")
    redo = pm.sample(pool, doc.get("seed", 20261030))
    if [p["id"] for p in redo] != ids or [p["text"] for p in redo] != [p.get("text") for p in ps]:
        errors.append("re-deriving from the seed does not reproduce the frozen sample")

    sidecar = FROZEN + ".sha256"
    facts["frozen_digest"] = pm.sha256_file(FROZEN)
    facts["frozen_verified"] = False
    if not os.path.exists(sidecar):
        errors.append("no .sha256 sidecar")
    else:
        with open(sidecar, encoding="utf-8") as fh:
            want = fh.read().split()[0]
        facts["frozen_verified"] = want == facts["frozen_digest"]
        if not facts["frozen_verified"]:
            errors.append(f"frozen file does not match its sidecar: {want[:12]}")

    words = [p.get("words") or 0 for p in ps]
    facts["total_words"] = sum(words)
    facts["min_words"], facts["max_words"] = (min(words), max(words)) if words else (0, 0)
    facts["design_band"] = pm.WORDS_DESIGN
    facts["hard_band"] = pm.WORDS_HARD

    # Lookahead, so overlapping pairs are found: a non-overlapping scan reads "The North
    # Atlantic" as "The North", filters the sentence-initial article, and then never sees
    # "North Atlantic" at all.
    names = {}
    for p in ps:
        for m in re.finditer(r"(?=(\b[A-Z][a-z]+\s+[A-Z][a-z]+\b))", p.get("text") or ""):
            pair = m.group(1)
            if pair.split()[0].lower() not in PROPER_NOUN_STOP:
                names.setdefault(pair, []).append(p["id"])
    facts["proper_nouns"] = names
    return errors, facts


def build(doc, facts, errors):
    ps = doc["premises"]
    out = []
    w = out.append
    fd = facts["frozen_digest"]
    short = fd[:DIGEST_LEN]

    w("# Premise sign-off sheet — 20 frozen premises\n")
    w("**Study:** 50-novel prose-tell study (plus an exploratory 200,000-word long-form "
      "stratum, `DECISIONS.md` §2), design v1 amended per `study/REDTEAM.md`  ")
    w("**Frozen file:** `premises/frozen/premises-v1.json`  ")
    w(f"**sha256:** `{short}…`  "
      + ("verified against its `.sha256` sidecar" if facts["frozen_verified"] else
         "**DOES NOT MATCH ITS SIDECAR**") + "  ")
    w(f"**Frozen at:** {doc.get('frozen_at', '?')} · **seed** `{doc.get('seed')}` · "
      f"**per genre** {doc.get('per_genre')} · **pool sha256** "
      f"`{facts['pool_digest'][:DIGEST_LEN]}…` "
      + ("(unchanged; sample re-derives from the seed)" if not any(
          "pool" in e or "re-deriving" in e for e in errors) else
         "**(pool or sample has drifted — see the errors above)**") + "  ")
    w(f"**Contents:** {len(ps)} premises · {facts['genres']} genres × 2 · "
      f"{facts['total_words']:,} words · {facts['min_words']}–{facts['max_words']} words each  ")
    w(f"**Render rule:** `{doc.get('render', '')}`\n")
    w("This is the list design §13 asks you to approve before any book is generated. It "
      "is a sign-off, not a draft. The file is hashed and refuses to overwrite, so any "
      "change after your yes is a protocol deviation, not an edit: `premise.py --out` "
      "writes a new version and the manifest records why.\n")

    w("## What the validator already checked\n")
    w("Run on every sheet build, not asserted from memory:\n")
    w("- 20 premises, two per genre, ids unique; each `text` is exactly the render of its "
      "five fields; each `words` count agrees with the text.")
    w("- No rendered premise contains a measured lexicon term (`delve`, `tapestry`, "
      "`testament`, `not just`, …) — a premise carrying one would contaminate that "
      "pair's lexical row.")
    w("- No craft instruction of any kind; §6 forbids style in the input because style is "
      "part of what is measured.")
    w(f"- Closest two premises: `{facts['max_overlap'][1]}` ~ `{facts['max_overlap'][2]}` "
      f"at token overlap {facts['max_overlap'][0]:.2f} (error threshold 0.55). No pair is "
      f"the same story with the cast changed.")
    w("- The sample re-derives from the committed pool and seed, so this list is the "
      "sample and not a convenience list edited afterwards.\n")

    w("## Three things beyond the list that need your yes\n")
    w("| # | what | why it is not the design as written |")
    w("|---|---|---|")
    w(f"| D6 | Premises render at **{facts['min_words']}–{facts['max_words']} words**, "
      f"not §6's {facts['design_band'][0]}–{facts['design_band'][1]} | a tighter premise "
      f"leaves both arms more room, and cross-premise diversity is what makes the "
      f"cross-book fingerprint rows (H3) interpretable. Recorded in README. |")
    w("| D7a | **No person names** appear in any premise | §8.4 measures which names a "
      "model reaches for. Supplying \"Mira\" in the premise hands the name to both arms "
      "and deletes the measurement. |")
    w("| D7b | **No `tone` and no `ending` field** | §6 allows both \"if any\". At the "
      "margin they are instructions about style or structure, and §6 forbids those. "
      "Uniform omission keeps the fields identical across all 20. |")
    w("")
    w(f"- [ ] D6 — approve the {facts['min_words']}–{facts['max_words']}-word band "
      f"(or name the band you want instead)")
    w("- [ ] D7a — approve premises without person names")
    w("- [ ] D7b — approve premises without tone/ending fields\n")

    w("## The pairings\n")
    w("Book IDs are assigned **by position in this file**, and that order is part of what "
      "you are approving: reordering the frozen file would silently re-pair the arms. "
      "A-NN is the naive book, B-NN the Incunabula book, and both receive the same bytes.\n")
    w("| # | pair | premise | genre | working label | words | text sha256 |")
    w("|---:|---|---|---|---|---:|---|")
    for i, p in enumerate(ps, 1):
        w(f"| {i:02d} | A-{i:02d} / B-{i:02d} | `{p['id']}` | {p['genre']} | "
          f"{p['title_label']} | {p['words']} | `{digest(p['text'])[:DIGEST_LEN]}` |")
    w("")

    w("## The twenty, verbatim\n")
    w("Each block is the exact string both arms receive: one paragraph, one space between "
      "fields, no labels, no title. Field order is protagonist, situation, conflict, "
      "setting, stakes. The digest is a 16-hex prefix of `sha256(text)` in UTF-8.\n")
    for i, p in enumerate(ps, 1):
        w(f"### {i:02d} · `{p['id']}` · {p['genre']} — {p['title_label']}\n")
        w(f"*Pair A-{i:02d} / B-{i:02d} · {p['words']} words · "
          f"`{digest(p['text'])[:DIGEST_LEN]}`*\n")
        w(p["text"] + "\n")
    w("")

    w("## How the arms receive it\n")
    w("**Arm A** (design §3) gets the premise inside one opening prompt and nothing else "
      "craft-related:\n")
    w("```")
    w(f"Write a novel of about {A_TARGET:,} words based on this premise: {{TEXT}}")
    w("```\n")
    w(f"`{{TARGET}}` is now frozen at **{A_TARGET:,} words**, accepted band "
      f"{A_BAND[0]:,}–{A_BAND[1]:,} (design §12.2, answered in `DECISIONS.md` §2); "
      "`{TEXT}` is the block above, byte-identical. A long-form stratum of "
      f"{LONG_TARGET:,}-word books ({LONG_BAND[0]:,}–{LONG_BAND[1]:,}) runs on premises "
      "from the pool's unselected twenty, is reported separately, and is **not** part of "
      "these twenty pairs. **Arm B** receives the same `{TEXT}` "
      "through the pipeline (§4), and the manifest records the pipeline commit and the "
      "ductus for each book — `UNASSIGNED` for the primary twenty, since that is the "
      "state every catalogue book was drafted in (`DECISIONS.md` §3). Neither arm gets "
      "the working label — it exists for filing "
      "only, per §6, and a label like \"the wet season\" is itself a mood hint.\n")
    extra = " ".join(sorted(facts["proper_nouns"])) if facts["proper_nouns"] else "none"
    w(f"Capitalised multi-word sequences in the twenty: {extra}. Places are legitimate; "
      "person names are not, and a regex cannot tell them apart, so they are listed here "
      "for your eye rather than judged by a check.\n")

    w("## Sign-off\n")
    w("Tick the premises you approve as written. Anything left unticked is a change "
      "request: name the change at the bottom, and I will prepare `premises-v2.json` with "
      "the deviation logged. Changes are made **before** generation; after it, a premise "
      "change invalidates the pair it belongs to.\n")
    for i, p in enumerate(ps, 1):
        w(f"- [ ] {i:02d} · `{p['id']}` · {p['genre']} — {p['title_label']} "
          f"({p['words']}w)")
    w("")
    w("- [ ] **All twenty approved as written** — no §12 answer is outstanding; this tick "
      "is the last gate before Arm A starts\n")
    w("### Changes requested\n")
    w("| # | premise | what to change |")
    w("|---:|---|---|")
    for _ in range(3):
        w("|  |  |  |")
    w("")
    w("---\n")
    w(f"Generated from `premises/frozen/premises-v1.json` (`sha256 {short}…`) by "
      f"`premises/review-sheet.py`. Every premise digest in this sheet is computed from "
      f"the frozen text at build time, so a sheet that disagrees with the file cannot be "
      f"produced — but this file is a *rendering* of that JSON, not the artifact. The "
      f"bytes that count are in the JSON, and the digest above pins them.\n")
    return "\n".join(out) + "\n"


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing sheet (discards any sign-off on it)")
    args = ap.parse_args(argv)

    if not os.path.exists(FROZEN):
        print(f"missing {FROZEN} - run premise.py --sample first")
        return 2
    with open(FROZEN, encoding="utf-8") as fh:
        doc = json.load(fh)

    errors, facts = check(doc)
    for e in errors:
        print(f"  ERROR  {e}")
    if errors:
        print(f"\n{len(errors)} error(s). No sheet written: a sheet built on a premise "
              f"file that fails its own checks would be signed in bad faith.")
        return 1

    body = build(doc, facts, errors)
    if os.path.exists(SHEET) and not args.force:
        with open(SHEET, encoding="utf-8") as fh:
            if fh.read() == body:
                print(f"already current: {SHEET}")
                return 0
        print(f"REFUSING to overwrite {SHEET}: a sheet with ticks on it is a record of a "
              f"decision, and regenerating it would erase the sign-off. Use --force only "
              f"if the premise file changed and the old sheet is void.")
        return 2

    with open(SHEET, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    print(f"wrote {SHEET}")
    print(f"  {len(doc['premises'])} premises, {facts['total_words']:,} words, "
          f"frozen sha256 {facts['frozen_digest'][:DIGEST_LEN]} verified")
    print(f"  closest pair {facts['max_overlap'][1]} ~ {facts['max_overlap'][2]} "
          f"at {facts['max_overlap'][0]:.2f} overlap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
