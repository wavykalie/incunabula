#!/usr/bin/env python3
"""premise.py - render, validate, sample and freeze the study's premises.

Design §6. The pool is larger than the sample (4 candidates per genre for a sample of
2), so a dropped premise has a reported replacement and the sample is not a convenience
list. What gets frozen is the RENDERED TEXT - the exact bytes both arms receive - not
the fields, because a field can be re-rendered differently later and the study's central
claim is that A-03 and B-03 got the same input.

Two choices made here, both recorded because they are deviations from a literal reading
of §6 and both are cheap to reverse before generation:

  * No person names in a premise. §6 asks for "protagonist (age band, role, one defining
    trait)", not a name, and §8.4 measures which names a model reaches for. A premise
    that supplies "Mira" hands the name to both arms and quietly removes the measurement.
  * No `tone` / `ending` fields. §6 allows them ("if any"). At the margin both are
    instructions about style or structure, and §6 itself forbids style instructions. A
    uniform pool with neither is cleaner than a pool where some premises carry a tone and
    others do not.

usage:
    python premise.py --check                 validate the pool
    python premise.py --sample --seed 20261030  freeze 20 (2 per genre)
    python premise.py --sample-long --out frozen/premises-v2.json
                                              freeze 3 for the 200k stratum
    python premise.py --verify                re-hash the frozen file
    python premise.py --render lit-01         print one premise's exact text
"""

import argparse
import datetime
import hashlib
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(HERE, "candidates.json")
FROZEN_DIR = os.path.join(HERE, "frozen")
FIELD_ORDER = ("protagonist", "situation", "conflict", "setting", "stakes")
PER_GENRE = 2

# The long-form stratum (DECISIONS.md §2): 3 pairs of 200,000-word books, on premises the
# primary twenty did NOT take. Separate premises rather than longer books, so no premise is
# measured at two lengths and the frozen twenty stay untouched.
LONG_COUNT = 3
LONG_TARGET = 200000
V1 = os.path.join(FROZEN_DIR, "premises-v1.json")
# §6 says "roughly 100-200 words". The hard bounds below are what the code enforces; the
# §6 band is reported as a warning. This pool renders at 60-120 words, which is a
# recorded deviation (README, "Deviations from design v1"): a tighter premise leaves the
# arms less room, and cross-premise diversity is what makes the fingerprint rows (H3)
# interpretable. Pending Kalie's yes at freeze - §13's step, not a code decision.
WORDS_HARD = (60, 200)
WORDS_DESIGN = (100, 200)

# Ten genres, two each (design §6). Two per genre is a blocking variable, not a sample
# from which any genre-level claim can be made; see REDTEAM.md M6.
GENRES = (
    "literary", "contemporary romance", "mystery", "thriller", "science fiction",
    "fantasy", "horror", "historical fiction", "adventure", "comedy",
)

# Words the study measures. A premise containing one of these hands that word to both
# arms and contaminates its own lexical row for that pair.
STYLE_LEXICON = (
    "delve", "tapestry", "intricate", "resonate", "testament", "navigate", "navigating",
    "landscape", "vibrant", "profound", "in the heart of", "a world where", "not just",
    "not only", "myriad", "palpable", "seamless", "leverage",
)

# Craft direction of any kind. §6 forbids style instructions. Only phrases that cannot be
# ordinary content are errors; single words that are polysemous ("voice", "sentence",
# "present tense") are warnings, because "the voice on the tape" is not a style note and a
# validator that fails it teaches the author to write around the checker.
INSTRUCTION_ERRORS = (
    "in the style of", "point of view", "should be written", "must be written",
    "write in", "avoids clich", "avoid clich", "first person", "third person",
    "tone:", "mood:", "lyrical", "sparse prose", "vivid prose",
)
INSTRUCTION_WARNINGS = (
    "voice", "sentence", "paragraph", "chapter", "imagery", "present tense",
    "past tense", "rhythm", "metaphor",
)


def load(path=POOL):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def render(p):
    """The exact text both arms receive. One space, fixed order, no labels."""
    return " ".join(p[f].strip() for f in FIELD_ORDER)


def words(text):
    return len(text.split())


def tokens(text):
    return {w for w in re.findall(r"[a-z]{4,}", text.lower())}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def validate(pool):
    """Return (errors, warnings). Errors block a freeze; warnings need a human eye."""
    errors, warnings, band = [], [], []
    if not isinstance(pool, list):
        return ["candidates.json must be a list of premise objects"], []
    seen_ids = set()
    by_genre, texts = {}, []
    for i, p in enumerate(pool):
        where = p.get("id") or f"#{i}"
        if not isinstance(p, dict):
            errors.append(f"{where}: not an object")
            continue
        for key in ("id", "genre", "title_label") + FIELD_ORDER:
            if not p.get(key):
                errors.append(f"{where}: missing field {key!r}")
        if errors and any(e.startswith(f"{where}: missing") for e in errors):
            continue
        if p["id"] in seen_ids:
            errors.append(f"{where}: duplicate id")
        seen_ids.add(p["id"])
        if p["genre"] not in GENRES:
            errors.append(f"{where}: genre {p['genre']!r} is not one of the ten")
        by_genre.setdefault(p["genre"], []).append(p)

        named = re.search(r"\bname\b|\bnamed\b|\bcalled\b", p["protagonist"], re.I)
        if named:
            warnings.append(f"{where}: protagonist field may be naming someone "
                            f"({named.group(0)!r}); premises carry no person names")

        for f in FIELD_ORDER:
            s = p[f].strip()
            if not s.endswith((".", "?", "!")):
                errors.append(f"{where}.{f}: does not end a sentence")
            if not s[0].isupper():
                errors.append(f"{where}.{f}: does not begin a sentence")

        text = render(p)
        n = words(text)
        if not (WORDS_HARD[0] <= n <= WORDS_HARD[1]):
            errors.append(f"{where}: {n} words rendered, outside "
                          f"{WORDS_HARD[0]}-{WORDS_HARD[1]}")
        elif not (WORDS_DESIGN[0] <= n <= WORDS_DESIGN[1]):
            band.append(f"{where} ({n}w)")
        low = text.lower()
        for term in STYLE_LEXICON:
            if term in low:
                errors.append(f"{where}: contains measured lexicon term {term!r}")
        for term in INSTRUCTION_ERRORS:
            if term in low:
                errors.append(f"{where}: contains craft instruction {term!r}")
        for term in INSTRUCTION_WARNINGS:
            if re.search(r"\b" + re.escape(term) + r"\b", low):
                warnings.append(f"{where}: contains {term!r} - content or instruction? "
                                f"read it")
        texts.append((p["id"], tokens(text), n))

    for g in GENRES:
        got = len(by_genre.get(g, []))
        if got < PER_GENRE:
            errors.append(f"genre {g!r}: {got} candidate(s), need at least {PER_GENRE}")
        if got > 4:
            warnings.append(f"genre {g!r}: {got} candidates; the pool is meant to be "
                            f"about 4 per genre so replacements are not a convenience")

    if band:
        warnings.append(f"{len(band)} premise(s) outside design §6's "
                        f"{WORDS_DESIGN[0]}-{WORDS_DESIGN[1]}-word band, a recorded "
                        f"deviation (README): " + ", ".join(band))

    # Near-duplicates: two premises that are the same story with the cast changed would
    # make one pair measure premise similarity instead of the pipeline.
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i][1], texts[j][1]
            sim = jaccard(a, b)
            if sim > 0.55:
                errors.append(f"{texts[i][0]} ~ {texts[j][0]}: token overlap {sim:.2f}")
            elif sim > 0.35:
                warnings.append(f"{texts[i][0]} ~ {texts[j][0]}: token overlap {sim:.2f}")

    return errors, warnings


def proper_nouns(pool):
    """Capitalised two-word sequences, reported for human review.

    Places are legitimate; person names are not. No regex separates the two, so this
    prints the list and a person rules on it. Design §6's rule, B4's lesson: a check that
    guesses here would rather miss than accuse.
    """
    out = {}
    for p in pool:
        for m in re.findall(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b", render(p)):
            out.setdefault(m, []).append(p["id"])
    return out


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sample(pool, seed, per_genre=PER_GENRE, exclude=()):
    """Stratified sample. The generator is seeded per genre, so adding a genre later
    does not reshuffle the genres already sampled."""
    chosen = []
    for g in GENRES:
        ids = sorted(p["id"] for p in pool if p["genre"] == g and p["id"] not in exclude)
        rng = random.Random(f"{seed}:{g}")
        take = ids if len(ids) <= per_genre else rng.sample(ids, per_genre)
        chosen.extend((g, i) for i in take)
    by_id = {p["id"]: p for p in pool}
    out = []
    for g, pid in sorted(chosen):
        p = by_id[pid]
        text = render(p)
        out.append({
            "id": p["id"], "genre": g, "title_label": p["title_label"],
            **{f: p[f] for f in FIELD_ORDER},
            "text": text, "words": words(text),
        })
    return out


def sample_long(pool, seed, count=LONG_COUNT, exclude=()):
    """One premise per genre, from what the primary freeze did not take.

    Genres are shuffled under the seed and the first `count` are used; within a genre the
    premise is drawn under a second seed derived from the genre. Nothing is hand-picked, so
    the long set is reproducible and a reader can rerun it and get the same three.
    """
    by_genre = {}
    for p in pool:
        if p["id"] in exclude:
            continue
        by_genre.setdefault(p["genre"], []).append(p["id"])
    genres = [g for g in GENRES if by_genre.get(g)]
    random.Random(f"{seed}:long").shuffle(genres)
    picked = sorted(genres[:count])
    by_id = {p["id"]: p for p in pool}
    out = []
    for g in picked:
        ids = sorted(by_genre[g])
        pid = random.Random(f"{seed}:long:{g}").choice(ids)
        p = by_id[pid]
        text = render(p)
        out.append({
            "id": p["id"], "genre": g, "title_label": p["title_label"],
            **{f: p[f] for f in FIELD_ORDER},
            "text": text, "words": words(text),
        })
    return out


def freeze(pool, seed, out_path, force=False, long_form=False, count=LONG_COUNT):
    # Warnings were already printed by main(); printing them again here made --sample
    # read as two runs.
    errors, _ = validate(pool)
    if errors:
        for e in errors:
            print(f"  ERROR  {e}")
        print(f"\n{len(errors)} error(s). Nothing frozen.")
        return 2

    v1_sha = None
    if long_form:
        if verify(V1) != 0:
            print(f"\nthe long stratum is drawn from what {os.path.basename(V1)} did not take, "
                  f"and that file does not verify. Freeze the primary twenty first "
                  f"(DECISIONS.md §2). Nothing frozen.")
            return 2
        with open(V1, encoding="utf-8") as fh:
            taken = {p["id"] for p in json.load(fh)["premises"]}
        v1_sha = sha256_file(V1)
        chosen = sample_long(pool, seed, count=count, exclude=taken)
        if len(chosen) < count:
            print(f"only {len(chosen)} genre(s) left unclaimed in the pool; asked for {count}")
            return 2
    else:
        chosen = sample(pool, seed)
    doc = {
        "study": "50-novel prose-tell study",
        "design": "v1, amended per study/REDTEAM.md (C-dist for thresholds)",
        "seed": seed,
        "per_genre": PER_GENRE,
        "frozen_at": datetime.date.today().isoformat(),
        "pool_file": os.path.relpath(POOL, HERE).replace("\\", "/"),
        "pool_sha256": sha256_file(POOL),
        "render": " | ".join(FIELD_ORDER) + " joined by one space; no labels",
        "premises": chosen,
    }
    if long_form:
        doc.update({
            "stratum": "long-form (exploratory, never pooled with the primary twenty)",
            "target_words": LONG_TARGET,
            "per_genre": 1,
            "excluded_by": os.path.basename(V1),
            "excluded_by_sha256": v1_sha,
            "count": count,
        })
    body = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"

    if os.path.exists(out_path) and not force:
        with open(out_path, encoding="utf-8") as fh:
            if fh.read() == body:
                print(f"already frozen and unchanged: {out_path}")
                return 0
        print(f"REFUSING to overwrite {out_path}: a frozen premise file is immutable.\n"
              f"  A change is a protocol deviation: write a new version with --out,\n"
              f"  and record the deviation in the manifest.")
        return 2

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    digest = sha256_file(out_path)
    with open(out_path + ".sha256", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"{digest}  {os.path.basename(out_path)}\n")
    print(f"froze {len(chosen)} premises -> {out_path}")
    print(f"  sha256 {digest}")
    print(f"  {len(chosen)} x {sum(p['words'] for p in chosen)} words total")
    return 0


def verify(path):
    sidecar = path + ".sha256"
    if not os.path.exists(path) or not os.path.exists(sidecar):
        print(f"missing {path} or its .sha256. Nothing verified.")
        return 2
    with open(sidecar, encoding="utf-8") as fh:
        want = fh.read().split()[0]
    got = sha256_file(path)
    if want != got:
        print(f"MISMATCH  {path}\n  recorded {want}\n  actual   {got}")
        return 1
    print(f"ok  {path}  {got}")
    return 0


def main(argv=None):
    try:                      # Windows consoles default to cp1252 and die on § and —
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="validate the pool")
    ap.add_argument("--sample", action="store_true", help="freeze a stratified sample")
    ap.add_argument("--sample-long", action="store_true",
                    help="freeze the long-form stratum from the unclaimed premises")
    ap.add_argument("--count", type=int, default=LONG_COUNT)
    ap.add_argument("--seed", type=int, default=20261030)
    ap.add_argument("--out", default=os.path.join(FROZEN_DIR, "premises-v1.json"))
    ap.add_argument("--force", action="store_true", help="overwrite (a protocol deviation)")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--render", metavar="ID")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    if args.verify:
        return verify(args.out)

    pool = load()

    if args.render:
        p = next((x for x in pool if x["id"] == args.render), None)
        if not p:
            print(f"no premise {args.render!r}")
            return 2
        print(render(p))
        return 0

    if args.list:
        for g in GENRES:
            for p in pool:
                if p["genre"] == g:
                    print(f"{p['id']:<10} {words(render(p)):>4}w  {p['title_label']}")
        return 0

    errors, warnings = validate(pool)
    print(f"pool: {len(pool)} candidates, {len(GENRES)} genres")
    for w in warnings:
        print(f"  warn   {w}")
    if errors:
        for e in errors:
            print(f"  ERROR  {e}")
        print(f"\n{len(errors)} error(s).")
        return 1
    print(f"  ok     0 errors, {len(warnings)} warning(s)")

    pn = proper_nouns(pool)
    if pn:
        print("\nproper nouns found (places are fine, person names are not):")
        for name, ids in sorted(pn.items()):
            print(f"  {name:<24} {', '.join(ids)}")

    if args.sample and args.sample_long:
        print("--sample and --sample-long write different files; run one at a time.")
        return 2
    if args.sample:
        print()
        return freeze(pool, args.seed, args.out, force=args.force)
    if args.sample_long:
        print()
        return freeze(pool, args.seed, args.out, force=args.force, long_form=True,
                      count=args.count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
